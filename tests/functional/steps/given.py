import pytest
from pytest import FixtureRequest
from pytest_bdd import given, parsers
from requests import post
from tests.functional.data import searches
from tests.functional.data import patients
from tests.functional.data.users import UserDirectory
from tests.functional.data.patients import Patient
from tests.functional.data.searches import Search
from tests.functional.data.updates import Update
from tests.functional.steps.when import retrieve_patient
from pytest_nhsd_apim.apigee_apis import ApiProductsAPI

import json
from random import randint
from datetime import datetime
import time


@given('scope added to product')
def add_scope_to_products_patient_access(products_api: ApiProductsAPI,
                                         nhsd_apim_proxy_name: str,
                                         nhsd_apim_authorization: dict):
    scope = nhsd_apim_authorization['scope']
    product_name = nhsd_apim_proxy_name.replace("-asid-required", "")

    def is_scope_in_product() -> bool:
        return scope in products_api.get_product_by_name(product_name)['scopes']

    if is_scope_in_product():
        return

    product = products_api.get_product_by_name(product_name=product_name)
    product['scopes'].append(scope)
    products_api.put_product_by_name(product_name=product_name, body=product)

    max_wait, time_waited, wait_period = 10, 0, 1
    while not is_scope_in_product():
        if time_waited > max_wait:
            raise TimeoutError(f'Scope {scope} did not get added to'
                               f'product {product_name}')
        time.sleep(wait_period)
        time_waited += wait_period


@given('I am a patient with a related person', target_fixture='patient')
def self_patient_with_a_related_person() -> Patient:
    return patients.SELF_WITH_RELATED_PERSON


@given('I have a patient with a related person', target_fixture='patient')
def patient_with_a_related_person() -> Patient:
    return patients.WITH_RELATED_PERSON


@given("I enter a patient's vague demographic details", target_fixture='search')
def vague_patient() -> Search:
    return searches.VAGUE


@given("I am an unknown user", target_fixture='headers_with_authorization')
def provide_headers_with_no_auth_details() -> None:
    return {}


@pytest.fixture(scope='session')
def user_directory() -> UserDirectory:
    return UserDirectory()


@given(
    parsers.cfparse(
        "I am a {access_level:String} user with the NHS number linked to an account",
        extra_types=dict(String=str)
    ), target_fixture='patient')
def set_user(access_level: str) -> Patient:
    patient = patients.OTHER_PATIENTS[access_level]
    return patient


# Keep the comments for easily finding via text search...
# Given I am a healthcare worker user
@given(
    parsers.cfparse(
        "I am {_:String} {user_name:String} user",
        extra_types=dict(String=str)
    ))
def add_auth_marker(request: FixtureRequest, user_name: str, user_directory: UserDirectory) -> None:
    auth_details = user_directory[user_name.replace(' ', '_')
                                           .replace('-', '_')]
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))


@given("I have a patient's record to update")
@given("I have my record to update")
def record_to_update(update: Update, headers_with_authorization: dict, pds_url: str) -> dict:
    response = retrieve_patient(headers_with_authorization, update.nhs_number, pds_url)

    update.record = json.loads(response.text)
    update.etag = response.headers['Etag']

    return update.record


@given("I wish to update the patient's gender")
def add_new_gender_to_patch(update: Update) -> None:
    current_gender = update.record['gender']
    new_gender = 'male' if current_gender == 'female' else 'female'
    update.value = new_gender


@given("I wish to update my telephone number")
def replace_last_digit_in_telecom(update: Update) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    new_telecom_value = '07' + str(randint(000000000, 999999999))
    id_ = update.record['telecom'][0]['id']

    value = {
        'id': id_,
        'value': new_telecom_value,
        'system': 'phone',
        'use': 'mobile',
        'period': {
            'start': today
        }
    }
    update.value = value


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


@given("I have a refreshed access token", target_fixture='headers_with_authorization')
def add_refresh_token_to_auth_header(headers_with_authorization: dict,
                                     identity_service_base_url: str,
                                     _nhsd_apim_auth_token_data: dict,
                                     _test_app_credentials: dict) -> dict:
    old_token = _nhsd_apim_auth_token_data.get('access_token')
    refresh_token = _nhsd_apim_auth_token_data.get('refresh_token')

    response = post(
        f"{identity_service_base_url}/token",
        data={
            "client_id": _test_app_credentials["consumerKey"],
            "client_secret": _test_app_credentials["consumerSecret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200, f'POST /token failed. Response:\n {response.text}'

    new_token = response.json()['access_token']
    assert new_token != old_token
    headers_with_authorization.update({
        'Authorization': f'Bearer {new_token}'
    })
    return headers_with_authorization
