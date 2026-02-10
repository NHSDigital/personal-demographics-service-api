import datetime
import json
import uuid
from urllib.parse import parse_qs, urljoin, urlparse

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
from tests.functional.utils.helpers import get_role_id_from_user_info_endpoint


scenario = partial(pytest_bdd.scenario, './features/post_patient.feature')


@scenario('The rate limit is tripped when POSTing new Patients (>3tps)')
def test_post_patient_rate_limit():
    pass


# FIXTURES------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def healthcare_worker_auth_headers(identity_service_base_url: str) -> dict:
    """Authenticates as a healthcare worker and returns valid request headers"""
    session = requests.session()

    callback_url = "https://example.org/callback"
    callback_host = urlparse(callback_url).netloc
    form_request = session.get(
        url=f"{identity_service_base_url}/authorize",
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "state": uuid.uuid4(),
            "redirect_uri": callback_url,
        },
    )

    tree = html.fromstring(form_request.text)
    form = tree.forms[0]

    # Do not follow the external callback redirect.
    login_request = session.post(
        url=form.action,
        data={
            "username": "656005750107",
            "login": "Sign in",
        },
        allow_redirects=False,
    )
    assert login_request.status_code in (301, 302, 303, 307, 308), (
        f"Expected redirect from login POST, got status {login_request.status_code}. "
        f"Body starts with: {login_request.text[:300]!r}"
    )

    login_location = login_request.headers.get("Location")
    assert login_location, "Login redirect response did not include a Location header"

    # Follow only internal redirects and stop before requesting the external callback host.
    final_location = login_location
    for _ in range(10):
        parsed = urlparse(final_location)
        if parsed.netloc == callback_host:
            break

        next_response = session.get(final_location, allow_redirects=False)
        assert next_response.status_code in (301, 302, 303, 307, 308), (
            f"Expected redirect while walking auth flow, got status {next_response.status_code}. "
            f"URL={final_location} Body starts with: {next_response.text[:300]!r}"
        )
        next_location = next_response.headers.get("Location")
        assert next_location, f"Missing Location header while walking auth flow. URL={final_location}"
        final_location = urljoin(final_location, next_location)

    parsed_query = parse_qs(urlparse(final_location).query)
    code_values = parsed_query.get("code")
    assert code_values and code_values[0], f"No auth code in final redirect URL: {final_location}"
    code = code_values[0]

    token_request = session.post(
        url=f"{identity_service_base_url}/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": callback_url,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    assert token_request.status_code == 200, (
        "Token request failed. "
        f"status={token_request.status_code} "
        f"client_id={CLIENT_ID} "
        f"redirect_uri={callback_url} "
        f"final_location={final_location} "
        f"body={token_request.text[:500]!r}"
    )
    access_token = token_request.json()["access_token"]

    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Correlation-ID": str(uuid.uuid4()),
        "Authorization": f"Bearer {access_token}",
    }

    role_id = get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)
    headers.update({"NHSD-Session-URID": role_id})

    return headers


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
