import datetime
import jwt
import uuid
import time
import requests
from .config_files import config
from pytest import mark
from pytest_bdd import scenario, given, when, then, parsers


# simple patient request
def get_patient_request(headers: dict):
    return requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?",
        headers=headers,
        params={
            "family": "Smith",
            "gender": "female",
            "birthdate": "eq2010-10-22"
        }
    )


@mark.skip(reason="unfinished code")
@scenario(
    "features/unattended_access.feature",
    "PDS FHIR API accepts request with valid access token",
)
def test_valid():
    pass


@mark.skip(reason="unfinished code")
@scenario(
    "features/unattended_access.feature",
    "PDS FHIR API rejects request with invalid access token",
)
def test_invalid():
    pass


@mark.skip(reason="unfinished code")
@scenario(
    "features/unattended_access.feature",
    "PDS FHIR API rejects request with missing access token",
)
def test_missing():
    pass


@mark.skip(reason="unfinished code")
@scenario(
    "features/unattended_access.feature",
    "PDS FHIR API rejects request with expired access token",
)
def test_expired():
    pass


@given("I am authenticating using unattended access", target_fixture="auth")
def auth():
    return {}


@given("I have a valid access token")
def set_valid_access_token(auth):
    claims = {
        "sub": config.UNATTENDED_ACCESS_API_KEY,
        "iss": config.UNATTENDED_ACCESS_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/oauth2/token",
        "exp": int(time.time()) + 300,
    }

    headers = {
        "kid": config.KEY_ID
        }

    encoded_jwt = jwt.encode(claims, config.SIGNING_KEY, algorithm="RS512", headers=headers)

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
    try:
        response_expires_in = int(response_json["expires_in"])
        assert response_expires_in >= 0
    except:
        assert False, "Invalid 'expires_in' value. Must be an integer."

    auth["response"] = response.json()


@given("I have an invalid access token")
def set_invalid_access_token(auth):
    auth["access_token"] = "INVALID_ACCESS_TOKEN"


@given("I have no access token")
def set_no_access_token(auth):
    auth["access_token"] = None


@given("I have an expired access token")
def set_expired_access_token(auth):
    claims = {
        "sub": config.UNATTENDED_ACCESS_API_KEY,
        "iss": config.UNATTENDED_ACCESS_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/oauth2/token",
        "exp": int(time.time()),
    }

    headers = {
        "kid": config.KEY_ID
        }

    encoded_jwt = jwt.encode(claims, config.SIGNING_KEY, algorithm="RS512", headers=headers)

    response = requests.post(
        f"{config.BASE_URL}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        }
    )

    print(response.json())

    assert False


@given("I have a request context", target_fixture="context")
def context():
    return {}


@when("I GET a patient")
def get_patient(auth, context):
    authentication = auth["access_token"]

    if authentication is not None:
        token_type = auth["token_type"]
        authentication = f"{token_type} {authentication}"

    headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": f"Bearer {authentication}",
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
    print(context["response"])
    assert context["status"] == status


@then("I get a Patient resource in the response")
def check_patient_resource(context):
    expected_keys = {
        "resourceType",
        "timestamp",
        "total",
        "type"
    }
    assert context["response"].keys() == expected_keys
    assert context["response"]["resourceType"] == "Bundle"
    assert context["response"]["total"] == 0
    assert context["response"]["type"] == "searchset"

    try:
        datetime.datetime.strptime(context["response"]["timestamp"], '%Y-%m-%dT%H:%M:%S+00:00')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DDThh-mm-ss+00:00")


@then("I get a diagnosis of invalid access token")
def check_diagnosis_invalid(context):
    assert context["response"]["issue"][0]["diagnostics"] == "Invalid Access Token"


@then("I get a diagnosis of expired access token")
def check_diagnosis_expired(context):
    assert False


@then("I get an error response")
def check_error_response(context):
    assert context["response"]["issue"][0]["severity"] == "error"


@scenario(
    "features/unattended_access.feature",
    "PDS FHIR API accepts request without user role ID",
)
def test_valid_when_without_user_id():
    pass


@when("I GET a patient without a user role ID")
def get_patient_without_user_role_id(auth, context):
    access_token = auth["response"]["access_token"]

    headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Request-ID": str(uuid.uuid4())
        }

    response = get_patient_request(headers)

    context["response"] = response.json()
    context["status"] = response.status_code
