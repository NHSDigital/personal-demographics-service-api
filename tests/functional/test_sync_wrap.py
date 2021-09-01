from tests.functional.conftest import set_quota_and_rate_limit
from tests.scripts.pds_request import PdsRecord
import pytest
from polling2 import poll, TimeoutException
from pytest_bdd import scenario, given, when, then, parsers


@pytest.mark.apmspii_832
@scenario('./features/sync_wrap.feature',
          'The rate limit is tripped through a synchronous request'
          )
def test_sync_wrap_rate_limit():
    pass


@pytest.mark.apmspii_874
@scenario('./features/sync_wrap.feature',
          'The rate limit is tripped during sync-wrap polling'
          )
def test_sync_wrap_polling_rate_limit():
    pass


@pytest.mark.apmspii_921
@scenario('./features/sync_wrap.feature',
          'The access token expires during sync-wrap polling'
          )
def test_sync_wrap_polling_token_expires():
    pass


# -------------------------------- GIVEN ----------------------------


@given("I have a low sync-wrap timeout", target_fixture="context")
def _setup(cfg, sync_wrap_low_wait_update: PdsRecord):
    cfg["pds"] = sync_wrap_low_wait_update
    return cfg


@given("I have a proxy with a low rate limit set", target_fixture="context")
def setup_rate_limit_proxy(cfg, setup_patch):
    context = {
        "pds": setup_patch["pds"],
        "product": setup_patch["product"],
        "app": setup_patch["app"],
        "token": setup_patch["token"],
        **cfg
    }
    set_quota_and_rate_limit(context["product"], rate_limit="1pm")
    assert context["product"].rate_limit == "1pm"
    return context


@given("I have a valid PATCH request", target_fixture="context")
def setup_patch_request(cfg, context):
    return {
        **cfg,
        **context
    }


@given("I have an access token expiring soon", target_fixture="context")
def setup_expired_token(cfg, setup_patch_short_lived_token):
    return {
        "pds": setup_patch_short_lived_token,
        **cfg
    }

# -------------------------------- WHEN ----------------------------


@when("I send a request")
def send_request(context: dict):
    pass


@when("the rate limit is tripped")
def trip_rate_limit(context: dict):
    """ Repeat request until receives a 429 or timeout"""

    def _update_patient():
        response = context["pds"].update_patient_response(
            patient_id=context["TEST_PATIENT_ID"],
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": "2001-01-01"}]}
        )
        return response

    def _is_rate_limited(response):
        return response.status_code == 429

    try:
        response = poll(lambda: _update_patient(), timeout=30, step=0.5, check_success=_is_rate_limited)
        context["pds"] = response
        return
    except TimeoutException:
        assert False, "Timeout Error: Rate limit wasn't tripped within set timeout"


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@when("the rate limit is tripped with sync-wrap polling")
def trip_rate_limit_sync_polling(context: dict, create_random_date):
    context["pds"].headers = {
         "X-Sync-Wait": "29"
    }

    def _update_patient():
        response = context["pds"].update_patient_response(
            patient_id=context["TEST_PATIENT_ID"],
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
        )
        return response

    def _is_rate_limited_polling(response):
        return response.status_code == 503

    try:
        response = poll(lambda: _update_patient(), timeout=30, step=0.5, check_success=_is_rate_limited_polling)
        context["pds"] = response
        return
    except TimeoutException:
        assert False, "Timeout Error: Rate limit with sync wrap request wasn't tripped within set timeout"


@when("I PATCH a patient")
def access_token_expired_sync_polling(context: dict, create_random_date):

    # get current gender
    current_gender = context['pds'].last_response.gender
    new_gender = 'female' if current_gender == 'male' else 'male'

    response = context["pds"].update_patient_response(
        patient_id=context["TEST_PATIENT_ID"],
        payload={"patches": [{"op": "replace", "path": "/gender", "value": new_gender}]}
    )
    context["pds"] = response

# -------------------------------- THEN ----------------------------


@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def timeout_status(status, context: dict):
    assert context["pds"].status_code == status


@then(
    parsers.cfparse(
        "returns the error code {error_msg:String}", extra_types=dict(String=str)
    )
)
def response_error_code(error_msg, context: dict):
    assert context["pds"].response["issue"][0]["details"]["coding"][0]["code"] == error_msg


@then("returns a helpful error message")
def error_message(context):
    assert context["pds"].response is not None


@then("returns a rate limit error message")
def rate_limit_error_message(status, context: dict):
    assert context["pds"].response is not None
