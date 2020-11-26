import dateutil.parser
import jwt
import uuid
import time
import requests
from .config_files import config
from .config_files.environment import ENV
# from pytest import mark
from pytest_bdd import scenario, given, when, then, parsers


def get_patient_request(headers: dict, extra_params: dict = None):
    params = {"family": "Smith", "gender": "female", "birthdate": "eq2010-10-22"}
    if extra_params:
        params = {**params, **extra_params}
    return requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?",
        headers=headers,
        params=params,
    )


@given("I determine whether an asid is required")
def check_which_test_app_to_use():
    if "asid-required" in config.PDS_BASE_PATH:
        config.APPLICATION_RESTRICTED_API_KEY = ENV["application_restricted_with_asid_api_key"]
        config.SIGNING_KEY = ENV["signing_key_with_asid"]


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request with valid access token",
)
def test_valid():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with invalid access token",
)
def test_invalid():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with missing access token",
)
def test_missing():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with expired access token",
)
def test_expired():
    pass


# @mark.skip(reason="broken on internal-qa")
@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request without user role ID",
)
def test_valid_when_without_user_id():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request for more than one result",
)
def test_rejects_request_for_two_results():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request for one result",
)
def test_accepts_request_for_one_result():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects PATCH requests",
)
def test_rejects_patch_request():
    pass


@given("I am authenticating using unattended access", target_fixture="auth")
def auth():
    return {}


@given("I have a valid access token")
def set_valid_access_token(auth):
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/oauth2/token",
        "exp": int(time.time()) + 300,
    }

    headers = {"kid": config.KEY_ID}

    encoded_jwt = jwt.encode(
        claims, config.SIGNING_KEY, algorithm="RS512", headers=headers
    )

    response = requests.post(
        f"{config.BASE_URL}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    response_json = response.json()

    assert {"access_token", "expires_in", "token_type"} == response_json.keys()
    assert response_json["access_token"] is not None
    assert response_json["token_type"] == "Bearer"
    assert response_json["expires_in"] and int(response_json["expires_in"]) > 0

    auth["response"] = response_json
    auth["access_token"] = response_json["access_token"]
    auth["token_type"] = response_json["token_type"]


@given("I have an invalid access token")
def set_invalid_access_token(auth):
    auth["access_token"] = "INVALID_ACCESS_TOKEN"
    auth["token_type"] = "Bearer"


@given("I have no access token")
def set_no_access_token(auth):
    auth["access_token"] = None
    auth["token_type"] = "Bearer"


@given("I have an expired access token")
def set_expired_access_token(auth):
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/oauth2/token",
        "exp": int(time.time()) + 300,
    }

    encoded_jwt = jwt.encode(
        claims, config.SIGNING_KEY, algorithm="RS512", headers={"kid": config.KEY_ID}
    )

    response = requests.post(
        f"{config.BASE_URL}/oauth2/token",
        data={
            "_access_token_expiry_ms": "1",
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    response_json = response.json()

    assert {"access_token", "expires_in", "token_type"} == response_json.keys()
    assert response_json["access_token"] is not None
    assert response_json["token_type"] == "Bearer"
    assert response_json["expires_in"] and int(response_json["expires_in"]) == 0

    auth["response"] = response_json
    auth["access_token"] = response_json["access_token"]
    auth["token_type"] = response_json["token_type"]


@given("I have a request context", target_fixture="context")
def context():
    return {}


@when("I GET a patient")
def get_patient(auth, context):
    authentication = auth["access_token"]

    if authentication is not None:
        token_type = auth["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        headers={
            "NHSD-SESSION-URID": "123",
            "Authorization": f"{authentication}",
            "X-Request-ID": str(uuid.uuid4()),
        }
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I GET a patient asking for two results")
def get_patient_two_results(auth, context):
    authentication = auth["access_token"]

    if authentication is not None:
        token_type = auth["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        headers={
            "NHSD-SESSION-URID": "123",
            "Authorization": f"{authentication}",
            "X-Request-ID": str(uuid.uuid4()),
        },
        extra_params={"_max-results": "2"},
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I PATCH a patient")
def patch_patient(auth, context):
    authentication = auth["access_token"]

    if authentication is not None:
        token_type = auth["token_type"]
        authentication = f"{token_type} {authentication}"

    headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": f"{authentication}",
        "X-Request-ID": str(uuid.uuid4()),
    }

    response = requests.patch(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9123123123",
        headers=headers,
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I GET a patient asking for one result")
def get_patient_one_result(auth, context):
    authentication = auth["access_token"]

    if authentication is not None:
        token_type = auth["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        headers={
            "NHSD-SESSION-URID": "123",
            "Authorization": f"{authentication}",
            "X-Request-ID": str(uuid.uuid4()),
        },
        extra_params={"_max-results": "1"},
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I GET a patient without a user role ID")
def get_patient_without_user_role_id(auth, context):
    access_token = auth["response"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Request-ID": str(uuid.uuid4()),
    }

    response = get_patient_request(headers)

    context["response"] = response.json()
    context["status"] = response.status_code


@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def check_status(status, context):
    assert context["status"] == status


@then("I get a Bundle resource in the response")
def check_bundle_resource(context):
    response = context["response"]
    EXPECTED_KEYS = {"resourceType", "timestamp", "total", "type"}
    assert response.keys() == EXPECTED_KEYS
    assert response["resourceType"] == "Bundle"
    assert response["type"] == "searchset"
    assert response["total"] >= 0
    assert dateutil.parser.parse(response["timestamp"])


@then("I get a diagnosis of Invalid Access Token")
def check_diagnosis_invalid(context):
    assert context["response"]["issue"][0]["diagnostics"] == "Invalid Access Token"


@then("I get a diagnosis of insufficient permissions")
def check_diagnosis_insufficient_perms(context):
    assert (
        context["response"]["issue"][0]["diagnostics"]
        == "Your app has insufficient permissions to perform this search. Please contact support."
    )


@then("I get a diagnosis of insufficient permissions to use this method")
def check_diagnosis_invalid_method(context):
    assert (
        context["response"]["issue"][0]["diagnostics"]
        == "Your app has insufficient permissions to use this method. Please contact support."
    )


# This needs to be changed, as it's a confusing message
@then("I get a diagnosis of Invalid access token")
def check_diagnosis_missing(context):
    assert context["response"]["issue"][0]["diagnostics"] == "Invalid access token"


@then("I get a diagnosis of expired access token")
def check_diagnosis_expired(context):
    assert context["response"]["issue"][0]["diagnostics"] == "Access Token expired"


@then("I get an error response")
def check_error_response(context):
    assert context["response"]["issue"][0]["severity"] == "error"
