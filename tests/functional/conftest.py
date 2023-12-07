from tests.scripts.pds_request import GenericPdsRequestor, PdsRecord
import pytest
import os
from pytest_bdd import given, when, then, parsers
from jsonpath_rw import parse
from pytest_check import check
import urllib
import uuid
from .utils.apigee_api_apps import ApigeeApiDeveloperApps
from .utils.apigee_api_products import ApigeeApiProducts
from .configuration import config
from .configuration.config import BASE_URL, PDS_BASE_PATH
import random
from requests import Response, get, patch, post
import json
import jwt
from typing import Union
from .data.searches import Search
from .data.updates import Update
from .data import searches
from .data import updates
from .data import patients
from .data.patients import Patient
from copy import copy
from tests.functional.utils.helpers import is_key_in_dict
import time

from pytest_nhsd_apim.identity_service import (
    ClientCredentialsConfig,
    ClientCredentialsAuthenticator,
)

from pytest_nhsd_apim.apigee_apis import (
    ApiProductsAPI,
    DeveloperAppsAPI,
)

FILE_DIR = os.path.dirname(__file__)
RESPONSES_DIR = os.path.join(FILE_DIR, 'data', 'responses')


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


@given("I am an unknown user", target_fixture='headers_with_authorization')
def provide_headers_with_no_auth_details() -> None:
    return {}


@given("I am a healthcare worker")
def provide_healthcare_worker_auth_details(request) -> None:
    auth_details = {
        "api_name": "personal-demographics-service",
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
        "force_new_token": True
    }
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@given("I am a P9 user")
def provide_p9_auth_details(request) -> None:
    auth_details = {
        "api_name": "personal-demographics-service",
        "access": "patient",
        "level": "P9",
        "login_form": {"username": "9912003071"},
        "force_new_token": True
    }
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@given('scope added to product')
def add_scope_to_products_patient_access(products_api: ApiProductsAPI,
                                         nhsd_apim_proxy_name: str,
                                         nhsd_apim_authorization: dict):
    product_name = nhsd_apim_proxy_name.replace("-asid-required", "")

    default_product = products_api.get_product_by_name(product_name=product_name)
    if nhsd_apim_authorization['scope'] not in default_product['scopes']:
        default_product['scopes'].append(nhsd_apim_authorization['scope'])
        products_api.put_product_by_name(product_name=product_name, body=default_product)
        time.sleep(2)


@given("I am a P5 user")
def provide_p5_auth_details(request) -> None:
    auth_details = {
        "api_name": "personal-demographics-service",
        "access": "patient",
        "level": "P5",
        "login_form": {"username": "9912003071"},
        "force_new_token": True
    }
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@given("I am a p5 user")
def provide_p5_lower_case_auth_details(request) -> None:
    auth_details = {
        "api_name": "personal-demographics-service",
        "access": "patient",
        "level": "p5",
        "login_form": {"username": "9912003071"},
        "force_new_token": True
    }
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@given("I am a P0 user")
def provide_p0_auth_details(request) -> None:
    auth_details = {
        "api_name": "personal-demographics-service",
        "access": "patient",
        "level": "P0",
        "login_form": {"username": "9912003071"},
        "force_new_token": True
    }
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@pytest.fixture()
def search() -> Search:
    return searches.DEFAULT


@pytest.fixture()
def update() -> Update:
    return updates.DEFAULT


@given("I enter a patient's vague demographic details", target_fixture='search')
def vague_patient() -> Search:
    return searches.VAGUE


@pytest.fixture()
def patient() -> Patient:
    return patients.DEFAULT


@given('I have a patient with a related person', target_fixture='patient')
def patient_with_a_related_person() -> Patient:
    return patients.WITH_RELATED_PERSON


@pytest.fixture()
def nhs_number(patient: Patient) -> str:
    return patient.nhs_number


