import pytest_bdd
from pytest_bdd import given, then, parsers
from functools import partial
from .data.patients import Patient
from .data import searches
from .data.searches import Search
from .data.updates import Update
from .utils.helpers import get_role_id_from_user_info_endpoint
import pytest
from pytest_check import check
import logging
from .configuration.config import BASE_URL, PDS_BASE_PATH
from requests import Response
import re
import uuid
from jsonpath_rw import parse


AUTH_HEALTHCARE_WORKER = {
        "api_name": "personal-demographics-service",
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
        "force_new_token": True
    }
LOGGER = logging.getLogger(__name__)

retrieve_scenario = partial(pytest_bdd.scenario, './features/healthcare_worker_retrieve.feature')
search_scenario = partial(pytest_bdd.scenario, './features/healthcare_worker_search.feature')
update_scenario = partial(pytest_bdd.scenario, './features/healthcare_worker_update.feature')

related_person_scenario = partial(pytest_bdd.scenario, './features/related_person.feature')

status_scenario = partial(pytest_bdd.scenario, './features/status_endpoints.feature')


@retrieve_scenario('Healthcare worker can retrieve patient')
def test_retrieve_patient():
    pass


@retrieve_scenario('Healthcare worker using deprecated url')
def test_retrieve_with_deprecated_url():
    pass


@retrieve_scenario('Attempt to retrieve a patient with missing authorization header')
def test_retrieve_with_missing_auth():
    pass


@retrieve_scenario('Attempt to retrieve a patient with an empty authorization header')
def test_retrieve_using_empty_auth():
    pass


@retrieve_scenario('Attempt to retrieve a patient with an invalid authorization header')
def test_retrieve_using_invalid_auth():
    pass


@retrieve_scenario('Attempt to retrieve a patient without stating a role')
def test_retrieve_with_missing_role():
    pass


@retrieve_scenario('Attempt to retrieve a patient with an invalid role')
def test_retrieve_using_invalid_role():
    pass


@retrieve_scenario('Attempt to retrieve a patient without Request ID header')
def test_retrieve_using_empty_request_id():
    pass


@retrieve_scenario('Attempt to retrieve a patient with an invalid X-Request-ID')
def test_retrieve_using_invalid_request_id():
    pass


@retrieve_scenario('Attempt to retrieve a patient with a missing X-Request-ID')
def test_retrieve_with_missing_request_id():
    pass


@search_scenario('Healthcare worker can search for patient')
def test_search_patient():
    pass


@search_scenario('Attempt to search for a patient with missing authorization header')
def test_search_with_missing_auth():
    pass


@search_scenario('Attempt to search for a patient with an empty authorization header')
def test_search_using_empty_auth():
    pass


@search_scenario('Attempt to search for a patient with an invalid authorization header')
def test_search_using_invalid_auth():
    pass


@search_scenario('Attempt to search for a patient with an empty Request ID header')
def test_search_using_empty_request_id():
    pass


@search_scenario('Attempt to search for a patient with an invalid X-Request-ID')
def test_search_using_invalid_request_id():
    pass


@search_scenario('Attempt to search for a patient with a missing X-Request-ID')
def test_search_with_missing_request_id():
    pass


@search_scenario('Healthcare worker searches for sensitive patient')
def test_search_sensitive_patient():
    pass


@search_scenario('Healthcare worker searches for patient without specifying gender')
def test_search_gender_free():
    pass


@search_scenario('Healthcare worker searches for a patient with range for date of birth')
def test_search_with_dob_range():
    pass


@search_scenario('Searching without gender can return mutliple results')
def test_search_with_vauge_details():
    pass


@search_scenario('Searching with fuzzy match')
def test_search_with_fuzzy_match():
    pass


@search_scenario('Searching with unicode returns unicode record')
def test_search_with_unicode():
    pass


@search_scenario('Searching with specified results limit can return error')
def test_search_returns_error_due_to_results_limit():
    pass


@search_scenario('Search returns an empty bundle')
def test_search_returns_empty():
    pass


@update_scenario('Update patient')
def test_update_patient():
    pass


@update_scenario('Update patient using deprecated respond-async still returns 200')
def test_update_patient_with_deprecated_header():
    pass


@update_scenario('Update patient with invalid wait header still updates')
def test_update_with_invalid_wait():
    pass


@update_scenario('Update patient with low wait header')
def test_update_with_low_wait():
    pass


@update_scenario('Update patient with missing Authorization header')
def test_update_with_missing_auth():
    pass


