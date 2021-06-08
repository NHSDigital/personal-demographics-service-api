from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest
import asyncio
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from .config_files import config
import random


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
        "urn:nhsd:apim:app:level3:",
        "urn:nhsd:apim:user-nhs-id:aal3:personal-demographics-service"
    ])
    # Allows access to all proxy paths - so we don't have to specify the pr proxy explicitly
    await product.update_paths(paths=["/", "/*"])
    return product


@pytest.fixture()
async def get_token(request):
    """Get an access or refresh token
    some examples:
        1. access_token via simulated oauth (default)
            get_token()
        2. get access token with a specified timeout value (default is 5 seconds)
            get_token(timeout=500000)  # 5 minuets
        3. refresh_token via simulated oauth
            get_token(grant_type="refresh_token", refresh_token=<refresh_token>)
        4. access_token with JWT
            get_token(grant_type='client_credentials', _jwt=jwt)
        5. access_token using a specific app
            get_token(app=<app>)

    Args:
        request(requests): HTTP requests object.

    Returns:
        _token(dict): Identity Service HTTP Response body
        e.g. { "accessToken" : "eJkajgolJ...", "refreshToken" : "eJjagk.."}.
    """
    async def _token(
        grant_type: str = "authorization_code",
        test_app: ApigeeApiDeveloperApps = None,
        **kwargs
    ):
        if test_app:
            # Use provided test app
            oauth = OauthHelper(test_app.client_id, test_app.client_secret, test_app.callback_url)
            resp = await oauth.get_token_response(grant_type=grant_type, **kwargs)
        else:
            # Use env vars
            oauth = OauthHelper(
                client_id=config.CLIENT_ID,
                client_secret=config.CLIENT_SECRET,
                redirect_uri="https://nhsd-apim-testing-internal-dev.herokuapp.com/",
            )
            resp = await oauth.get_token_response(grant_type=grant_type, **kwargs)

        if resp['status_code'] != 200:
            message = 'unable to get token'
            raise RuntimeError(f"\n{'*' * len(message)}\n"
                               f"MESSAGE: {message}\n"
                               f"URL: {resp.get('url')}\n"
                               f"STATUS CODE: {resp.get('status_code')}\n"
                               f"RESPONSE: {resp.get('body')}\n"
                               f"HEADERS: {resp.get('headers')}\n"
                               f"{'*' * len(message)}\n")
        return resp['body']

    return _token


@pytest.fixture(scope="function")
async def setup_session(request):
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

    # Set default JWT Testing resource url
    await app.set_custom_attributes(
            {
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                     'identity-service-jwks/main/jwks/internal-dev/'
                                     '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json'
            }
    )

    await product.update_environments([config.ENVIRONMENT])
    oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)
    resp = await oauth.get_token_response(grant_type="authorization_code")
    token = resp["body"]["access_token"]

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

    response = pds.get_patient_response(patient_id='5900038181')

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
        patient_id='5900038181',
        payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
    )
    return resp


def set_quota_and_rate_limit(
    product: ApigeeApiProducts,
    rate_limit: str = "1000ps",
    quota: int = 60000,
    quota_interval: str = "1",
    quota_time_unit: str = "minute"
) -> None:
    """Sets the quota and rate limit on an apigee product.

    Args:
        product (ApigeeApiProducts): Apigee product
        rate_limit (str): The rate limit to be set.
        quota (int): The amount of requests per quota interval.
        quoata_interval (str): The length of a quota interval in quota units.
        quota_time_unit (str): The quota unit length e.g. minute.
    """
    asyncio.run(product.update_ratelimits(quota=quota,
                                          quota_interval=quota_interval,
                                          quota_time_unit=quota_time_unit,
                                          rate_limit=rate_limit))


@pytest.fixture()
def create_random_date():
    day = str(random.randrange(1, 28)).zfill(2)
    month = str(random.randrange(1, 12)).zfill(2)
    year = random.randrange(1940, 2020)
    new_date = f"{year}-{month}-{day}"
    return new_date
