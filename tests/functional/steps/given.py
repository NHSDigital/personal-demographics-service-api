import pytest
from pytest_bdd import given, parsers
from requests import post
from tests.functional.data import searches
from tests.functional.data import patients
from tests.functional.data.patients import Patient
from tests.functional.data.searches import Search
from tests.functional.data.updates import Update
from tests.functional.steps.when import retrieve_patient
import json


@given('I have a patient with a related person', target_fixture='patient')
def patient_with_a_related_person() -> Patient:
    return patients.WITH_RELATED_PERSON


@given("I enter a patient's vague demographic details", target_fixture='search')
def vague_patient() -> Search:
    return searches.VAGUE


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
