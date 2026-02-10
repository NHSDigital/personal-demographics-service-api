import datetime
import json
import re
import uuid

import aiohttp
import asyncio
import requests
import pytest
import pytest_bdd

from dateutil import parser
from functools import partial
from lxml import html
from pytest_bdd import when, then

from tests.functional.configuration.config import (CLIENT_ID, CLIENT_SECRET)


scenario = partial(pytest_bdd.scenario, './features/post_patient.feature')


@scenario('The rate limit is tripped when POSTing new Patients (>3tps)')
def test_post_patient_rate_limit():
    pass


# FIXTURES------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def healthcare_worker_auth_headers(identity_service_base_url: str) -> dict:
    """Runs callback hypotheses and always fails with a diagnostics summary."""
    session = requests.session()

    def _attempt_auth_flow(callback_url: str, follow_redirects: bool, label: str) -> dict:
        result = {
            "label": label,
            "callback_url": callback_url,
            "follow_redirects": follow_redirects,
        }
        print(f"[callback-hypothesis] START {json.dumps(result)}")
        try:
            form_request = session.get(
                url=f"{identity_service_base_url}/authorize",
                params={
                    "response_type": "code",
                    "client_id": CLIENT_ID,
                    "state": uuid.uuid4(),
                    "redirect_uri": callback_url
                }
            )
            result["authorize_status_code"] = form_request.status_code
        except Exception as exc:
            result["error_stage"] = "authorize"
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result

        tree = html.fromstring(form_request.text)
        if not tree.forms:
            result["error_stage"] = "authorize_form_parse"
            result["error"] = "No authorization form found in response"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result
        form = tree.forms[0]

        try:
            login_request = session.post(
                url=form.action,
                data={
                    'username': '656005750107',
                    'login': 'Sign in'
                },
                allow_redirects=follow_redirects
            )
            result["login_status_code"] = login_request.status_code
        except Exception as exc:
            result["error_stage"] = "login"
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result

        try:
            if follow_redirects:
                login_location = login_request.history[-1].headers["Location"]
            else:
                login_location = login_request.headers["Location"]
            result["login_location"] = login_location
        except Exception as exc:
            result["error_stage"] = "redirect_parse"
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result

        code_matches = re.findall(r".*code=(.*)&", login_location)
        if not code_matches:
            result["error_stage"] = "auth_code_parse"
            result["error"] = "No auth code found in login redirect URL"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result
        code = code_matches[0]

        try:
            token_request = session.post(
                url=f"{identity_service_base_url}/token",
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': callback_url,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                }
            )
            result["token_status_code"] = token_request.status_code
        except Exception as exc:
            result["error_stage"] = "token"
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
            return result

        result["token_result"] = "success" if token_request.status_code == 200 else "failed"
        print(f"[callback-hypothesis] RESULT {json.dumps(result, default=str)}")
        return result

    callback_results = []

    # Original code path hypothesis: follow redirects with example callback.
    callback_results.append(
        _attempt_auth_flow("https://example.org/callback", True, "original_follow_redirects")
    )

    # Original code with local callback URLs.
    callback_results.append(
        _attempt_auth_flow("http://localhost/callback", True, "local_http_follow_redirects")
    )
    callback_results.append(
        _attempt_auth_flow("https://localhost/callback", True, "local_https_follow_redirects")
    )

    # Redirect-handling hypothesis: same callbacks without following redirects.
    callback_results.append(
        _attempt_auth_flow("https://example.org/callback", False, "example_no_redirect_follow")
    )
    callback_results.append(
        _attempt_auth_flow("http://localhost/callback", False, "local_http_no_redirect_follow")
    )
    callback_results.append(
        _attempt_auth_flow("https://localhost/callback", False, "local_https_no_redirect_follow")
    )

    print(f"[callback-hypothesis] SUMMARY {json.dumps(callback_results, default=str)}")
    pytest.fail("Intentional diagnostics failure after testing all callback hypotheses")


# SUPPORTING FUNCTIONS-------------------------------------------------------------------------------------------
async def _create_patient(session, headers, url, body):
    details = {'request_time': datetime.datetime.now(datetime.timezone.utc)}

    async with session.post(url=url, headers=headers, json=body) as resp:
        status = resp.status
        headers = resp.headers
        text = await resp.text()
        try:
            json_obj = json.loads(text)
        except ValueError:
            json_obj = resp.json()
        response_dict = json_obj
        details['status'] = status
        details['response'] = response_dict
        details['response_time'] = parser.parse(headers['Date'])
        return details


async def _create_all_patients(headers, url, body, loop, num_patients):
    conn = aiohttp.TCPConnector(limit=3)
    async with aiohttp.ClientSession(connector=conn, loop=loop) as session:
        results = await asyncio.gather(
            *[_create_patient(session, headers, url, body) for _ in range(num_patients)],
            return_exceptions=True
        )
        return results


# STEPS----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# WHEN------------------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
@when("I post to the Patient endpoint more than 3 times per second", target_fixture='post_results')
def post_patient_multiple_times(healthcare_worker_auth_headers: dict, pds_url: str) -> list:
    # firing 40 requests in 10 seconds should trigger the spike arrest policy
    patients_to_create = 40
    target_time_between_first_and_last_request = 10

    url = f'{pds_url}/Patient'
    body = json.dumps({"nhsNumberAllocation": "Done"})

    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(
        _create_all_patients(healthcare_worker_auth_headers, url, body, loop, patients_to_create)
    )
    request_times = [x['request_time'] for x in results]
    request_times.sort()
    elapsed_time_req = request_times[-1] - request_times[0]
    assert elapsed_time_req.seconds == 0

    response_times = [x['response_time'] for x in results]
    response_times.sort()
    actual_time_between_first_and_last_request = response_times[-1] - response_times[0]

    # we fired requests at or faster than the expected rate
    assert actual_time_between_first_and_last_request.seconds <= target_time_between_first_and_last_request

    return results


# THEN------------------------------------------------------------------------------------------------------------
@then("I get a mix of 400 and 429 HTTP response codes")
def assert_expected_spike_arrest_response_codes(post_results):
    successful_requests = [x for x in post_results if x['status'] == 400]
    spike_arrests = [x for x in post_results if x['status'] == 429]
    actual_number_of_spike_arrests = len(spike_arrests)

    patients_to_create = 40
    target_time_between_first_and_last_request = 10
    expected_minimum_number_of_spike_arrests = int(patients_to_create / target_time_between_first_and_last_request)

    assert actual_number_of_spike_arrests >= expected_minimum_number_of_spike_arrests
    assert len(successful_requests) + len(spike_arrests) == len(post_results)


@then("the 429 response bodies alert me that there have been too many Create Patient requests")
def assert_expected_429_diagnostics(post_results):
    spike_arrests = [x for x in post_results if x['status'] == 429]
    diagnostics = [x['response']['issue'][0]['diagnostics'] for x in spike_arrests]
    expected_diagnostics = 'There have been too many Create Patient requests. Please try again later.'
    correct_diagnostics = [x for x in diagnostics if x == expected_diagnostics]
    assert len(correct_diagnostics) == len(spike_arrests), "Some of the diagnostics messages were not as expected"
