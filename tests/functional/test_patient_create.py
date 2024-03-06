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

from .configuration.config import (PDS_BASE_PATH, CLIENT_ID, CLIENT_SECRET)
from .utils.helpers import get_role_id_from_user_info_endpoint


scenario = partial(pytest_bdd.scenario, './features/post_patient_spike_arrest.feature')


@pytest.mark.skipif("asid-required" in PDS_BASE_PATH, reason="Don't run in asid-required environment")
@scenario('The rate limit is tripped when POSTing new Patients (>5tps)')
def test_post_patient_rate_limit():
    pass


# FIXTURES------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def healthcare_worker_auth_headers(identity_service_base_url: str) -> dict:
    """Authenticates as a healthcare worker and returns valid request headers"""
    sesh = requests.session()

    form_request = sesh.get(
        url=f"{identity_service_base_url}/authorize",
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "state": uuid.uuid4(),
            "redirect_uri": "https://example.org/callback"
        }
    )

    tree = html.fromstring(form_request.text)
    form = tree.forms[0]

    login_request = sesh.post(
        url=form.action,
        data={
            'username': '656005750107',
            'login': 'Sign in'
        }
    )
    login_location = login_request.history[-1].headers['Location']

    code = re.findall('.*code=(.*)&', login_location)[0]

    token_request = sesh.post(
        url=f"{identity_service_base_url}/token",
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': "https://example.org/callback",
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )
    assert token_request.status_code == 200
    access_token = token_request.json()["access_token"]

    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Correlation-ID": str(uuid.uuid4()),
        "Authorization": f'Bearer {access_token}'
    }

    role_id = get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)
    headers.update({"NHSD-Session-URID": role_id})

    return headers


# SUPPORTING FUNCTIONS-------------------------------------------------------------------------------------------
async def _create_patient(session, headers, url, body):
    details = {'request_time': datetime.datetime.now(datetime.timezone.utc)}

    async with session.post(url=url, headers=headers, data=body) as resp:
        status = resp.status
        headers = resp.headers
        text = await resp.text()
        response_dict = json.loads(text)
        details['status'] = status
        details['response'] = response_dict
        details['response_time'] = parser.parse(headers['Date'])
        return details


async def _create_all_patients(headers, url, body, loop, num_patients):
    conn = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=conn, loop=loop) as session:
        results = await asyncio.gather(
            *[_create_patient(session, headers, url, body) for _ in range(num_patients)],
            return_exceptions=True
        )
        return results


# STEPS----------------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
@when("I post to the Patient endpoint more than 5 times per second", target_fixture='post_results')
def post_patient_multiple_times(healthcare_worker_auth_headers: dict, pds_url: str) -> list:
    patients_to_create = 27
    url = f'{pds_url}/Patient'
    body = json.dumps({'type': 'object', 'properties': {'nhsNumberAllocation':
                            {'type': 'string', 'description': 'FHIR resource type.',
                             'enum': ['Done'], 'example': 'Done'}},
                             'required': ['nhsNumberAllocation']})

    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(
        _create_all_patients(healthcare_worker_auth_headers, url, body, loop, patients_to_create)
    )
    request_times = [x['request_time'] for x in results]
    request_times.sort()
    elapsed_time_req = request_times[-1] - request_times[0]
    # look how fast we sent those requests
    assert elapsed_time_req.seconds == 0

    response_times = [x['response_time'] for x in results]
    response_times.sort()
    elapsed_time_res = response_times[-1] - response_times[0]
    # the responses came back in under 5 seconds
    assert elapsed_time_res.seconds <= 5

    return results


@then("I get a mix of 404 and 429 HTTP response codes")
def assert_expected_spike_arrest_response_codes(post_results):
    successful_requests = [x for x in post_results if x['status'] == 404]
    spike_arrests = [x for x in post_results if x['status'] == 429]
    assert len(spike_arrests) > 0
    assert len(successful_requests) + len(spike_arrests) == len(post_results)


@then("the 429 response bodies alert me that there have been too many Create Patient requests")
def assert_expected_429_diagnostics(post_results):
    spike_arrests = [x for x in post_results if x['status'] == 429]
    diagnostics = [x['response']['issue'][0]['diagnostics'] for x in spike_arrests]
    expected_diagnostics = 'There have been too many Create Patient requests. Please try again later.'
    correct_diagnostics = [x for x in diagnostics if x == expected_diagnostics]
    assert len(correct_diagnostics) == len(spike_arrests), "Some of the diagnostics messages were not as expected"
