import json
import pytest_bdd
from pytest_bdd import given, when, then, parsers
from functools import partial
from .data.pds_scenarios import retrieve, search as search_scenario
from .data.expected_errors import error_responses
from .data import patients
from .data.patients import Patient
from .data import searches
from .data.searches import Search
from .data import updates
from .data.updates import Update
from .utils import helpers
import pytest
from pytest_check import check
import logging
from .configuration.config import ENVIRONMENT, BASE_URL, PDS_BASE_PATH
from requests import Response, get, patch
import re
import urllib.parse
from jsonpath_rw import parse

LOGGER = logging.getLogger(__name__)

# TODO: Move this out?
AUTH_HEALTHCARE_WORKER = {
    "api_name": "personal-demographics-service",
    "access": "healthcare_worker",
    "level": "aal3",
    "login_form": {"username": "656005750104"},
    "force_new_token": True
}

IDENTITY_SERVICE_BASE_URL = "https://int.api.service.nhs.uk/oauth2-mock"

scenario = partial(pytest_bdd.scenario, './features/healthcare_worker_access.feature')
related_person_scenario = partial(pytest_bdd.scenario, './features/related_person.feature')
status_scenario = partial(pytest_bdd.scenario, './features/status_endpoints.feature')


@scenario('Healthcare worker can retrieve patient')
def test_retrieve_patient():
    pass


@scenario('Healthcare worker using deprecated url')
def test_retrieve_with_deprecated_url():
    pass


@scenario('Attempt to retrieve a patient with missing authorization header')
def test_retrieve_with_missing_auth():
    pass


@scenario('Attempt to retrieve a patient with an empty authorization header')
def test_retrieve_using_empty_auth():
    pass


@scenario('Attempt to retrieve a patient with an invalid authorization header')
def test_retrieve_using_invalid_auth():
    pass


@scenario('Attempt to retrieve a patient without stating a role')
def test_retrieve_with_missing_role():
    pass


@scenario('Attempt to retrieve a patient with an invalid role')
def test_retrieve_using_invalid_role():
    pass


@scenario('Attempt to retrieve a patient without Request ID header')
def test_retrieve_using_empty_request_id():
    pass


@scenario('Attempt to retrieve a patient with an invalid X-Request-ID')
def test_retrieve_using_invalid_request_id():
    pass


@scenario('Attempt to retrieve a patient with a missing X-Request-ID')
def test_retrieve_with_missing_request_id():
    pass


@scenario('Healthcare worker can search for patient')
def test_search_patient():
    pass


@scenario('Attempt to search for a patient with missing authorization header')
def test_search_with_missing_auth():
    pass


@scenario('Attempt to search for a patient with an empty authorization header')
def test_search_using_empty_auth():
    pass


@scenario('Attempt to search for a patient with an invalid authorization header')
def test_search_using_invalid_auth():
    pass


@scenario('Attempt to search for a patient with an empty Request ID header')
def test_search_using_empty_request_id():
    pass


@scenario('Attempt to search for a patient with an invalid X-Request-ID')
def test_search_using_invalid_request_id():
    pass


@scenario('Attempt to search for a patient with a missing X-Request-ID')
def test_search_with_missing_request_id():
    pass


@scenario('Healthcare worker searches for sensitive patient')
def test_search_sensitive_patient():
    pass


@scenario('Healthcare worker searches for patient without specifying gender')
def test_search_gender_free():
    pass


@scenario('Healthcare worker searches for a patient with range for date of birth')
def test_search_with_dob_range():
    pass


@scenario('Searching without gender can return mutliple results')
def test_search_with_vauge_details():
    pass


@scenario('Searching with fuzzy match')
def test_search_with_fuzzy_match():
    pass


@scenario('Searching with unicode returns unicode record')
def test_search_with_unicode():
    pass


@scenario('Searching with specified results limit can return error')
def test_search_returns_error_due_to_results_limit():
    pass


@scenario('Update patient')
def test_update_patient():
    pass


@scenario('Update patient using deprecated respond-async still returns 200')
def test_update_patient_with_deprecated_header():
    pass


@scenario('Update patient with invalid wait header still updates')
def test_update_with_invalid_wait():
    pass


@scenario('Update patient with low wait header')
def test_update_with_low_wait():
    pass


@scenario('Update patient with missing Authorization header')
def test_update_with_missing_auth():
    pass


@scenario('Update patient with an empty authorization header')
def test_update_with_empty_auth():
    pass


@scenario('Update patient with an invalid authorization header')
def test_update_using_invalid_auth():
    pass


@scenario('Update patient with an empty Request ID header')
def test_update_using_empty_request_id():
    pass


@scenario('Update patient with an invalid X-Request-ID')
def test_update_using_invalid_request_id():
    pass


@scenario('Update patient with a missing X-Request-ID')
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


@pytest.fixture()
def pds_url() -> str:
    return f"{BASE_URL}/{PDS_BASE_PATH}"


