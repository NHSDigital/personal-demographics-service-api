from pytest_check import check
from pytest_bdd import then, parsers
from jsonpath_rw import parse
from requests import Response
import os
import json
from tests.functional.data.patients import Patient
from tests.functional.data.searches import Search
from tests.functional.utils.helpers import is_key_in_dict
from tests.functional.conftest import RESPONSES_DIR


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
