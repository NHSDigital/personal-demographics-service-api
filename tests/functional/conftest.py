import pytest
import asyncio
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from tests.scripts.generic_request import GenericRequest
from tests.scripts.pds_request import GenericPdsRequestor

"""
Used in:
https://github.com/NHSDigital/api-management-service-template/tree/master/tests

Tested for app, product and oauth creation:
https://github.com/NHSDigital/api-management-service-template/blob/master/tests/test_endpoints.py


"""


@pytest.fixture()
def get_token(request):
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
            # Use default test app
            resp = await request.cls.oauth.get_token_response(grant_type=grant_type, **kwargs)

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


async def _set_default_rate_limit(product: ApigeeApiProducts):
    await product.update_ratelimits(quota=60000,
                                    quota_interval="1",
                                    quota_time_unit="minute",
                                    rate_limit="1000ps")


@ pytest.fixture()
async def test_product():
    """Create a test product which can be modified by the test"""
    product = ApigeeApiProducts()
    await product.create_new_product()
    _set_default_rate_limit(product)
    yield product
    await product.destroy_product()


@ pytest.fixture()
def app():
    return ApigeeApiDeveloperApps()


@ pytest.fixture()
async def test_app(app):
    """Create a test app which can be modified in the test"""
    await app.create_new_app()

    yield app
    await app.destroy_app()


async def _product_with_full_access():
    product = ApigeeApiProducts()
    await product.create_new_product()
    await _set_default_rate_limit(product)
    await product.update_scopes([
        "personal-demographics-service:USER-RESTRICTED",
        "urn:nhsd:apim:app:level3:",
        "urn:nhsd:apim:user-nhs-id:aal3:personal-demographics-service"
    ])
    # Causes a break if we specify the proxy
    # await product.update_proxies(["identity-service-internal-dev", "personal-demographics-int-pr-565"])  # form env
    # Allows access to all proxy paths, could be risky?
    await product.update_paths(paths=["/", "/*"])
    return product


@ pytest.fixture(scope="function")
def setup_session(request, get_token):
    """This fixture is automatically called once at the start of pytest execution.
    The default app created here should be modified by your tests.
    If your test requires specific app config then please create your own using
    the fixture test_app.

    Changes:
    This fixture can be used to run automatically at the start of a pytest session
    through scope="session" and autouse=True.
    """
    product = asyncio.run(_product_with_full_access())
    print("\nCreating Default App..")
    # Create a new app
    app = ApigeeApiDeveloperApps()

    asyncio.run(app.create_new_app(callback_url="https://nhsd-apim-testing-internal-dev.herokuapp.com/callback"))
    # Assign the new product to the app
    asyncio.run(app.add_api_product([product.name]))

    # Set default JWT Testing resource url
    asyncio.run(
        app.set_custom_attributes(
            {
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                     'identity-service-jwks/main/jwks/internal-dev/'
                                     '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json'
            }
        )
    )
    oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)
    token = asyncio.run(get_token(test_app=app))
    yield oauth, product, app, token["access_token"]

    # Teardown
    print("\nDestroying Default App..")
    asyncio.run(app.destroy_app())
    asyncio.run(product.destroy_product())