@pytest.fixture()
def patient() -> Patient:
    return patients.DEFAULT


@given('I have a patient with a related person', target_fixture='patient')
def patient_with_a_related_person() -> Patient:
    return patients.WITH_RELATED_PERSON


@given("I have a patient's demographic details", target_fixture='search')
def search() -> Search:
    return searches.DEFAULT


@pytest.fixture()
def update() -> Update:
    return updates.DEFAULT


@given("I have a sensitive patient's demographic details", target_fixture='search')
def search_for_sensitive() -> Patient:
    return searches.SENSITIVE


@given("I have a patient's demographic details without gender", target_fixture='search')
def search_without_gender() -> Patient:
    return searches.UNKNOWN_GENDER


@given("I have a patient's demographic details with a date of birth range", target_fixture='search')
def search_dob_range() -> Patient:
    return searches.DOB_RANGE


@given("I enter a patient's vague demographic details", target_fixture='search')
def vague_patient() -> Search:
    return searches.VAGUE


@given("I enter a patient's fuzzy demographic details", target_fixture='search')
def fuzzy_search() -> Search:
    return searches.FUZZY


@given("I enter a patient's unicode demographic details", target_fixture='search')
def unicode_search() -> Search:
    return searches.UNICODE


@pytest.fixture()
def nhs_number(patient: Patient) -> str:
    return patient.nhs_number


@given("I have a patient's record to update", target_fixture='record_to_update')
def record_to_update(update: Update, headers_with_authorization: dict, pds_url: str) -> dict:
    response = retrieve_patient(headers_with_authorization, update.nhs_number, pds_url)

    update.record_to_update = json.loads(response.text)
    update.etag = response.headers['Etag']

    return update.record_to_update


@pytest.fixture()
def query_params(search: Search) -> str:
    return urllib.parse.urlencode(search.query)


@when(
    parsers.cfparse(
        'the query parameters contain {key:String} as {value:String}',
        extra_types=dict(String=str)
    ),
    target_fixture='query_params'
)
def amended_query_params(search: Search, key: str, value: str) -> str:
    query_params = search.query
    query_params.append((key, value))
    return urllib.parse.urlencode(query_params)


@given("I am a healthcare worker")
def provide_healthcare_worker_auth_details(request) -> None:
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER))


@given("I am an unknown user", target_fixture='headers_with_authorization')
def provide_headers_with_no_auth_details() -> None:
    return {}


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
        "I have an empty {field:String} header",
        extra_types=dict(String=str)
    ),
    target_fixture='headers_with_authorization')
def empty_header(headers_with_authorization: dict, field: str) -> dict:
    headers_with_authorization.update({field: ''})
    return headers_with_authorization


@given(
    parsers.cfparse(
        'I have a header {field:String} value of "{value:String}"',
        extra_types=dict(String=str)
    ),
    target_fixture='headers_with_authorization')
def invalid_header(headers_with_authorization: dict, field: str, value: str) -> dict:
    headers_with_authorization.update({field: value})
    return headers_with_authorization


@given("I wish to update the patient's gender")
def add_new_gender_to_patch(update: Update) -> None:
    current_gender = update.record_to_update['gender']
    new_gender = 'male' if current_gender == 'female' else 'female'
    update.value = new_gender


@given('I am using the deprecated url', target_fixture='pds_url')
def use_deprecated_url() -> str:
    prNo = re.search("pr-[0-9]+", PDS_BASE_PATH)
    prString = f"-{prNo.group()}" if prNo is not None else ""
    return f"{BASE_URL}/personal-demographics{prString}"


@when('I retrieve a patient', target_fixture='response')
def retrieve_patient(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}", headers=headers_with_authorization)


@when('I retrieve their related person', target_fixture='response')
def retrieve_related_person(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}/RelatedPerson", headers=headers_with_authorization)


