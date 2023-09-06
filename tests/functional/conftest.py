from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest

from .utils.apigee_api_apps import ApigeeApiDeveloperApps
from .utils.apigee_api_products import ApigeeApiProducts
from .config_files import config
import random
import json
from typing import Union


from pytest_nhsd_apim.identity_service import (
    ClientCredentialsConfig,
    ClientCredentialsAuthenticator,
)

from pytest_nhsd_apim.apigee_apis import (
    ApigeeClient,
    ApiProductsAPI,
    ApigeeNonProdCredentials,
    DeveloperAppsAPI,
)

import logging

LOGGER = logging.getLogger(__name__)
DEVELOPER_EMAIL = "apm-testing-internal-dev@nhs.net"


@pytest.fixture()
def client():
    config = ApigeeNonProdCredentials()
    return ApigeeClient(config=config)


@pytest.fixture()
def api_products(client):
    return ApiProductsAPI(client=client)


@pytest.fixture()
def developer_apps(client):
    return DeveloperAppsAPI(client=client)


@pytest.fixture()
def add_asid_to_testapp(developer_apps, nhsd_apim_test_app):
    app = nhsd_apim_test_app()
    LOGGER.info(f'app:{app}')
    app_name = app["name"]

    # Check if the ASID attribute is already available
    app_attributes = developer_apps.get_app_attributes(email=DEVELOPER_EMAIL, app_name=app_name)
    # LOGGER.info(f'app_attributes: {app_attributes}')
    custom_attributes = app_attributes['attribute']
    # LOGGER.info(f'custom_attributes: {custom_attributes}')
    existing_asid_attribute = None
    for attribute in custom_attributes:
        if attribute['name'] == 'asid':
            existing_asid_attribute = attribute['value']

    if not existing_asid_attribute:
        LOGGER.info(f'ASID attribute not found. Adding {config.ENV["internal_dev_asid"]} to {app_name}')
        # Add ASID to the test app - To be refactored when we move to .feature files TODO
        custom_attributes.append({"name": "asid", "value": config.ENV["internal_dev_asid"]})
        # LOGGER.info(f'custom_attributes: {custom_attributes}')
        data = {"attribute": custom_attributes}
        response = developer_apps.post_app_attributes(email=DEVELOPER_EMAIL, app_name=app_name, body=data)
        LOGGER.info(f'Test app updated with ASID attribute: {response}')


def _set_default_rate_limit(product: ApigeeApiProducts, api_products):
    """Updates an Apigee Product with a default rate limit and quota.

    Args:
        product (ApigeeApiProducts): Apigee product.
    """
    product.update_ratelimits(quota=60000,
                              quota_interval="1",
                              quota_time_unit="minute",
                              rate_limit="1000ps",
                              api_products=api_products)


def _product_with_full_access(api_products):
    """Creates an apigee product with access to all proxy paths and scopes.
    Returns:
        product (ApigeeApiProducts): Apigee product.
    """

    product = ApigeeApiProducts()
    product.create_new_product(api_products)
    _set_default_rate_limit(product, api_products)
    product.update_scopes([
        "personal-demographics-service:USER-RESTRICTED",
        "urn:nhsd:apim:app:level3:personal-demographics-service",
        "urn:nhsd:apim:user-nhs-cis2:aal3:personal-demographics",
        # f"urn:nhsd:apim:user-nhs-cis2:aal3:{config.PROXY_NAME}",
        "urn:nhsd:apim:user-nhs-login:P9:personal-demographics"
    ], api_products)
    # Allows access to all proxy paths - so we don't have to specify the pr proxy explicitly
    product.update_paths(paths=["/", "/*"], api_products=api_products)
    # product.update_proxies(proxies=[config.PROXY_NAME], api_products=api_products)
    LOGGER.info(f'product.get_product_details(): {product.get_product_details(api_products)}')

    return product


