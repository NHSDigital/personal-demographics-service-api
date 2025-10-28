from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest
import urllib
import uuid
from .utils.apigee_api_apps import ApigeeApiDeveloperApps
from .utils.apigee_api_products import ApigeeApiProducts
from .configuration import config
from .configuration.config import BASE_URL, PDS_BASE_PATH
import random
from requests import Response
import requests
import json
import jwt
from typing import Union
from tests.functional.data.searches import Search
from tests.functional.data.updates import Update
from tests.functional.data import searches
from tests.functional.data import updates
from tests.functional.data import patients
from tests.functional.data.patients import Patient
import time
import os

from pytest_nhsd_apim.identity_service import (
    ClientCredentialsConfig,
    ClientCredentialsAuthenticator,
    AuthorizationCodeAuthenticator,
    AuthorizationCodeConfig,
)

from pytest_nhsd_apim.apigee_apis import (
    ApiProductsAPI,
    DeveloperAppsAPI,
)

FILE_DIR = os.path.dirname(__file__)
RESPONSES_DIR = os.path.join(FILE_DIR, 'data', 'responses')
CALLBACK_URL = "https://example.org/callback"

@pytest.fixture()
def developer_email() -> str:
    return "apm-testing-internal-dev@nhs.net"


@pytest.fixture()
def pds_url() -> str:
    return f"{BASE_URL}/{PDS_BASE_PATH}"


@pytest.fixture()
def add_asid_to_testapp(developer_apps_api,
                        nhsd_apim_test_app,
                        developer_email):
    app = nhsd_apim_test_app()
    app_name = app["name"]

    app_attributes = developer_apps_api.get_app_attributes(email=developer_email, app_name=app_name)
    custom_attributes = app_attributes['attribute']
    existing_asid_attribute = None
    for attribute in custom_attributes:
        if attribute['name'] == 'asid':
            existing_asid_attribute = attribute['value']

    if not existing_asid_attribute and config.ENV.contains("internal_dev_asid"):
        custom_attributes.append({"name": "asid", "value": config.ENV["internal_dev_asid"]})
        data = {"attribute": custom_attributes}
        developer_apps_api.post_app_attributes(email=developer_email, app_name=app_name, body=data)


@pytest.fixture(scope='function')
def headers_with_authorization(_nhsd_apim_auth_token_data: dict,
                               add_asid_to_testapp: None) -> dict:
    access_token = _nhsd_apim_auth_token_data.get("access_token", "")

    headers = {
        "X-Request-ID": str(uuid.uuid1()),
        "X-Correlation-ID": str(uuid.uuid1()),
        "Authorization": f'Bearer {access_token}'
    }
    return headers


@pytest.fixture()
def search() -> Search:
    return searches.DEFAULT


@pytest.fixture()
def update() -> Update:
    return updates.DEFAULT


@pytest.fixture()
def patient() -> Patient:
    return patients.DEFAULT


@pytest.fixture()
def nhs_number(patient: Patient) -> str:
    return patient.nhs_number


@pytest.fixture()
def query_params(search: Search) -> str:
    return urllib.parse.urlencode(search.query)


@pytest.fixture()
def response_body(response: Response) -> dict:
    response_body = json.loads(response.text)
    if "timestamp" in response_body:
        response_body.pop("timestamp")
    return response_body


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
        "urn:nhsd:apim:user-nhs-login:P9:personal-demographics"
    ], api_products)
    # Allows access to all proxy paths - so we don't have to specify the pr proxy explicitly
    product.update_paths(paths=["/", "/*"], api_products=api_products)

    return product


@pytest.fixture(scope="function")
def setup_session(request, _jwt_keys, apigee_environment, developer_apps_api, products_api):
    """This fixture is called at a function level.
    The default app created here should be modified by your tests.
    """

    product = _product_with_full_access(products_api)
    product.update_environments([config.ENVIRONMENT], api_products=products_api)

    app = ApigeeApiDeveloperApps()
    app.create_new_app(
        callback_url=CALLBACK_URL,
        status="approved",
        jwks_resource_url=config.JWKS_RESOURCE_URL,
        products=[product.name],
        developer_apps=developer_apps_api
    )

    client_credentials_config = ClientCredentialsConfig(
        environment=apigee_environment,
        identity_service_base_url=f"https://{apigee_environment}.api.service.nhs.uk/{config.OAUTH_PROXY}",
        client_id=app.get_client_id(),
        jwt_private_key=config.SIGNING_KEY,
        jwt_kid="test-1",
    )

    authenticator = ClientCredentialsAuthenticator(config=client_credentials_config)

    token_response = authenticator.get_token()
    assert "access_token" in token_response

    yield product, app, token_response, developer_apps_api, products_api

    app.destroy_app(developer_apps_api)
    product.destroy_product(products_api)


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
def encoded_jwt(identity_service_base_url: str):
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{identity_service_base_url}/token",
        "exp": int(time.time()) + 300,
    }

    encoded_jwt = jwt.encode(claims,
                             config.SIGNING_KEY,
                             algorithm="RS512",
                             headers={"kid": config.KEY_ID})

    return encoded_jwt


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
def nhs_login_sign_in(_test_app_credentials, apigee_environment, nhs_number, developer_apps_api, products_api):
    """
    Authenticating a user through NHS login
    """

    # Creating a new test app
    product = _product_with_full_access(products_api)
    product.update_environments([config.ENVIRONMENT], api_products=products_api)

    test_app = ApigeeApiDeveloperApps()
    test_app.create_new_app(
        callback_url="https://example.org/callback",
        status="approved",
        jwks_resource_url=config.JWKS_RESOURCE_URL,
        products=[product.name],
        developer_apps=developer_apps_api
    )

    # Set your app config
    authorizationCodeConfig = AuthorizationCodeConfig(
        environment=apigee_environment,
        identity_service_base_url=f"https://{apigee_environment}.api.service.nhs.uk/{config.OAUTH_PROXY}",
        callback_url=CALLBACK_URL,
        client_id=test_app.get_client_id(),
        client_secret=test_app.get_client_secret(),
        scope="nhs-login",
        login_form={"username": nhs_number},
    )

    # Pass the config to the Authenticator
    authenticator = AuthorizationCodeAuthenticator(config=authorizationCodeConfig)

    login_session = requests.session()

    # Hit `authorize` endpoint w/ required query params --> we
    # are redirected to the simulated_auth page. The requests package
    # follows those redirects.
    authorize_response = authenticator._get_authorize_endpoint_response(
        login_session,
        f"{authenticator.config.identity_service_base_url}/authorize",
        authenticator.config.client_id,
        authenticator.config.callback_url,
        authenticator.config.scope,
    )

    authorize_form = authenticator._get_authorization_form(
            authorize_response.content.decode()
    )
    # Parse the login page.  For keycloak this presents an
    # HTML form, which must be filled in with valid data.  The tester
    # can submits their login data with the `login_form` field.

    form_submission_data = authenticator._get_authorize_form_submission_data(
        authorize_form, authenticator.config.login_form
    )

    # POST the filled in form. This is equivalent to clicking the
    # "Login" button if we were a human.

    response_identity_service_login = authenticator._log_in_identity_service_provider(
        login_session, authorize_response, authorize_form, form_submission_data
    )

    # Clean up
    test_app.destroy_app(developer_apps_api)
    product.destroy_product(products_api)

    return response_identity_service_login