@when("I search for the patient's PDS record", target_fixture='response')
def search_patient(headers_with_authorization: dict, query_params: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient?{query_params}", headers=headers_with_authorization)


@when("I update the patient's PDS record", target_fixture='response')
def update_patient(headers_with_authorization: dict, update: Update, pds_url: str) -> Response:
    headers = headers_with_authorization
    headers.update({
        "Content-Type": "application/json-patch+json",
        "If-Match": update.etag,
    })
    return patch(url=f"{pds_url}/Patient/{update.nhs_number}",
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


@pytest.fixture()
def response_body(response: Response) -> dict:
    response_body = json.loads(response.text)
    if "timestamp" in response_body:
        response_body.pop("timestamp")
    return response_body


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
    # TODO: this should probably be refactored
    if 'entry' in response_body:
        response_body = response_body['entry'][0]['resource']

    with check:
        assert response_body["id"] == nhs_number
        assert response_body["resourceType"] == "Patient"


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


@then(
    parsers.cfparse(
        'the response body is the {error:String} response',
        extra_types=dict(String=str)
    )
)
def resposne_body_contains_error(response_body: dict, error) -> None:
    assert response_body == error_responses[error]


@then('the response body contains the expected response')
def response_body_as_expected(response_body: dict, patient: Patient) -> None:
    assert response_body == patient.expected_response


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


@then("the response body contains the patient's new gender")
def new_gender(response_body: Response, update: Update) -> None:
    with check:
        assert response_body['gender'] == update.value


@then("the response body contains the record's new version number")
def version_incremented(response_body: Response, update: Update) -> None:
    with check:
        assert response_body["meta"]["versionId"] == str(int(update.record_version) + 1)


@then('the response body contains the expected values')
def check_expected_search_response_body(response_body: dict, search: Search) -> None:
    with check:
        for field in search.expected_response_fields:
            matches = parse(field.path).find(response_body)
            assert matches, f'There are no matches for {field.expected_value} at {field.path} in the resposne body'
            for match in matches:
                assert match.value == field.expected_value,\
                    f'{field.path} in response does not contain the expected value, {field.expected_value}'


class TestUserRestrictedRetrievePatientOld:

    # TODO: Do we beed to implement this?s
    def test_setup(self, add_proxies_to_products_user_restricted):
        LOGGER.info("Setting up the products and proxies for testing")

    # test_deprecated_url
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_deprecated_url(self, headers_with_token):
    #     response = helpers.retrieve_patient_deprecated_url(
    #         retrieve[0]["patient"],
    #         self.headers
    #     )

    #     helpers.check_response_status_code(response, 404)

    # TODO: Reimplement this!
    @pytest.mark.smoke_test
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    @pytest.mark.skipif(ENVIRONMENT != 'int', reason="INT can only use pre-built test app")
    def test_retrieve_patient_for_int(self,
                                      apigee_environment,
                                      nhsd_apim_config,
                                      _test_app_credentials):
        headers = helpers.get_headers(apigee_environment,
                                      nhsd_apim_config,
                                      _test_app_credentials,
                                      AUTH_HEALTHCARE_WORKER)
        self.retrieve_patient_and_assert(retrieve[0], headers)

    # test_retrieve_patient
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_patient_for_non_int(self, headers_with_token):
    #     self.retrieve_patient_and_assert(retrieve[0], self.headers)

    def retrieve_patient_and_assert(self, patient: dict, headers):
        response = helpers.retrieve_patient(
            retrieve[0]["patient"],
            headers
        )

        helpers.check_response_headers(response, headers)
        helpers.check_response_status_code(response, 200)
        helpers.check_retrieve_response_body_shape(response)

    # test_missing_auth
    # def test_retrieve_patient_with_missing_auth_header(self, headers):
    #     response = helpers.retrieve_patient(
    #         retrieve[1]["patient"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[1]["response"])
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, headers)

    # test_empty_auth
    # def test_retrieve_patient_with_blank_auth_header(self, headers):
    #     headers['authorization'] = ''
    #     response = helpers.retrieve_patient(
    #         retrieve[2]["patient"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(
    #         response,
    #         retrieve[2]["response"]
    #     )
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, headers)

    # test_invalid_auth
    # def test_retrieve_patient_with_invalid_auth_header(self, headers):
    #     headers['authorization'] = 'Bearer abcdef123456789'
    #     response = helpers.retrieve_patient(
    #         retrieve[3]["patient"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[3]["response"])
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, headers)

    # test_missing_role
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_user_role_sharedflow_retrieve_patient_with_missing_urid_header(self, headers_with_authorization):
    #     headers = headers_with_authorization
    #     headers.pop("NHSD-Session-URID")
    #     LOGGER.info(f'headers: {headers}')
    #     response = helpers.retrieve_patient(
    #         retrieve[10]["patient"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[10]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     helpers.check_response_headers(response, headers)

    # test_invalid_role
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_user_role_sharedflow_invalid_role(self, headers_with_token):
    #     self.headers["NHSD-Session-URID"] = "invalid"
    #     response = helpers.retrieve_patient(
    #         retrieve[9]["patient"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[9]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     helpers.check_response_headers(response, self.headers)

    # test_empty_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_patient_with_blank_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = ''
    #     response = helpers.retrieve_patient(
    #         retrieve[5]["patient"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[5]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     self.headers.pop("X-Request-ID")
    #     helpers.check_response_headers(response, self.headers)

    # test_invalid_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_patient_with_invalid_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = '1234'
    #     response = helpers.retrieve_patient(
    #         retrieve[6]["patient"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[6]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     helpers.check_response_headers(response, self.headers)

    # test_missing_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_patient_with_missing_x_request_header(self, headers_with_token):
    #     self.headers.pop("X-Request-ID")
    #     response = helpers.retrieve_patient(
    #         retrieve[7]["patient"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(response, retrieve[7]["response"])
    #     helpers.check_response_status_code(response, 412)
    #     helpers.check_response_headers(response, self.headers)