@pytest.fixture(scope="function")
def setup_session(request, _jwt_keys, apigee_environment, client, api_products):
    """This fixture is called at a function level.
    The default app created here should be modified by your tests.
    """

    product = _product_with_full_access(api_products)
    product.update_environments([config.ENVIRONMENT], api_products=api_products)

    LOGGER.info(f'product.proxies: {product.proxies}')

    print("\nCreating Default App..")
    # Create a new app
    developer_apps = DeveloperAppsAPI(client=client)

    app = ApigeeApiDeveloperApps()
    create_app_response = app.create_new_app(
        callback_url="https://example.org/callback",
        status="approved",
        jwks_resource_url=config.JWKS_RESOURCE_URL,
        products=[product.name],
        developer_apps=developer_apps
    )

    LOGGER.info(f'create_app_response: {create_app_response}')

    # app.set_custom_attributes({'jwks-resource-url': config.JWKS_RESOURCE_URL}, developer_apps=developer_apps)
    # product.update_environments([config.ENVIRONMENT], api_products=api_products)

    # Assign the new product to the app
    # app.add_api_product([product.name], developer_apps=developer_apps)

    LOGGER.info(f'app.get_app_details(): {app.get_app_details(developer_apps=developer_apps)}')
    # LOGGER.info(f'consumerKey: {_test_app_credentials["consumerKey"]}')
    # LOGGER.info(f'_jwt_keys["private_key_pem"]: {_jwt_keys["private_key_pem"]}')

    # LOGGER.info(f'JWT_PRIVATE_KEY_ABSOLUTE_PATH: {config.JWT_PRIVATE_KEY_ABSOLUTE_PATH}')

    # Set up app config
    client_credentials_config = ClientCredentialsConfig(
        environment=apigee_environment,
        identity_service_base_url=f"https://{apigee_environment}.api.service.nhs.uk/{config.OAUTH_PROXY}",
        # client_id=_test_app_credentials["consumerKey"],
        client_id=app.get_client_id(),
        # jwt_private_key=_jwt_keys["private_key_pem"],
        jwt_private_key=config.SIGNING_KEY,
        jwt_kid="test-1",
    )

    # Pass the config to the Authenticator
    authenticator = ClientCredentialsAuthenticator(config=client_credentials_config)

    # Get token
    token_response = authenticator.get_token()
    assert "access_token" in token_response
    token = token_response["access_token"]

    LOGGER.info(f'token_response: {token_response}')

    # auth["response"] = token_response
    # auth["access_token"] = token_response["access_token"]
    # auth["token_type"] = token_response["token_type"]

    LOGGER.info(f'token: {token}')

    yield product, app, token_response, developer_apps, api_products

    # Teardown
    print("\nDestroying Default App..")

    app.destroy_app(developer_apps)
    product.destroy_product(api_products)


@pytest.fixture()
def setup_patch(setup_session):
    """Fixture to make an async request using sync-wrap.
    GET /Patient -> PATCH /Patient
    """

    [product, app, token_response, developer_apps, api_products] = setup_session

    pds = GenericPdsRequestor(
        pds_base_path=config.PDS_BASE_PATH,
        base_url=config.BASE_URL,
        token=token_response["access_token"],
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
        "token": token_response["access_token"],
        "developer_apps": developer_apps,
        "api_products": api_products
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
    proxy: str = "",
    api_products: ApiProductsAPI = None,
    developer_apps: DeveloperAppsAPI = None
) -> None:
    """Sets the quota and rate limit on an apigee product or app.

    Args:
        obj (Union[ApigeeApiProducts,ApigeeApiDeveloperApps]): Apigee product or Apigee app
        rate_limit (str): The rate limit to be set.
        quota (int): The amount of requests per quota interval.
        quota_interval (str): The length of a quota interval in quota units.
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
        apigeeObj.update_attributes(rate_limiting, api_products)
    elif isinstance(apigeeObj, ApigeeApiDeveloperApps):
        apigeeObj.set_custom_attributes(rate_limiting, developer_apps)
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
