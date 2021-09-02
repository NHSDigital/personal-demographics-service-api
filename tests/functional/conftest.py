from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest
import asyncio
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from .config_files import config
import random
from time import time
import json
from typing import Union

from .config_files.config import BASE_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


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
    # APMSPII-1139 increase token expiry time to provide sufficient time to conduct the tests
    resp = await oauth.get_token_response(grant_type="authorization_code", timeout=20000)
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
async def setup_patch_short_lived_token(setup_session):
    """Fixture to make an async request using sync-wrap, with a short-lived -- 1 second -- access token.
    GET /Patient -> PATCH /Patient
    """

    product, app, _ = setup_session

    oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)
    resp = await oauth.get_token_response(grant_type="authorization_code", timeout=config.AUTH_TOKEN_EXPIRY_MS)
    token = resp["body"]["access_token"]

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

    return pds


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
            "jwks-resource-url": "https://raw.githubusercontent.com/NHSDigital/"
                                 "identity-service-jwks/main/jwks/internal-dev/"
                                 "9baed6f4-1361-4a8e-8531-1f8426e3aba8.json"
        }
    )

    yield product, app

    await app.destroy_app()
    await product.destroy_product()


@pytest.fixture()
def nhs_login_token_exchange(test_app_and_product):
    test_product, test_app = test_app_and_product

    async def get_token_nhs_login_token_exchange(scope: str = "P9"):
        """Call identity server to get an access token"""
        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
        )

        id_token_claims = {
            "aud": "tf_-APIM-1",
            "id_status": "verified",
            "nhs_number": "9693633172",
            "token_use": "id",
            "auth_time": 1616600683,
            "iss": BASE_URL,
            "vot": "P9.Cp.Cd",
            "exp": int(time()) + 600,
            "iat": int(time()) - 10,
            "vtm": "https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk",
            "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
            "identity_proofing_level": scope,
        }
        id_token_headers = {
            "sub": "49f470a1-cc52-49b7-beba-0f9cec937c46",
            "aud": "APIM-1",
            "kid": "nhs-login",
            "iss": BASE_URL,
            "typ": "JWT",
            "exp": 1616604574,
            "iat": 1616600974,
            "alg": "RS512",
            "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
        }
        with open(config.ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH, "r") as f:
            contents = f.read()

        client_assertion_jwt = oauth.create_jwt(kid="test-1")
        id_token_jwt = oauth.create_id_token_jwt(
            algorithm="RS512",
            claims=id_token_claims,
            headers=id_token_headers,
            signing_key=contents,
        )

        # When
        token_resp = await oauth.get_token_response(
            grant_type="token_exchange",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "subject_token": id_token_jwt,
                "client_assertion": client_assertion_jwt,
            },
        )
        assert token_resp["status_code"] == 200
        return token_resp["body"]['access_token']
    return get_token_nhs_login_token_exchange
