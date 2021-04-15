import pytest
import asyncio
import requests
from http import HTTPStatus
from api_test_utils.apigee_api_products import ApigeeApiProducts
from tests.scripts.pds_request import GenericPdsRequestor
from pytest_bdd import scenario, given, when, then, parsers
from .config_files.config import BASE_URL, PDS_BASE_PATH


def set_quota_and_rate_limit(
    product: ApigeeApiProducts,
    rate_limit: str = "1000ps",
    quota: int = 60000,
    quota_interval: str = "1",
    quota_time_unit: str = "minute"
) -> None:
    """Sets the quota and rate limit on an apigee product.

    Args:
        product (ApigeeApiProducts): Apigee product
        rate_limit (str): The rate limit to be set.
        quota (int): The amount of requests per quota interval.
        quoata_interval (str): The length of a quota interval in quota units.
        quota_time_unit (str): The quota unit length e.g. minute.
    """
    asyncio.run(product.update_ratelimits(quota=quota,
                                          quota_interval=quota_interval,
                                          quota_time_unit=quota_time_unit,
                                          rate_limit=rate_limit))


def _trip_rate_limit(token: str) -> requests.Response:
    """Trips the spike arrest policy and returns the response.

    Args:
        token (str): OAuth access token.

    Returns:
        response (requests.Response): HTTP Response.
    """
    def _pds_response():
        pds = GenericPdsRequestor(
            pds_base_path=PDS_BASE_PATH,
            base_url=BASE_URL,
            token=token,
        )
        response = pds.get_patient_response(patient_id='5900038181')
        # only check when the rate limit is tripped
        if response.status_code == 429:
            return response

    for _ in range(0, 10):
        response = _pds_response()
        if response:
            return response


@pytest.mark.happy_path
@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@scenario('./features/proxy_behaviour.feature', 'API Proxy rate limit tripped')
def test_spike_arrest_policy():
    pass


@pytest.mark.happy_path
@pytest.mark.quota
@pytest.mark.apmspii_627
@scenario('./features/proxy_behaviour.feature', 'API quota is tripped')
def test_qouta_limit():
    pass


@pytest.mark.quota
@pytest.mark.rate_limit
@pytest.mark.apmspii_627
@given("I have a proxy", target_fixture="context")
def setup_proxy(setup_session):
    return {
        "oauth": setup_session[0],
        "product": setup_session[1],
        "app": setup_session[2],
        "token": setup_session[3],
    }


@pytest.mark.apmspii_627
@pytest.mark.rate_limit
@given("the product has a low rate limit set")
def set_rate_limit(context):
    set_quota_and_rate_limit(context["product"], rate_limit="1ps")
    assert context["product"].rate_limit == "1ps"
    return context


@pytest.mark.quota
@pytest.mark.apmspii_627
@given("the product has a low quota set")
def set_quota_limit(context):
    set_quota_and_rate_limit(context["product"], quota=1)
    assert context["product"].quota == 1
    return context


@pytest.mark.apmspii_627
@pytest.mark.rate_limit
@when("the rate limit is tripped")
def trip_rate_limit(context):
    context["pds"] = _trip_rate_limit(context["token"])
    assert "pds" in context is not None


@pytest.mark.quota
@pytest.mark.apmspii_627
@when("the quota is tripped")
def trip_quota(context):
    context["pds"] = _trip_rate_limit(context["token"])
    assert "pds" in context is not None


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
