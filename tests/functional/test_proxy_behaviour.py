from enum import Enum
from tests.functional.conftest import set_quota_and_rate_limit
import pytest
import requests
from polling2 import poll, TimeoutException
from http import HTTPStatus
from tests.scripts.pds_request import GenericPdsRequestor
from pytest_bdd import scenario, given, when, then, parsers
from .config_files.config import BASE_URL, PDS_BASE_PATH


class HTTPMethods(Enum):
    GET = "GET"
    PATCH = "PATCH"


def _trip_rate_limit(token: str, req_type: HTTPMethods, timeout: int = 30, step: int = 0.5) -> requests.Response:
    """Trips the spike arrest policy and returns the response.

    Args:
        token (str): OAuth access token.
        req_type(HTTPMethods): HTTP Method to send
        timeout(int): Timeout to trip rate_limit
        step(int): time between requests

    Returns:
        response (requests.Response): HTTP Response.
    """
    pds = GenericPdsRequestor(
        pds_base_path=PDS_BASE_PATH,
        base_url=BASE_URL,
        token=token,
    )
    # Set Etag for all requests
    if req_type == HTTPMethods.PATCH:
        patient = pds.get_patient_response(patient_id='9693632176')
        pds.headers = {
            "If-Match": patient.headers["Etag"] if patient.headers.get("Etag") else "W/22",
        }

    def _pds_response():

        if req_type == HTTPMethods.GET:
            response = pds.get_patient_response(patient_id='9693632176')
        if req_type == HTTPMethods.PATCH:
            response = pds.update_patient_response(
                patient_id='9693632176',
                payload={"patches": [{"op": "replace", "path": "/birthDate", "value": "2001-01-01"}]}
            )
        return response

    def _check_correct_response(response):
        """ Check that the response has tripped rate_limit"""
        return response.status_code == 429

    try:
        response = poll(lambda: _pds_response(), timeout=timeout, step=step, check_success=_check_correct_response)
        return response
    except TimeoutException:
        assert False, "Timeout Error: Rate limit wasn't tripped within set timeout"


@pytest.mark.happy_path
@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@scenario('./features/proxy_behaviour.feature', 'API Proxy rate limit tripped')
def test_spike_arrest_policy():
    pass


@pytest.mark.happy_path
@pytest.mark.rate_limit
@pytest.mark.apmspii_874
@scenario('./features/proxy_behaviour.feature', 'The rate limit tripped for PATCH requests')
def test_async_spike_arrest_policy():
    pass


@pytest.mark.happy_path
@pytest.mark.quota
@pytest.mark.apmspii_627
@scenario('./features/proxy_behaviour.feature', 'API quota is tripped')
def test_quota_limit():
    pass


@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@given("I have a proxy with a low rate limit set", target_fixture="context")
def setup_rate_limit_proxy(setup_session):
    product, app, token = setup_session

    context = {
        "product": product,
        "app": app,
        "token": token,
    }
    set_quota_and_rate_limit(context["product"], rate_limit="1pm")
    assert context["product"].rate_limit == "1pm"
    return context


@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@given("I have a proxy with a low quota set", target_fixture="context")
def setup_quota_proxy(setup_session):
    context = {
        "product": setup_session[0],
        "app": setup_session[1],
        "token": setup_session[2],
    }
    set_quota_and_rate_limit(context["product"], quota=1)
    assert context["product"].quota == 1
    return context


@pytest.mark.apmspii_627
@pytest.mark.rate_limit
@when(parsers.cfparse(
    "I make a {request:String} request and the rate limit is tripped",
    extra_types=dict(String=str)
))
def trip_rate_limit(request, context):
    context["pds"] = _trip_rate_limit(context["token"], req_type=HTTPMethods[request])
    assert "pds" in context and context["pds"] is not None, "Rate limit wasn't tripped"


@pytest.mark.quota
@pytest.mark.apmspii_627
@when("the quota is tripped")
def trip_quota(context):
    context["pds"] = _trip_rate_limit(context["token"], req_type=HTTPMethods.GET)
    assert "pds" in context and context["pds"] is not None, "Rate limit wasn't tripped"


@pytest.mark.quota
@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def rate_limit_status(status, context):
    assert context["pds"].status_code == status


@pytest.mark.quota
@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@then("returns a rate limit error message")
def quota_message(context):
    response = context["pds"].response
    EXPECTED_KEYS = {"resourceType", "issue"}
    assert response.keys() == EXPECTED_KEYS
    assert (
        response["issue"][0]["details"]["coding"][0]["code"] == HTTPStatus.TOO_MANY_REQUESTS.name
    )
