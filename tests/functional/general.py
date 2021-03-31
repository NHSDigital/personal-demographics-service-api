import pytest
import asyncio
from api_test_utils.apigee_api_products import ApigeeApiProducts
from tests.scripts.pds_request import GenericPdsRequestor
from pytest_bdd import scenario, given, when, then, parsers
from .config_files.config import BASE_URL, PDS_BASE_PATH, FHIR_EXT

"""A test suite to test the general proxy behaviour."""


def set_quota_and_rate_limit(
    product: ApigeeApiProducts,
    rate_limit: str = "1000ps",
    quota: int = 60000,
    quota_interval: str = "1",
    quota_time_unit: str = "minute"
):
    """Sets the quota and rate limit on an apigee product.
    """

    asyncio.run(product.update_ratelimits(quota=quota,
                                          quota_interval=quota_interval,
                                          quota_time_unit=quota_time_unit,
                                          rate_limit=rate_limit))


@pytest.mark.happy_path
@scenario('./features/proxy_behaviour.feature', 'API Proxy rate limit tripped')
def test_spike_arrest_policy():
    pass


@pytest.mark.apmspii_627
@given("I have a proxy", target_fixture="context")
def spike_arrest_setup(setup_session):
    context = {}
    context["oauth"] = setup_session[0]
    context["product"] = setup_session[1]
    context["app"] = setup_session[2]
    context["token"] = setup_session[3]
    return context


@given("the product has a low rate limit set")
def set_rate_limit(context):
    print("Product ... ", context["product"])
    set_quota_and_rate_limit(context["product"], rate_limit="3ps")
    assert context["product"].rate_limit == "3ps"
    return context


@when("the rate limit is tripped")
def trip_rate_limit(context):

    def rate_limit():
        pds = GenericPdsRequestor(
            pds_ext=PDS_BASE_PATH,
            base_url=BASE_URL,
            fhir_ext=FHIR_EXT,
            token=context["token"],
        )
        response = pds.get_patient_response(patient_id='5900023656')  # Changes per env?
        # only check when the rate limit is tripped
        if response.status_code == 429:
            return response

    for _ in range(0, 10):
        rate_limit_tripped = rate_limit()
        if rate_limit_tripped:
            print("Rate limit tripped ... ")
            context["pds"] = rate_limit_tripped
            return context

    assert "pds" in context is not None


@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def rate_limit_status(status, context):
    assert context["pds"].status_code == status


@then("returns a rate limit error message")
def rate_limit_message(context):
    response = context["pds"].response
    EXPECTED_KEYS = {"resourceType", "issue"}
    assert response.keys() == EXPECTED_KEYS
    assert (
        response["issue"][0]["diagnostics"] == "You have exceeded your application's rate limit. "
        "Please see: https://digital.nhs.uk/developer/guides-and-documentation/reference-guide#rate-limits "
        "for more details."
    )


@pytest.mark.happy_path
@pytest.mark.apmspii_627
@scenario('./features/proxy_behaviour.feature', 'API quota is tripped')
def test_qouta_limit():
    pass


@given("I have a proxy", target_fixture="context")
def quota_setup(setup_session):
    context = {}
    context["oauth"] = setup_session[0]
    context["product"] = setup_session[1]
    context["app"] = setup_session[2]
    context["token"] = setup_session[3]
    return context


@given("the product has a low quota set")
def set_quota_limit(context):
    print("Product ... ", context["product"])
    set_quota_and_rate_limit(context["product"], quota=1)
    assert context["product"].quota == 1
    return context


@when("the quota is tripped")
def trip_quota(context):

    def rate_limit():
        pds = GenericPdsRequestor(
            pds_ext=PDS_BASE_PATH,
            base_url=BASE_URL,
            fhir_ext=FHIR_EXT,
            token=context["token"],
        )
        response = pds.get_patient_response(patient_id='5900023656')
        # only check when the rate limit is tripped
        if response.status_code == 429:
            return response

    for _ in range(0, 10):
        rate_limit_tripped = rate_limit()
        if rate_limit_tripped:
            print("Rate limit tripped ... ")
            context["pds"] = rate_limit_tripped
            return context

    assert "pds" in context is not None


@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def quota_response(status, context):
    assert context["pds"].status_code == status


@then("returns a rate limit error message")
def quota_message(context):
    response = context["pds"].response
    EXPECTED_KEYS = {"resourceType", "issue"}
    assert response.keys() == EXPECTED_KEYS
    assert (
        response["issue"][0]["diagnostics"] == "You have exceeded your application's rate limit. "
        "Please see: https://digital.nhs.uk/developer/guides-and-documentation/reference-guide#rate-limits "
        "for more details."
    )