@given("I have a patient's record to update", target_fixture='record_to_update')
def record_to_update(update: Update, headers_with_authorization: dict, pds_url: str) -> dict:
    response = retrieve_patient(headers_with_authorization, update.nhs_number, pds_url)

    update.record_to_update = json.loads(response.text)
    update.etag = response.headers['Etag']

    return update.record_to_update


@given("I wish to update the patient's gender")
def add_new_gender_to_patch(update: Update) -> None:
    current_gender = update.record_to_update['gender']
    new_gender = 'male' if current_gender == 'female' else 'female'
    update.value = new_gender


@given(
    parsers.cfparse(
        "I don't have {_:String} {header_field:String} header",
        extra_types=dict(String=str)
    ),
    target_fixture='headers_with_authorization'
)
def remove_header(headers_with_authorization, header_field) -> dict:
    headers_with_authorization.pop(header_field)
    return headers_with_authorization


@given(
    parsers.cfparse(
        'I have a header {field:String} value of "{value:String}"',
        extra_types=dict(String=str)
    ),
    target_fixture='headers_with_authorization')
def update_header(headers_with_authorization: dict, field: str, value: str) -> dict:
    headers_with_authorization.update({field: value})
    return headers_with_authorization


@given(
    parsers.cfparse(
        "I have an empty {field:String} header",
        extra_types=dict(String=str)
    ),
    target_fixture='headers_with_authorization')
def empty_header(headers_with_authorization: dict, field: str) -> dict:
    headers_with_authorization.update({field: ''})
    return headers_with_authorization


