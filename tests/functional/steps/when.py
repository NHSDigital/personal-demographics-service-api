from pytest_bdd import when, parsers
from requests import Response, get, patch
from tests.functional.data.updates import Update
from tests.functional.data.searches import Search
from copy import copy
import urllib


@when('I retrieve my details', target_fixture='response')
@when('I retrieve a patient', target_fixture='response')
def retrieve_patient(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}", headers=headers_with_authorization)


@when(
    parsers.cfparse(
        "I retrieve {_:String} related person",
        extra_types=dict(String=str)
    ),
    target_fixture='response'
)
def retrieve_related_person(headers_with_authorization: dict, nhs_number: str, pds_url: str) -> Response:
    return get(url=f"{pds_url}/Patient/{nhs_number}/RelatedPerson", headers=headers_with_authorization)


@when("I update the patient's PDS record", target_fixture='response')
@when("I update another patient's PDS record", target_fixture='response')
@when("I update my PDS record", target_fixture='response')
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


@when("I sign in using NHS login", target_fixture="response")
def nhs_login(nhs_login_sign_in) -> Response:
    return nhs_login_sign_in