@update_scenario('Update patient with an empty authorization header')
def test_update_with_empty_auth():
    pass


@update_scenario('Update patient with an invalid authorization header')
def test_update_using_invalid_auth():
    pass


@update_scenario('Update patient with an empty Request ID header')
def test_update_using_empty_request_id():
    pass


@update_scenario('Update patient with an invalid X-Request-ID')
def test_update_using_invalid_request_id():
    pass


@update_scenario('Update patient with a missing X-Request-ID')
def test_update_with_missing_request_id():
    pass


@related_person_scenario('Retrieve a related person')
def test_retrieve_related_person():
    pass


@status_scenario('Ping endpoint')
def test_ping():
    pass


@status_scenario('Healthcheck endpoint')
def test_healthcheck():
    pass


@pytest.fixture(scope='function')
def headers_with_authorization(
    _nhsd_apim_auth_token_data,
    identity_service_base_url,
    add_asid_to_testapp
):
    """Assign required headers with the Authorization header"""

    LOGGER.info(f'_nhsd_apim_auth_token_data: {_nhsd_apim_auth_token_data}')
    access_token = _nhsd_apim_auth_token_data.get("access_token", "")

    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "Authorization": f'Bearer {access_token}'
               }

    role_id = get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)
    headers.update({"NHSD-Session-URID": role_id})

    # setattr(request.cls, 'headers', headers)
    LOGGER.info(f'headers: {headers}')
    return headers


@given("I have a sensitive patient's demographic details", target_fixture='search')
def search_for_sensitive() -> Patient:
    return searches.SENSITIVE


@given("I have a patient's demographic details without gender", target_fixture='search')
def search_without_gender() -> Patient:
    return searches.UNKNOWN_GENDER


@given("I have a patient's demographic details with a date of birth range", target_fixture='search')
def search_dob_range() -> Patient:
    return searches.DOB_RANGE


@given("I enter a patient's fuzzy demographic details", target_fixture='search')
def fuzzy_search() -> Search:
    return searches.FUZZY


@given("I enter a patient's unicode demographic details", target_fixture='search')
def unicode_search() -> Search:
    return searches.UNICODE


@given("I enter a patient's demographic details incorrectly", target_fixture='search')
def empty_search() -> Search:
    return searches.EMPTY_RESULTS


@given('I am using the deprecated url', target_fixture='pds_url')
def use_deprecated_url() -> str:
    prNo = re.search("pr-[0-9]+", PDS_BASE_PATH)
    prString = f"-{prNo.group()}" if prNo is not None else ""
    return f"{BASE_URL}/personal-demographics{prString}"


@then(
    parsers.cfparse(
        "I get a {expected_status:Number} HTTP response",
        extra_types=dict(Number=int)
    )
)
def check_status(response: Response, expected_status: int) -> None:
    LOGGER.info(response.text)
    with check:
        assert response.status_code == expected_status


@then('the resposne body contains the sensitivity flag')
def response_body_contains_sensitivity_flag(response_body: str) -> None:
    value_in_response_body_at_path(response_body,
                                   'restricted',
                                   'str',
                                   'entry[0].resource.meta.security[0].display')


@then(
    parsers.cfparse(
        '{value:String} is {_:String} {type_convertor:String} at {path:String} in the response body',
        extra_types=dict(String=str)
    ))
def value_in_response_body_at_path(response_body: dict, value: str, type_convertor: str, path: str):
    matches = parse(path).find(response_body)
    with check:
        assert matches, f'There are no matches for {value} at {path} in the resposne body'
        for match in matches:
            assert match.value == eval(type_convertor)(value), \
                f'{match.value} is not the expected value, {value}, at {path}'


@then(
    parsers.cfparse(
        'the response body does not contain {field:String}',
        extra_types=dict(String=str)
    )
)
def response_body_does_not_contain(response_body: dict, field: str) -> None:
    assert field not in response_body


@then(
    parsers.cfparse(
        'the response header does not contain {field:String}',
        extra_types=dict(String=str)
    )
)
def response_header_does_not_contain(response: dict, field: str) -> None:
    assert field not in response.headers


@then("the response body contains the patient's new gender")
def new_gender(response_body: Response, update: Update) -> None:
    with check:
        assert response_body['gender'] == update.value


@then("the response body contains the record's new version number")
def version_incremented(response_body: Response, update: Update) -> None:
    with check:
        assert response_body["meta"]["versionId"] == str(int(update.record_version) + 1)
