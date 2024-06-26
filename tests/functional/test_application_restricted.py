import json
import pytest
from functools import partial
import jwt
import uuid
import time

import requests
from pytest_bdd import given, when, then, parsers
import pytest_bdd

from tests.functional.configuration import config
from tests.functional.utils import helpers

scenario = partial(pytest_bdd.scenario, "features/application_restricted.feature")


def teardown_function(function):
    time.sleep(0.01)


def get_patient_request(headers: dict, extra_params: dict = None):
    params = {"family": "Part", "gender": "male", "birthdate": "eq1931-10-04"}
    if extra_params:
        params = {**params, **extra_params}
    return requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?",
        headers=headers,
        params=params,
    )


def patch_patient_request(headers: dict):
    return requests.patch(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
        headers=headers,
    )


@given("I determine whether an asid is required")
def check_which_test_app_to_use():
    if "asid-required" in config.PDS_BASE_PATH:
        config.APPLICATION_RESTRICTED_API_KEY = (
            config.APPLICATION_RESTRICTED_WITH_ASID_API_KEY
        )
        config.SIGNING_KEY = config.APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY
        config.JWKS_RESOURCE_URL = config.JWKS_RESOURCE_URL_ASID_REQUIRED_APP


@scenario("PDS FHIR API rejects synchronous PATCH requests")
def test_rejects_synchronous_patch_request():
    pass


@pytest.mark.skipif(
    "asid-required" in config.PDS_BASE_PATH, reason="App-restricted update skip"
)
@scenario("App with pds-app-restricted-update attribute set to TRUE accepts PATCH requests")
def test_app_restricted_update_attribute_set_to_true():
    pass


@pytest.mark.skipif(
    "asid-required" in config.PDS_BASE_PATH, reason="App-restricted update skip"
)
@scenario("App with pds-app-restricted-update attribute set to FALSE does not accept PATCH requests")
def test_app_restricted_update_attribute_set_to_false():
    pass


@pytest.mark.skipif(
    "asid-required" in config.PDS_BASE_PATH, reason="App-restricted update skip"
)
@scenario(
    "App with pds-app-restricted-update attribute set to TRUE and invalid app restricted scope does not allow a PATCH"
)
def test_app_restricted_update_attribute_invalid_scope():
    pass


@scenario("PDS FHIR API rejects app restricted update")
def test_app_restricted_update_returns_error_msg():
    pass


@pytest.mark.skipif(
    "asid-required" not in config.PDS_BASE_PATH, reason="ASID required test only"
)
@scenario("App without an ASID fails in an asid-required API Proxy")
def test_app_without_asid_fails():
    pass


@pytest.mark.skipif(
    "asid-required" not in config.PDS_BASE_PATH, reason="ASID required test only"
)
@scenario("App WITH an ASID works in an asid-required API Proxy")
def test_app_with_asid_works():
    pass


@given("I am authenticating using unattended access", target_fixture="auth")
def auth():
    return {}


@given("I create a new app")
def create_test_app(setup_session, context):
    product, app, token_response, developer_apps, api_products = setup_session
    context["product"] = product
    context["app"] = app
    context["token_response"] = token_response
    context["developer_apps"] = developer_apps
    context["api_products"] = api_products


@given(parsers.parse("I add the attribute with key of {key} and a value of {value}"))
def add_custom_attribute_to_app(key: str, value: str, context: dict):

    app = context["app"]
    developer_apps = context["developer_apps"]
    app.set_custom_attributes(
        {
            "jwks-resource-url": config.JWKS_RESOURCE_URL,
            "asid": config.ENV["internal_dev_asid"],
            key: value
        },
        developer_apps
    )


@given("I add an asid attribute")
def add_asid_attribute_to_app(context: dict):

    app = context["app"]
    developer_apps = context["developer_apps"]
    app.set_custom_attributes(
        {
            "jwks-resource-url": config.JWKS_RESOURCE_URL,
            "asid": config.ENV["internal_dev_asid"],
        },
        developer_apps
    )


@given(parsers.parse("I add the scope {scope}"))
def add_scope_to_product(scope, context):
    product = context["product"]
    api_products = context["api_products"]
    product.update_scopes([scope], api_products)


