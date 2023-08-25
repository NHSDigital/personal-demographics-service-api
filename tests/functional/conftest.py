from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest
import asyncio

from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from .config_files import config
import random
import json
from typing import Union


from pytest_nhsd_apim.identity_service import (
    ClientCredentialsConfig,
    ClientCredentialsAuthenticator,
)


async def _set_default_rate_limit(product: ApigeeApiProducts):
    """Updates an Apigee Product with a default rate limit and quota.

    Args:
        product (ApigeeApiProducts): Apigee product.
    """
    await product.update_ratelimits(quota=60000,
                                    quota_interval="1",
                                    quota_time_unit="minute",
                                    rate_limit="1000ps")


async def _product_with_full_access():
    """Creates an apigee product with access to all proxy paths and scopes.

    Returns:
        product (ApigeeApiProducts): Apigee product.
    """
    product = ApigeeApiProducts()
    await product.create_new_product()
    await _set_default_rate_limit(product)
    await product.update_scopes([
        "personal-demographics-service:USER-RESTRICTED",
        "urn:nhsd:apim:app:level3:personal-demographics-service",
        "urn:nhsd:apim:user-nhs-id:aal3:personal-demographics-service"
    ])
    # Allows access to all proxy paths - so we don't have to specify the pr proxy explicitly
    await product.update_paths(paths=["/", "/*"])
    return product


@pytest.fixture(scope="function")
async def setup_session(request, _test_app_credentials, _jwt_keys, apigee_environment):
    """This fixture is called at a function level.
    The default app created here should be modified by your tests.
    """

    product = await _product_with_full_access()
    print("\nCreating Default App..")
    # Create a new app
    app = ApigeeApiDeveloperApps()
    await app.create_new_app(
        callback_url="https://example.org/callback"
    )
    # Assign the new product to the app
    await app.add_api_product([product.name])

    # Set up app config
    config = ClientCredentialsConfig(
        environment=apigee_environment,
        identity_service_base_url=f"https://{apigee_environment}.api.service.nhs.uk/oauth2-mock",
        client_id=_test_app_credentials["consumerKey"],
        jwt_private_key=_jwt_keys["private_key_pem"],
        jwt_kid="test-1",
    )

    # Pass the config to the Authenticator
    authenticator = ClientCredentialsAuthenticator(config=config)

    # Get token
    token_response = authenticator.get_token()
    assert "access_token" in token_response
    token = token_response["access_token"]

    yield product, app, token

    # Teardown
    print("\nDestroying Default App..")
    await app.destroy_app()
    await product.destroy_product()


@pytest.fixture()
def setup_patch(setup_session):
    """Fixture to make an async request using sync-wrap.
    GET /Patient -> PATCH /Patient
    """

    [product, app, token] = setup_session

    pds = GenericPdsRequestor(
        pds_base_path=config.PDS_BASE_PATH,
        base_url=config.BASE_URL,
        token=token,
    )

    response = pds.get_patient_response(patient_id=config.TEST_PATIENT_ID)

    pds.headers = {
        "If-Match": response.headers["Etag"],
        "Content-Type": "application/json-patch+json"
    }

    return {
        "pds": pds,
        "product": product,
        "app": app,
        "token": token,
    }


@pytest.fixture()
def sync_wrap_low_wait_update(setup_patch: GenericPdsRequestor, create_random_date) -> PdsRecord:
    pds = setup_patch["pds"]
    pds.headers = {
        "X-Sync-Wait": "0.25"
    }
    resp = pds.update_patient_response(
        patient_id=config.TEST_PATIENT_ID,
        payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
    )
    return resp


def set_quota_and_rate_limit(
    apigeeObj: Union[ApigeeApiProducts, ApigeeApiDeveloperApps],
    rate_limit: str = "1000ps",
    quota: int = 60000,
    quota_interval: str = "1",
    quota_time_unit: str = "minute",
    quota_enabled: bool = True,
    rate_enabled: bool = True,
    proxy: str = ""
) -> None:
    """Sets the quota and rate limit on an apigee product or app.

    Args:
        obj (Union[ApigeeApiProducts,ApigeeApiDeveloperApps]): Apigee product or Apigee app
        rate_limit (str): The rate limit to be set.
        quota (int): The amount of requests per quota interval.
        quoata_interval (str): The length of a quota interval in quota units.
        quota_time_unit (str): The quota unit length e.g. minute.
        quota_enabled (bool): Enable or disable proxy level quota.
        rate_enabled (bool): Enable or disable proxy level spike arrest.
        proxy (str): The proxy to apply rate limiting to.
    """
    value = json.dumps({
        proxy: {
            "quota": {
                "limit": quota,
                "interval": quota_interval,
                "timeunit": quota_time_unit,
                "enabled": quota_enabled
            },
            "spikeArrest": {
                "ratelimit": rate_limit,
                "enabled": rate_enabled
            }
        }
    })

    rate_limiting = {'ratelimiting': value}

    if (isinstance(apigeeObj, ApigeeApiProducts)):
        asyncio.run(apigeeObj.update_attributes(rate_limiting))
    elif isinstance(apigeeObj, ApigeeApiDeveloperApps):
        asyncio.run(apigeeObj.set_custom_attributes(rate_limiting))
    else:
        raise TypeError("Please provide an Apigee product or Apigee app")


@pytest.fixture()
def create_random_date():
    day = str(random.randrange(1, 28)).zfill(2)
    month = str(random.randrange(1, 12)).zfill(2)
    year = random.randrange(1940, 2020)
    new_date = f"{year}-{month}-{day}"
    return new_date


@pytest.fixture()
def app():
    """
    Import the test utils module to be able to:
        - Create apigee test application
            - Update custom attributes
            - Update custom ratelimits
            - Update products to the test application
    """
    return ApigeeApiDeveloperApps()


@pytest.fixture()
def product():
    """
    Import the test utils module to be able to:
        - Create apigee test product
            - Update custom scopes
            - Update environments
            - Update product paths
            - Update custom attributes
            - Update proxies to the product
            - Update custom ratelimits
    """
    return ApigeeApiProducts()


@pytest.fixture()
async def test_app_and_product(app, product):
    """Create a test app and product which can be modified in the test"""
    await product.create_new_product()

    await app.create_new_app()

    await product.update_scopes(
        [
            "urn:nhsd:apim:app:level3:personal-demographics-service",
            "urn:nhsd:apim:user-nhs-id:aal3:personal-demographics-service",
            "urn:nhsd:apim:user-nhs-login:P9:personal-demographics-service",
            "urn:nhsd:apim:user-nhs-login:P5:personal-demographics-service",
            "urn:nhsd:apim:user-nhs-login:P0:personal-demographics-service",
        ]
    )
    await app.add_api_product([product.name])
    await app.set_custom_attributes(
        {
            "jwks-resource-url": config.JWKS_RESOURCE_URL
        }
    )

    yield product, app

    await app.destroy_app()
    await product.destroy_product()
