from tests.functional.conftest import set_quota_and_rate_limit
from tests.scripts.pds_request import PdsRecord
from tests.user_restricted.utils.authenticator import Authenticator
import pytest
import requests
from pytest_bdd import scenario, given, when, then, parsers
from .config_files.environment import ENV
from .config_files import config

@pytest.mark.happy_path
@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@scenario('./features/sync_wrap.feature',
          'The rate limit is tripped through a synchronous request'
          )
def test_sync_wrap_rate_limit():
    pass


@pytest.mark.happy_path
@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@scenario('./features/sync_wrap.feature',
          'The rate limit is tripped through an async request'
          )
def test_async_rate_limit():
    pass


@pytest.mark.happy_path
@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@scenario('./features/sync_wrap.feature',
          'The rate limit is tripped during sync-wrap polling'
          )
def test_sync_polling_rate_limit():
    pass

    
@pytest.mark.happy_path
@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@scenario('./features/sync_wrap.feature',
          'The access token expires during sync-wrap polling'
          )
def test_sync_polling_token_expires():
    pass


# -------------------------------- GIVEN ----------------------------


@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@given("I have a low sync-wrap timeout", target_fixture="context")
def _setup(sync_wrap_low_wait_update: PdsRecord):
    context = {
        "pds": sync_wrap_low_wait_update
    }
    return context


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@given("I have a proxy with a low rate limit set", target_fixture="context")
def setup_rate_limit_proxy(setup_patch):
    context = {
        "pds": setup_patch["pds"],
        "product": setup_patch["product"],
        "app": setup_patch["app"],
        "token": setup_patch["token"],
    }
    set_quota_and_rate_limit(context["product"], rate_limit="1ps")
    assert context["product"].rate_limit == "1ps"
    return context


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@given("I have a valid PATCH request", target_fixture="context")
def setup_patch_request(context):
    return context

@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@given("I have an access token which expires in polling", target_fixture="context")
def setup_expired_token(setup_patch):
    '''
    data = {
            "_access_token_expiry_ms": "1",
            'client_id': config.CLIENT_ID,
            'client_secret': config.CLIENT_SECRET,
            'grant_type': "authorization_code",
            'redirect_uri': config.REDIRECT_URI
        }
    authenticator = Authenticator(requests.Session)
    response = authenticator.authenticate()
    data['code'] = authenticator.get_code_from_provider(response)

    response = requests.post(f"{config.BASE_URL}/oauth2/token", data=data)
    response_json = response.json()
    print(response_json)
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    '''


    context = {
        "pds": setup_patch["pds"],
        "product": setup_patch["product"],
        "app": setup_patch["app"],
        "token": setup_patch["token"] #Either change this to access a token with short life span, or set_up patch needs modifiying to use expiry param.
    }
  
    return context

# -------------------------------- WHEN ----------------------------


@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@when("I send a request")
def send_request(context: dict):
    pass


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@when("the rate limit is tripped")
def trip_rate_limit(context: dict):
    for i in range(10):
        response = context["pds"].update_patient_response(
            patient_id='5900038181',
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": "2001-01-01"}]}
        )
        if response.status_code == 429:
            context["pds"] = response
            return


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@when("the rate limit is tripped with an async request")
def trip_rate_limit_async(context: dict, create_random_date):
    context["pds"].headers = {
        "Prefer": "respond-async",
    }

    for i in range(10):
        response = context["pds"].update_patient_response(
            patient_id='5900038181',
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
        )
        if response.status_code == 429:
            context["pds"] = response
            return


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@when("the rate limit is tripped with sync-wrap polling")
def trip_rate_limit_sync_polling(context: dict, create_random_date):
    context["pds"].headers = {
        "X-Sync-Wait": "29"
    }
    response = context["pds"].update_patient_response(
        patient_id='5900038181',
        payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
    )
    # assert response.status_code == 429
    if response.status_code == 429:
        context["pds"] = response
        return
    if response.status_code == 200:
        response = context["pds"].update_patient_response(
            patient_id='5900038181',
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
        )
        # assert response.status_code == 429
        if response.status_code == 429:
            context["pds"] = response
            return

@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@when("the access token expires during sync-wrap polling")
def access_token_expired_sync_polling(context: dict, create_random_date):
    context["pds"].headers = {
        "X-Sync-Wait": "29"
    }   #Find a way to alter the OAuth tokens expiry, or assert equal to expiry time being near 0. Goes in here.
    response = context["pds"].update_patient_response(
        patient_id='5900038181',
        payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
    )
    print(response.status_code)
    # assert response.status_code == 401
    if response.status_code == 401:
        context["pds"] = response
        return
    if response.status_code == 200:
        response = context["pds"].update_patient_response(
            patient_id='5900038181',
            payload={"patches": [{"op": "replace", "path": "/birthDate", "value": create_random_date}]}
        )
        # assert response.status_code == 401
        if response.status_code == 401:
            context["pds"] = response
            return

# -------------------------------- THEN ----------------------------


@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@then(
    parsers.cfparse(
        "I get a {status:Number} HTTP response", extra_types=dict(Number=int)
    )
)
def timeout_status(status, context: dict):
    assert context["pds"].status_code == status


@pytest.mark.sync_wrap
@pytest.mark.apmspii_832
@then("returns a helpful error message")
def error_message(context):
    assert context["pds"].response is not None


@pytest.mark.sync_wrap
@pytest.mark.apmspii_874
@then("returns a rate limit error message")
def rate_limit_error_message(context):
    assert context["pds"].response is not None
