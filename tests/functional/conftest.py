import pytest
import asyncio
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts


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
        "urn:nhsd:apim:app:level3:personal-demographics-service"
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


@ pytest.fixture(scope="function")
def setup_session(request, get_token):
    """This fixture is called at a function level.
    The default app created here should be modified by your tests.
    """
    product = asyncio.run(_product_with_full_access())
    print("\nCreating Default App..")
    # Create a new app
    app = ApigeeApiDeveloperApps()

    asyncio.run(app.create_new_app(
        callback_url="https://example.org/callback"
    ))
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
