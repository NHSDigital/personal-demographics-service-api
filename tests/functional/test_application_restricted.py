import dateutil.parser
import jwt
import uuid
import time
import requests
from pytest_bdd import scenario, given, when, then, parsers


def teardown_function(function):
    time.sleep(0.01)


def get_patient_request(context: dict, headers: dict, extra_params: dict = None):
    params = {"family": "Part", "gender": "male", "birthdate": "eq1931-10-04"}
    if extra_params:
        params = {**params, **extra_params}
    return requests.get(
        f"{context['BASE_URL']}/{context['PDS_BASE_PATH']}/Patient?",
        headers=headers,
        params=params,
    )


def patch_patient_request(context: dict, headers: dict):
    return requests.patch(
        f"{context['BASE_URL']}/{context['PDS_BASE_PATH']}/Patient/{context['TEST_PATIENT_ID']}",
        headers=headers,
    )


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request with valid access token",
)
def test_app_restricted_valid():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with invalid access token",
)
def test_app_restricted_invalid():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with missing access token",
)
def test_app_restricted_missing():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request with expired access token",
)
def test_app_restricted_expired():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request without user role ID",
)
def test_app_restricted_valid_when_without_user_id():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects request for more than one result",
)
def test_app_restricted_rejects_request_for_two_results():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API accepts request for one result",
)
def test_app_restricted_accepts_request_for_one_result():
    pass


@scenario(
    "features/application_restricted.feature",
    "PDS FHIR API rejects synchronous PATCH requests",
)
def test_app_restricted_rejects_synchronous_patch_request():
    pass


# -------------------------------- SCENARIO ----------------------------


@given("I am authenticating using unattended access", target_fixture="context")
def setup_app_restricted(cfg):
    context = {
        **cfg
    }
    return context


@given("I have a valid access token")
def set_valid_access_token(context):
    claims = {
        "sub": context["APPLICATION_RESTRICTED_API_KEY"],
        "iss": context["APPLICATION_RESTRICTED_API_KEY"],
        "jti": str(uuid.uuid4()),
        "aud": f"{context['BASE_URL']}/oauth2/token",
        "exp": int(time.time()) + 300,
    }

    headers = {"kid": context["KEY_ID"]}

    encoded_jwt = jwt.encode(
        claims, context["SIGNING_KEY"], algorithm="RS512", headers=headers
    )

    response = requests.post(
        f"{context['BASE_URL']}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    response_json = response.json()
    print(response_json)

    # Does our response object contain the expected keys (maybe others too):
    assert {"access_token", "expires_in", "token_type", "issued_at"} <= set(response_json.keys())
    assert response_json["access_token"] is not None
    assert response_json["token_type"] == "Bearer"
    assert response_json["expires_in"] and int(response_json["expires_in"]) > 0

    context["response"] = response_json
    context["access_token"] = response_json["access_token"]
    context["token_type"] = response_json["token_type"]


@given("I have an invalid access token", target_fixture="context")
def set_invalid_access_token(cfg):
    context = {
        **cfg,
        "access_token": "INVALID_ACCESS_TOKEN",
        "token_type": "Bearer",
    }
    return context


@given("I have no access token", target_fixture="context")
def set_no_access_token(cfg):
    context = {
        **cfg,
        "access_token": None,
        "token_type": "Bearer",
    }
    return context


@given("I have an expired access token")
def set_expired_access_token(context):
    claims = {
        "sub": context["APPLICATION_RESTRICTED_API_KEY"],
        "iss": context["APPLICATION_RESTRICTED_API_KEY"],
        "jti": str(uuid.uuid4()),
        "aud": f"{context['BASE_URL']}/oauth2/token",
        "exp": int(time.time()) + 300,
    }

    encoded_jwt = jwt.encode(
        claims, context["SIGNING_KEY"], algorithm="RS512", headers={"kid": context["KEY_ID"]}
    )

    response = requests.post(
        f"{context['BASE_URL']}/oauth2/token",
        data={
            "_access_token_expiry_ms": "1",
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    response_json = response.json()

    # Does our response object contain the expected keys (maybe others too):
    assert {"access_token", "expires_in", "token_type", "issued_at"} <= set(response_json.keys())

    assert response_json["access_token"] is not None
    assert response_json["token_type"] == "Bearer"
    assert response_json["expires_in"] and int(response_json["expires_in"]) == 0

    context["response"] = response_json
    context["access_token"] = response_json["access_token"]
    context["token_type"] = response_json["token_type"]


@given("I have a request context")
def request_context(context):
    return context


@given("I determine whether an asid is required", target_fixture="context")
def check_which_test_app_to_use(cfg: dict):
    context = {
        **cfg
    }
    if "asid-required" in context["PDS_BASE_PATH"]:
        context["APPLICATION_RESTRICTED_API_KEY"] = context[
            "APPLICATION_RESTRICTED_WITH_ASID_API_KEY"
        ]
        context["SIGNING_KEY"] = context["signing_key_with_asid"]


@when("I GET a patient")
def get_patient(context):
    authentication = context["access_token"]

    if authentication is not None:
        token_type = context["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        context,
        headers={
            "NHSD-SESSION-URID": "123",
            "Authorization": f"{authentication}",
            "X-Request-ID": str(uuid.uuid4()),
        }
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I GET a patient asking for two results")
def get_patient_two_results(context):
    authentication = context["access_token"]

    if authentication is not None:
        token_type = context["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        context,
        headers={
            "NHSD-SESSION-URID": "123",
            "Authorization": f"{authentication}",
            "X-Request-ID": str(uuid.uuid4()),
        },
        extra_params={"_max-results": "2"},
    )

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I PATCH a patient and ommit the prefer header")
def patch_sync_patient(context):
    authentication = context["access_token"]

    if authentication is not None:
        token_type = context["token_type"]
        authentication = f"{token_type} {authentication}"

    headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": f"{authentication}",
        "X-Request-ID": str(uuid.uuid4()),
    }

    response = patch_patient_request(context, headers)

    context["response"] = response.json()
    context["status"] = response.status_code


@when("I GET a patient asking for one result")
def get_patient_one_result(context):
    authentication = context["access_token"]

    if authentication is not None:
        token_type = context["token_type"]
        authentication = f"{token_type} {authentication}"

    response = get_patient_request(
        context,
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
def get_patient_without_user_role_id(context):
    access_token = context["response"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Request-ID": str(uuid.uuid4()),
    }

    response = get_patient_request(context, headers)

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
    EXPECTED_KEYS = {"entry", "resourceType", "timestamp", "total", "type"}
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