class TestUserRestrictedSearchPatient:

    # test_search_patient
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_happy_path_for_non_int(self, headers_with_token):
    #     self.search_patient_and_assert(self.headers)

    # TODO: this need reimplementing
    @pytest.mark.smoke_test
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    @pytest.mark.skipif(ENVIRONMENT != 'int', reason="INT can only use pre-built test app")
    def test_search_patient_happy_path_for_int(self, apigee_environment, nhsd_apim_config, _test_app_credentials):
        headers = helpers.get_headers(apigee_environment,
                                      nhsd_apim_config,
                                      _test_app_credentials,
                                      AUTH_HEALTHCARE_WORKER)
        self.search_patient_and_assert(headers)

    def search_patient_and_assert(self, headers):
        response = helpers.search_patient(
            search[0]["query_params"],
            headers
        )
        helpers.check_response_status_code(response, 200)
        helpers.assert_correct_patient_nhs_number_is_returned(response, search[0]["patient_returned"])
        helpers.check_response_headers(response, headers)

    # test_search_with_missing_auth
    # def test_search_patient_with_missing_auth_header(self, headers):
    #     response = helpers.search_patient(
    #         search[1]["query_params"],
    #         headers
    #     )
    #     helpers.check_search_response_body(response, search[1]["response"])
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, headers)

    # Duplicate of test below, test_search_using_empty_auth
    def test_search_patient_with_blank_auth_header(self, headers):
        headers['authorization'] = ''
        response = helpers.search_patient(
            search_scenario[2]["query_params"],
            headers
        )
        helpers.check_search_response_body(response, search_scenario[2]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    # test_search_using_empty_auth
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_with_blank_auth_header_at(self, headers_with_token):
    #     self.headers['authorization'] = ''
    #     response = helpers.search_patient(
    #         search[2]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_search_response_body(response, search[2]["response"])
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, self.headers)

    # test_search_using_invalid_auth
    # def test_search_patient_with_invalid_auth_header(self, headers):
    #     headers['authorization'] = 'Bearer abcdef123456789'
    #     response = helpers.search_patient(
    #         search[3]["query_params"],
    #         headers
    #     )
    #     helpers.check_search_response_body(response, search[3]["response"])
    #     helpers.check_response_status_code(response, 401)
    #     helpers.check_response_headers(response, headers)

    # test_search_using_empty_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_with_blank_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = ''
    #     response = helpers.search_patient(
    #         search[5]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_search_response_body(response, search[5]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     self.headers.pop("X-Request-ID")
    #     helpers.check_response_headers(response, self.headers)

    # test_search_using_invalid_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_with_invalid_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = '1234'
    #     response = helpers.search_patient(
    #         search[6]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_search_response_body(response, search[6]["response"])
    #     helpers.check_response_status_code(response, 400)
    #     helpers.check_response_headers(response, self.headers)

    # test_search_with_missing_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_with_missing_x_request_header(self, headers_with_token):
    #     self.headers.pop("X-Request-ID")
    #     response = helpers.search_patient(
    #         search[7]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_search_response_body(response, search[7]["response"])
    #     helpers.check_response_status_code(response, 412)
    #     helpers.check_response_headers(response, self.headers)

    # test_search_sensitive_patient
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_happy_path_sensitive(self, headers_with_token):
    #     response = helpers.search_patient(
    #         search[10]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_response_status_code(response, 200)
    #     helpers.assert_correct_patient_nhs_number_is_returned(response, search[10]["patient_returned"])
    #     helpers.assert_is_sensitive_patient(response)
    #     helpers.check_response_headers(response, self.headers)

    # test_search_gender_free
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_patient_happy_path_gender_free(self, headers_with_token):
    #     response = helpers.search_patient(
    #         search[8]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_response_status_code(response, 200)
    #     helpers.assert_correct_patient_nhs_number_is_returned(response, search[8]["patient_returned"])
    #     helpers.check_response_headers(response, self.headers)

    # test_search_with_dob_range
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_search_advanced_alphanumeric_gender_free(self, headers_with_token):
    #     response = helpers.search_patient(
    #         search[9]["query_params"],
    #         self.headers
    #     )
    #     helpers.check_response_status_code(response, 200)
    #     helpers.assert_correct_patient_nhs_number_is_returned(response, search[9]["patient_returned"])
    #     helpers.check_response_headers(response, self.headers)

    # TODO: Does this need implementing? Is this not the same as the test above?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_simple_trace_no_gender(self, headers_with_token):
        """See TestBase37101 Chain 7001"""
        print(self.headers)
        response = helpers.search_patient(
            {"family": "Garton", "birthdate": "1946-06-23"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["resourceType"] == "Bundle"
        assert response_body["type"] == "searchset"
        assert response_body["total"] == 1
        assert response_body["entry"][0]["resource"]["id"] == "9693632109"

    # TODO: Is this necessary?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_simple_trace_no_gender_no_result(self, headers_with_token):
        """See TestBase37101 Chain 7002"""
        print(self.headers)
        response = helpers.search_patient(
            {"family": "Garton", "birthdate": "1947-06-23"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["resourceType"] == "Bundle"
        assert response_body["type"] == "searchset"
        assert response_body["total"] == 0

    # TODO: How to implement?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_no_gender_postcode_format_doesnt_affect_score(self, headers_with_token):
        """See TestBase37101 Chain 7003"""
        response_1 = helpers.search_patient(
            {"family": "Garton", "birthdate": "1946-06-23", "address-postcode": "DN18 5DW"},
            self.headers
        )
        response_1_body = response_1.json()

        response_2 = helpers.search_patient(
            {"family": "Garton", "birthdate": "1946-06-23", "address-postcode": "dn185dw"},
            self.headers
        )
        response_2_body = response_2.json()

        assert response_1.status_code == 200
        assert response_2.status_code == response_1.status_code
        assert response_1_body["entry"][0]["resource"]["id"] == "9693632109"
        assert response_1_body["entry"][0]["resource"]["id"] == response_2_body["entry"][0]["resource"]["id"]
        assert response_1_body["entry"][0]["search"]["score"] == 1
        assert response_1_body["entry"][0]["search"]["score"] == response_2_body["entry"][0]["search"]["score"]

    # test_search_with_vauge_details
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_algorithmic_search_without_gender(self, headers_with_token):
    #     """See TestBase37102 Chain 7001"""
    #     response = helpers.search_patient(
    #         {"family": "YOUDS", "birthdate": "1970-01-24"},
    #         self.headers
    #     )
    #     response_body = response.json()
    #     LOGGER.info(f'response_body: {response_body}')

    #     assert response.status_code == 200
    #     assert response_body["type"] == "searchset"
    #     assert response_body["resourceType"] == "Bundle"
    #     assert response_body["total"] == 4
    #     assert response_body["entry"][0]["search"]["score"] == 1
    #     assert response_body["entry"][0]["resource"]["id"] == "9693633679"
    #     assert response_body["entry"][0]["resource"]["gender"] == "male"
    #     assert response_body["entry"][0]["resource"]["birthDate"] == "1970-01-24"
    #     assert response_body["entry"][1]["search"]["score"] == 1
    #     assert response_body["entry"][1]["resource"]["id"] == "9693633687"
    #     assert response_body["entry"][1]["resource"]["gender"] == "female"
    #     assert response_body["entry"][1]["resource"]["birthDate"] == "1970-01-24"
    #     assert response_body["entry"][2]["search"]["score"] == 1
    #     assert response_body["entry"][2]["resource"]["id"] == "9693633695"
    #     assert response_body["entry"][2]["resource"]["gender"] == "unknown"
    #     assert response_body["entry"][2]["resource"]["birthDate"] == "1970-01-24"
    #     assert response_body["entry"][3]["search"]["score"] == 1
    #     assert response_body["entry"][3]["resource"]["id"] == "9693633709"
    #     assert response_body["entry"][3]["resource"]["gender"] == "other"
    #     assert response_body["entry"][3]["resource"]["birthDate"] == "1970-01-24"

    # test_search_with_fuzzy_match
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_algorithmic_fuzzy_match_unknown_gender(self, headers_with_token):
    #     """See TestBase37104 Chain 0001"""
    #     response = helpers.search_patient(
    #         {"family": "Garton", "given": "Bill", "birthdate": "1946-06-23", "_fuzzy-match": "true"},
    #         self.headers
    #     )
    #     response_body = response.json()

    #     assert response.status_code == 200
    #     assert response_body["type"] == "searchset"
    #     assert response_body["resourceType"] == "Bundle"
    #     assert response_body["entry"][0]["search"]["score"] == 1
    #     assert response_body["entry"][0]["resource"]["id"] == "9693632109"

    # test_search_with_unicode
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_algorithmic_fuzzy_match_unicode(self, headers_with_token):
    #     """See TestBase37104 Chain 0007"""
    #     response = helpers.search_patient(
    #         {"family": "ATTSÖN", "given": "PÀULINÉ", "birthdate": "1960-07-14", "_fuzzy-match": "true"},
    #         self.headers
    #     )
    #     response_body = response.json()

    #     assert response.status_code == 200
    #     assert response_body["type"] == "searchset"
    #     assert response_body["resourceType"] == "Bundle"
    #     assert response_body["entry"][0]["search"]["score"] == 0.9317
    #     assert response_body["entry"][0]["resource"]["id"] == "9693633148"
    #     assert response_body["entry"][0]["resource"]["gender"] == "female"
    #     assert response_body["entry"][0]["resource"]["birthDate"] == "1960-07-14"
    #     assert response_body["entry"][0]["resource"]["name"][0]["family"] == "attisón"
    #     assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == "Pauline"
    #     assert response_body["entry"][1]["search"]["score"] == 0.9077
    #     assert response_body["entry"][1]["resource"]["id"] == "9693633121"
    #     assert response_body["entry"][1]["resource"]["gender"] == "female"
    #     assert response_body["entry"][1]["resource"]["birthDate"] == "1960-07-14"

    # TODO: Is this necessary? These tests are not for end-to-end tests.
    # It is already shown that the proxy handles unicode. What is there to gain from this test?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_algorithmic_fuzzy_match_regular_returns_unicode(self, headers_with_token):
        """See TestBase37104 Chain 0008"""
        response = helpers.search_patient(
            {"family": "ATTSON", "given": "PAULINE", "birthdate": "1960-07-14", "_fuzzy-match": "true"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9889
        assert response_body["entry"][0]["resource"]["id"] == "9693633121"
        assert response_body["entry"][0]["resource"]["gender"] == "female"
        assert response_body["entry"][0]["resource"]["birthDate"] == "1960-07-14"
        assert response_body["entry"][0]["resource"]["name"][0]["family"] == "attison"
        assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == "Pauline"
        assert response_body["entry"][1]["search"]["score"] == 0.9648
        assert response_body["entry"][1]["resource"]["id"] == "9693633148"
        assert response_body["entry"][1]["resource"]["gender"] == "female"
        assert response_body["entry"][1]["resource"]["birthDate"] == "1960-07-14"

    # TODO: Is this necessary?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_algorithmic_fuzzy_match_for_birthdate_range(self, headers_with_token):
        """See TestBase37104 Chain 0009"""
        response = helpers.search_patient(
            "family=Garton&given=Bill&birthdate=le1990-01-01&birthdate=ge1946-01-19&_fuzzy-match=true",
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 1
        assert response_body["entry"][0]["resource"]["id"] == "9693632109"

    # TODO: Why is this fuzzy and exact?
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_algorithmic_exact_match_requested_but_not_found(self, headers_with_token):
        """See TestBase37105 Chain 0003"""
        response = helpers.search_patient(
            {
                "family": "PÀTSÖN", "given": "PÀULINÉ", "birthdate": "1979-07-27",
                "_fuzzy-match": "true", "_exact-match": "true"
            },
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["total"] == 0

    # TODO: What is this testing? Only two come back from search (having looked at full response)
    # We know that multiple resources can come back.
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_algorithmic_requesting_50_results(self, headers_with_token):
        """See TestBase37107 Chain 0004"""
        response = helpers.search_patient(
            {
                "family": "ATTSON", "given": "PAULINE", "birthdate": "1960-07-14",
                "_fuzzy-match": "true", "_max-results": "50"
            },
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9889
        assert response_body["entry"][0]["resource"]["id"] == "9693633121"
        assert response_body["entry"][1]["search"]["score"] == 0.9648

    # test_search_returns_error_due_to_results_limit
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_algorithmic_requesting_1_result_too_many_matches(self, headers_with_token):
        """See TestBase37107 Chain 0008"""
        response = helpers.search_patient(
            {
                "family": "Beever", "gender": "female", "birthdate": "ge1977-07-27", "_max-results": "1"
            },
            self.headers
        )
        response_body = response.json()
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "TOO_MANY_MATCHES"
        assert response_body["issue"][0]["details"]["coding"][0]["display"] == "Too Many Matches"

    # TODO: Is this necessary? Check this spine-side.
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_simple_search_family_name_still_required(self, headers_with_token):
        response = helpers.search_patient(
            {"given": "PAULINE", "birthdate": "1979-07-27"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 400
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"

    # TODO: Is this necessary? Check this spine-side.
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_simple_search_birthdate_still_required(self, headers_with_token):
        response = helpers.search_patient(
            {"family": "PATSON", "given": "PAULINE"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 400
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "MISSING_VALUE"

    # TODO: Is this necessary? Check this spine-side.
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    def test_search_for_similar_patient_different_genders(self, headers_with_token):
        """Performing a gender-free search where there exists four patients with the same
        name and date of birth, but differing gender values, should return multiple distinct results."""

        family = "YOUDS"
        given = "Luke"
        birth_date = "1970-01-24"

        genders = ['male', 'female', 'unknown', 'other']
        patient_ids = ['9693633679', '9693633687', '9693633695', '9693633709']

        # Do the individual items exist and can be retrieved with a gendered search?
        for i, gender in enumerate(genders):
            patient_id = patient_ids[i]
            response = helpers.search_patient(
                {"family": family, "given": given, "birthdate": birth_date, "gender": gender},
                self.headers
            )
            response_body = response.json()

            assert response.status_code == 200
            assert response_body["type"] == "searchset"
            assert response_body["resourceType"] == "Bundle"
            assert response_body["total"] == 1
            assert response_body["entry"][0]["resource"]["id"] == patient_id
            assert response_body["entry"][0]["resource"]["gender"] == gender
            assert response_body["entry"][0]["resource"]["name"][0]["family"] == family
            assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == given

        # Then retrieve and check for all of them with a genderless search
        response_all = helpers.search_patient(
            {"family": family, "given": given, "birthdate": birth_date},
            self.headers
        )
        response_all_body = response_all.json()

        assert response_all.status_code == 200
        assert response_all_body["type"] == "searchset"
        assert response_all_body["resourceType"] == "Bundle"
        assert response_all_body["total"] == 4

        # Order of search results is not guaranteed.
        # We will enumerate each one and make sure
        # it is unique and expected (ie from our genders,
        # and patient_ids lists)
        checked_results_count = 0
        for result in response_all_body["entry"]:
            i = genders.index(result["resource"]["gender"])
            patient_id, gender = patient_ids.pop(i), genders.pop(i)

            assert result["resource"]["id"] == patient_id
            assert result["resource"]["gender"] == gender
            assert result["resource"]["name"][0]["family"] == family
            assert result["resource"]["name"][0]["given"][0] == given

            checked_results_count += 1
        assert checked_results_count == 4


# class TestUserRestrictedPatientUpdateSyncWrap:
    # test_update_patient / test_update_patient_with_deprecated_header
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_gender(self, headers_with_token):
    #     #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
    #     response = helpers.retrieve_patient(
    #         update_scenario[0]["patient"],
    #         self.headers
    #     )
    #     patient_record = response.headers["Etag"]
    #     versionId = (json.loads(response.text))["meta"]["versionId"]

    #     current_gender = (json.loads(response.text))["gender"]
    #     new_gender = 'male' if current_gender == 'female' else 'female'

    #     # add the new gender to the patch, send the update and check the response
    #     update_scenario[0]["patch"]["patches"][0]["value"] = new_gender
    #     self.headers["X-Sync-Wait"] = "29"

    #     # Prefer header deprecated check that it still returns 200 response
    #     self.headers["Prefer"] = "respond-async"

    #     update_response = helpers.update_patient(
    #         update_scenario[0]["patient"],
    #         patient_record,
    #         update_scenario[0]["patch"],
    #         self.headers
    #     )
    #     with check:
    #         assert (json.loads(update_response.text))["gender"] == new_gender
    #     with check:
    #         assert int((json.loads(update_response.text))["meta"]["versionId"]) == int(versionId) + 1
    #     helpers.check_response_status_code(update_response, 200)

    # test_update_with_invalid_wait
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_gender_with_invalid_x_sync_wait_header(self, headers_with_token):
    #     #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
    #     def retrieve_patient():
    #         response = helpers.retrieve_patient(
    #             update_scenario[0]["patient"],
    #             self.headers
    #         )
    #         return response

    #     response = retrieve_patient()

    #     patient_record = response.headers["Etag"]
    #     versionId = (json.loads(response.text))["meta"]["versionId"]

    #     current_gender = (json.loads(response.text))["gender"]
    #     new_gender = 'male' if current_gender == 'female' else 'female'

    #     update_scenario[0]["patch"]["patches"][0]["value"] = new_gender

    #     self.headers["X-Sync-Wait"] = "invalid"

    #     update_response = helpers.update_patient(
    #         update_scenario[0]["patient"],
    #         patient_record,
    #         update_scenario[0]["patch"],
    #         self.headers
    #     )

    #     def assert_update_response(update_response):
    #         with check:
    #             assert (json.loads(update_response.text))["gender"] == new_gender
    #         with check:
    #             assert int((json.loads(update_response.text))["meta"]["versionId"]) == int(versionId) + 1
    #         helpers.check_response_status_code(update_response, 200)

    #     if update_response.status_code == 503 and json.loads(
    #             update_response.text, strict=False)["issue"][0]["code"] == "timeout":
    #         """
    #             Temp fix due to slow VEIT07 env causing update to exceed default X-Sync-Wait timeout of 10s.
    #             If the update times out retrieve the patient instead and check if the record has been updated.
    #         """
    #         retrieve_response = retrieve_patient()
    #         assert_update_response(retrieve_response)
    #     else:
    #         assert_update_response(update_response)

    # test_update_with_low_wait
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_gender_with_low_sync_wait_timeout(self, headers_with_token):
    #     #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
    #     response = helpers.retrieve_patient(
    #         update_scenario[0]["patient"],
    #         self.headers
    #     )
    #     patient_record = response.headers["Etag"]

    #     current_gender = (json.loads(response.text))["gender"]
    #     new_gender = 'male' if current_gender == 'female' else 'female'

    #     update_scenario[0]["patch"]["patches"][0]["value"] = new_gender

    #     self.headers["X-Sync-Wait"] = "0.25"
    #     update_response = helpers.update_patient(
    #         update_scenario[0]["patient"],
    #         patient_record,
    #         update_scenario[0]["patch"],
    #         self.headers
    #     )

    #     helpers.check_response_status_code(update_response, 503)

    # test_update_with_missing_auth
    # def test_update_patient_with_missing_auth_header(self, headers):
    #     update_response = helpers.update_patient(
    #         update_scenario[1]["patient"],
    #         'W/"14"',
    #         update_scenario[1]["patch"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[1]["response"])
    #     helpers.check_response_status_code(update_response, 401)
    #     helpers.check_response_headers(update_response, headers)

    # test_update_with_empty_auth
    # def test_update_patient_with_blank_auth_header(self, headers):
    #     headers['authorization'] = ''
    #     update_response = helpers.update_patient(
    #         update_scenario[2]["patient"],
    #         'W/"14"',
    #         update_scenario[2]["patch"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[2]["response"])
    #     helpers.check_response_status_code(update_response, 401)
    #     helpers.check_response_headers(update_response, headers)

    # test_update_using_invalid_auth
    # def test_update_patient_with_invalid_auth_header(self, headers):
    #     headers['authorization'] = 'Bearer abcdef123456789'
    #     update_response = helpers.update_patient(
    #         update_scenario[3]["patient"],
    #         'W/"14"',
    #         update_scenario[3]["patch"],
    #         headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[3]["response"])
    #     helpers.check_response_status_code(update_response, 401)
    #     helpers.check_response_headers(update_response, headers)

    # test_update_using_empty_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_with_blank_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = ''
    #     update_response = helpers.update_patient(
    #         update_scenario[5]["patient"],
    #         'W/"14"',
    #         update_scenario[5]["patch"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[5]["response"])
    #     helpers.check_response_status_code(update_response, 400)
    #     self.headers.pop("X-Request-ID")
    #     helpers.check_response_headers(update_response, self.headers)

    # test_update_using_invalid_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_with_invalid_x_request_header(self, headers_with_token):
    #     self.headers["X-Request-ID"] = '1234'
    #     update_response = helpers.update_patient(
    #         update_scenario[6]["patient"],
    #         'W/"14"',
    #         update_scenario[6]["patch"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[6]["response"])
    #     helpers.check_response_status_code(update_response, 400)
    #     helpers.check_response_headers(update_response, self.headers)

    # test_update_with_missing_request_id
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_update_patient_with_missing_x_request_header(self, headers_with_token):
    #     self.headers.pop("X-Request-ID")
    #     update_response = helpers.update_patient(
    #         update_scenario[7]["patient"],
    #         'W/"14"',
    #         update_scenario[7]["patch"],
    #         self.headers
    #     )
    #     helpers.check_retrieve_response_body(update_response, update_scenario[7]["response"])
    #     helpers.check_response_status_code(update_response, 412)
    #     helpers.check_response_headers(update_response, self.headers)


class TestUserRestrictedRetrieveRelatedPerson:

    # test_retrieve_related_person
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_retrieve_related_person_for_non_int(self, headers_with_token):
    #     self.retrieve_patient_and_assert(retrieve[8], self.headers)

    @pytest.mark.smoke_test
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    @pytest.mark.skipif(ENVIRONMENT != 'int', reason="INT can only use pre-built test app")
    def test_retrieve_related_person_for_int(self,
                                             apigee_environment,
                                             nhsd_apim_config,
                                             _test_app_credentials,):
        headers = helpers.get_headers(apigee_environment,
                                      nhsd_apim_config,
                                      _test_app_credentials,
                                      AUTH_HEALTHCARE_WORKER)
        self.retrieve_patient_and_assert(retrieve[8], headers)

    def retrieve_patient_and_assert(self, patient: dict, headers: dict):
        response = helpers.retrieve_patient_related_person(
            patient["patient"],
            headers
        )
        helpers.check_retrieve_related_person_response_body(response, patient["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, headers)


class TestStatusEndpoints:

    # test_ping
    # @pytest.mark.smoke_test
    # def test_ping_endpoint(self):
    #     response = helpers.ping_request()
    #     helpers.check_response_status_code(response, 200)

    # test_healthcheck
    # @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    # def test_health_check_endpoint_for_non_int(self, headers_with_token):
    #     response = helpers.check_health_check_endpoint(self.headers)
    #     helpers.check_response_status_code(response, 200)

    @pytest.mark.smoke_test
    @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
    @pytest.mark.skipif(ENVIRONMENT != 'int', reason="INT can only use pre-built test app")
    def test_health_check_endpoint_for_int(self,
                                           apigee_environment,
                                           nhsd_apim_config,
                                           _test_app_credentials):
        headers = helpers.get_headers(apigee_environment,
                                      nhsd_apim_config,
                                      _test_app_credentials,
                                      AUTH_HEALTHCARE_WORKER)
        response = helpers.check_health_check_endpoint(headers)
        helpers.check_response_status_code(response, 200)