@given("I have a valid access token")
def set_valid_access_token(auth, context):

    # Get new access token
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        "exp": int(time.time()) + 300,
    }

    # If one exists, use the client_id of the test app instead
    if "app" in context:
        claims.update(
            {
                "sub": context["app"].get_client_id(),
                "iss": context["app"].get_client_id(),
            }
        )

    headers = {"kid": config.KEY_ID}

    encoded_jwt = jwt.encode(
        claims, config.SIGNING_KEY, algorithm="RS512", headers=headers
    )

    response = requests.post(
        f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    token_response = response.json()
    print(token_response)

    # Does our response object contain the expected keys (maybe others too):
    assert {"access_token", "expires_in", "token_type", "issued_at"} <= set(
        token_response.keys()
    )

    assert token_response["access_token"] is not None
    assert token_response["token_type"] == "Bearer"
    assert token_response["expires_in"] and int(token_response["expires_in"]) > 0

    auth["response"] = token_response
    auth["access_token"] = token_response["access_token"]
    auth["token_type"] = token_response["token_type"]


@given("I have an expired access token")
def set_expired_access_token(auth):
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        "exp": int(time.time()) + 300,
    }

    encoded_jwt = jwt.encode(
        claims, config.SIGNING_KEY, algorithm="RS512", headers={"kid": config.KEY_ID}
    )

    response = requests.post(
        f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        data={
            "_access_token_expiry_ms": "1",
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    response_json = response.json()

    # Does our response object contain the expected keys (maybe others too):
    assert {"access_token", "expires_in", "token_type", "issued_at"} <= set(
        response_json.keys()
    )

    assert response_json["access_token"] is not None
    assert response_json["token_type"] == "Bearer"
    assert response_json["expires_in"] and int(response_json["expires_in"]) == 0

    auth["response"] = response_json
    auth["access_token"] = response_json["access_token"]
    auth["token_type"] = response_json["token_type"]


@given("I have a request context", target_fixture="context")
def context():
    return {}


@given(parsers.parse("I wait for {number_of:d} milliseconds"))
def wait_for_some_milliseconds(number_of: int):
    time.sleep(number_of / 1000)


@when("I GET a patient")
def get_patient(auth, context):
    headers = helpers.add_auth_header(
        {
            "NHSD-SESSION-URID": "123",
            "X-Request-ID": str(uuid.uuid4()),
        },
        auth,
    )

    response = get_patient_request(headers=headers)

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I PATCH a patient and ommit the prefer header")
def patch_sync_patient(auth, context):

    headers = helpers.add_auth_header(
        {
            "NHSD-SESSION-URID": "123",
            "X-Request-ID": str(uuid.uuid4()),
        },
        auth,
    )
    response = patch_patient_request(headers)

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I PATCH a patient")
def patch_patient(auth: dict, context: dict):

    headers = helpers.add_auth_header(
        {
            "X-Request-ID": str(uuid.uuid4()),
        },
        auth,
    )

    # GET patient to retrieve eTag
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
        headers=headers,
    )

    patient_version_id = response.headers['Etag']
    current_gender = (json.loads(response.text))["gender"]
    new_gender = "male" if current_gender == "female" else "female"

    # add the new gender to the patch
    patch = json.loads('{"patches":[{"op":"replace","path":"/gender","value":"male"}]}')
    patch["patches"][0]["value"] = new_gender

    headers.update(
        {
            "Content-Type": "application/json-patch+json",
            "If-Match": patient_version_id,
            "X-Request-ID": str(uuid.uuid4()),
        }
    )

    response = requests.patch(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
        headers=headers,
        json=patch,
    )

    context["status"] = response.status_code
    context["response"] = response.json()


@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def check_status(status, context):
    assert context["status"] == status


@then("I get an error response")
def check_error_response(context):
    assert context["response"]["issue"][0]["severity"] == "error"


@then(parsers.parse("the error {error_path} value is {error_msg}"))
def check_error_message_contains_value(error_path, error_msg, context):
    error_msg_set = map_error_response_to_dict(context)
    assert error_msg_set.get(error_path) == error_msg


def map_error_response_to_dict(context) -> dict:
    error_resp = context["response"]

    return {
        "issue.code": error_resp["issue"][0]["code"],
        "issue.details.coding.code": error_resp["issue"][0]["details"]["coding"][0][
            "code"
        ],
        "issue.details.coding.display": error_resp["issue"][0]["details"]["coding"][0][
            "display"
        ],
        "issue.diagnostics": error_resp["issue"][0]["diagnostics"],
        "issue.severity": error_resp["issue"][0]["severity"],
    }
