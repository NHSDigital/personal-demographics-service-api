from pytest_bdd import when, parsers
from requests import Response, get


@when('I retrieve my details', target_fixture='response')
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


@when("I sign in using NHS login", target_fixture="response")
def nhs_login(nhs_login_sign_in) -> Response:
    return nhs_login_sign_in