@given("I have an expired access token", target_fixture='headers_with_authorization')
def add_expired_token_to_auth_header(headers_with_authorization: dict,
                                     encoded_jwt: dict,
                                     identity_service_base_url: str) -> dict:
    response = post(
        f"{identity_service_base_url}/token",
        data={
            "_access_token_expiry_ms": "1",
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    assert response.status_code == 200, f'POST /token failed. Response:\n {response.text}'

    response_json = response.json()
    assert response_json["expires_in"] and int(response_json["expires_in"]) == 0

    token_value = response_json['access_token']
    headers_with_authorization.update({
        'Authorization': f'Bearer {token_value}'
    })
    return headers_with_authorization


@pytest.fixture
def query_params(search: Search) -> str:
    return urllib.parse.urlencode(search.query)


@when('I retrieve my details', target_fixture='response')
@when('I retrieve a patient', target_fixture='response')
def retrieve_patient(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}", headers=headers_with_authorization)


@when('I retrieve their related person', target_fixture='response')
def retrieve_related_person(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}/RelatedPerson", headers=headers_with_authorization)


@when("I update the patient's PDS record", target_fixture='response')
@when("I update another patient's PDS record", target_fixture='response')
def update_patient(headers_with_authorization: dict, update: Update, pds_url: str) -> Response:
    headers = headers_with_authorization
    headers.update({
        "Content-Type": "application/json-patch+json",
        "If-Match": update.etag,
    })

    return patch(url=f"{pds_url}/Patient/{update.nhs_number}",
                 headers=headers,
                 json=update.patches)


@when("I update another patient's PDS record using an incorrect path", target_fixture='response')
def update_patient_incorrect_path(headers_with_authorization: dict, update: Update, pds_url: str) -> Response:
    headers = headers_with_authorization
    headers.update({
        "Content-Type": "application/json-patch+json",
        "If-Match": update.etag,
    })

    return patch(url=f"{pds_url}/Patient?family=Smith&gender=female&birthdate=eq2010-10-22",
                 headers=headers,
                 json=update.patches)


@when(
    parsers.cfparse(
        "I hit the /{endpoint:String} endpoint",
        extra_types=dict(String=str)
    ),
    target_fixture='response'
)
def hit_endpoint(headers_with_authorization: dict, pds_url: str, endpoint: str):
    return get(url=f'{pds_url}/{endpoint}', headers=headers_with_authorization)


@when(
    parsers.cfparse(
        'the query parameters contain {key:String} as {value:String}',
        extra_types=dict(String=str)
    ),
    target_fixture='query_params',
)
def amended_query_params(search: Search, key: str, value: str) -> str:
    query_params = copy(search.query)
    query_params.append((key, value))
    return urllib.parse.urlencode(query_params)


@when("I search for a patient's PDS record", target_fixture='response')
@when("I search for the patient's PDS record", target_fixture='response')
def search_patient(headers_with_authorization: dict, query_params: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient?{query_params}", headers=headers_with_authorization)


@then(
    parsers.cfparse(
        "I get a {expected_status:Number} HTTP response code",
        extra_types=dict(Number=int)
    )
)
def check_status(response: Response, expected_status: int) -> None:
    with check:
        assert response.status_code == expected_status


@then(
    parsers.cfparse(
        'the response body is the {expected_response:String} response',
        extra_types=dict(String=str)
    )
)
def response_body_contains_error(response_body: dict, expected_response: str) -> None:
    response_file = expected_response.replace(' ', '_').lower()
    with open(os.path.join(RESPONSES_DIR, f'{response_file}.json'), 'r') as f:
        expected_response_body = json.load(f)
    assert response_body == expected_response_body


@then(
    parsers.cfparse(
        '{value:String} is at {path:String} in the response body',
        extra_types=dict(String=str)
    ))
def check_value_in_response_body_at_path(response_body: dict, value: str, path: str) -> None:
    matches = parse(path).find(response_body)
    with check:
        assert matches, f'There are no matches for {value} at {path} in the response body'
        for match in matches:
            assert match.value == value, f'{match.value} is not the expected value, {value}, at {path}'


@then('the response body contains the expected response')
def response_body_as_expected(response_body: dict, patient: Patient) -> None:
    assert response_body == patient.expected_response


@then(
    parsers.cfparse(
        'the {header_field:String} response header matches the request',
        extra_types=dict(String=str)
    )
)
def check_header_value(response: Response,
                       header_field: str,
                       headers_with_authorization: dict) -> None:
    with check:
        assert response.headers[header_field] == headers_with_authorization[header_field]


@then("the response body contains the patient's NHS number")
def response_body_contains_given_id(response_body: dict, nhs_number: dict) -> None:
    with check:
        assert response_body["id"] == nhs_number
        assert response_body["resourceType"] == "Patient"


@then('the response body is the correct shape')
def response_body_shape(response_body: Response) -> None:
    with check:
        assert response_body["address"] is not None
        assert isinstance(response_body["address"], list)

        assert response_body["birthDate"] is not None
        assert isinstance(response_body["birthDate"], str)
        assert len(response_body["birthDate"]) > 1

        assert response_body["gender"] is not None
        assert isinstance(response_body["gender"], str)

        assert response_body["name"] is not None
        assert isinstance(response_body["name"], list)
        assert len(response_body["name"]) > 0

        assert len(response_body["identifier"]) > 0
        assert isinstance(response_body["identifier"], list)

        assert response_body["meta"] is not None


@then('the response body contains the expected values')
def check_expected_search_response_body(response_body: dict, search: Search) -> None:
    with check:
        for field in search.expected_response_fields:
            matches = parse(field.path).find(response_body)
            assert matches, f'There are no matches for {field.expected_value} at {field.path} in the response body'
            for match in matches:
                assert match.value == field.expected_value,\
                    f'{field.path} in response does not contain the expected value, {field.expected_value}'


@then('the response body does not contain sensitive fields')
def check_sensitive_fields_are_absent(response_body: dict) -> None:
    _sensitive_fields = ['address',
                         'telecom',
                         'generalPractitioner']
    with check:
        for field in _sensitive_fields:
            assert not is_key_in_dict(response_body, field), f'Sensitive field, {field}, in response.'


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
        callback_url="https://example.org/callback",
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
