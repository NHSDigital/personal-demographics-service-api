import datetime
import json
import os
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
from pytest_bdd import given, when, then, parsers

from tests.functional.conftest import RESPONSES_DIR
from tests.functional.configuration.config import (CLIENT_ID, CLIENT_SECRET)
from tests.functional.utils.helpers import get_role_id_from_user_info_endpoint


scenario = partial(pytest_bdd.scenario, './features/post_patient.feature')


@scenario('Negative test - invalid request payload')
def test_post_patient_invalid():
    pass


@scenario('Valid request, basic payload')
def test_post_patient_basic():
    pass


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
# GIVEN----------------------------------------------------------------------------------------------------------
@given(parsers.parse('path "{path}"'), target_fixture="full_url")
def set_url_path(path: str, pds_url: str) -> str:
    if path[0] != "/":
        path = f"/{path}"
    return f"{pds_url}{path}"


@given(parsers.parse("request body:\n{request_body:json}", extra_types=dict(json=json.loads)),
       target_fixture="request_body")
def set_request_body(request_body: dict) -> dict:
    return request_body


@given(parsers.parse("headers:\n{headers:json}", extra_types=dict(json=json.loads)), target_fixture="headers")
def set_additional_headers(headers: dict, healthcare_worker_auth_headers: dict) -> dict:
    for key, value in headers.items():
        if value == "#(uuid)":
            headers[key] = str(uuid.uuid4())
    healthcare_worker_auth_headers.update(headers)
    return healthcare_worker_auth_headers


# WHEN------------------------------------------------------------------------------------------------------------
@when("method POST", target_fixture="response")
def make_post_request(full_url: str, healthcare_worker_auth_headers: dict, request_body: dict) -> requests.Response:
    response = requests.post(
        full_url,
        headers=healthcare_worker_auth_headers,
        json=request_body,
    )
    return response


@pytest.mark.asyncio
@when("I post to the Patient endpoint more than 5 times per second", target_fixture='post_results')
def post_patient_multiple_times(healthcare_worker_auth_headers: dict, pds_url: str) -> list:
    # firing 30 requests in 5 seconds should trigger the spike arrest policy
    # about 5 times...
    patients_to_create = 30
    target_request_time = 5

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
    elapsed_time_res = response_times[-1] - response_times[0]

    # we fired requests at or faster than the expected rate
    assert elapsed_time_res.seconds <= target_request_time

    return results


# THEN------------------------------------------------------------------------------------------------------------
@then(parsers.parse("status {expected_status:d}"))
def assert_expected_status(expected_status: int, response: requests.Response):
    assert response.status_code == expected_status


@then(parsers.parse("response body:\n{expected_response:json}", extra_types=dict(json=json.loads)))
def assert_expected_response_body(expected_response: dict, response: requests.Response):
    assert expected_response == response.json()


@then(parsers.parse("response body == read({response_file})"))
def assert_against_example_response_file(response_file, response: requests.Response):
    with open(os.path.join(RESPONSES_DIR, f'{response_file}.json'), 'r') as f:
        expected_response_body = json.load(f)
    assert response.json() == expected_response_body


@then("I get a mix of 400 and 429 HTTP response codes")
def assert_expected_spike_arrest_response_codes(post_results):
    successful_requests = [x for x in post_results if x['status'] == 400]
    spike_arrests = [x for x in post_results if x['status'] == 429]
    assert len(spike_arrests) >= 5
    assert len(successful_requests) + len(spike_arrests) == len(post_results)


@then("the 429 response bodies alert me that there have been too many Create Patient requests")
def assert_expected_429_diagnostics(post_results):
    spike_arrests = [x for x in post_results if x['status'] == 429]
    diagnostics = [x['response']['issue'][0]['diagnostics'] for x in spike_arrests]
    expected_diagnostics = 'There have been too many Create Patient requests. Please try again later.'
    correct_diagnostics = [x for x in diagnostics if x == expected_diagnostics]
    assert len(correct_diagnostics) == len(spike_arrests), "Some of the diagnostics messages were not as expected"


@then(parsers.parse("expected_response template == read({response_file})"), target_fixture='expected_response_json')
def set_expected_response_json_string(response_file):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    with open(os.path.join(RESPONSES_DIR, f'{response_file}.json'), 'r') as f:
        json_string = f.read()

    # swap out any pre-defined dynamic values
    new_string = json_string.replace("#todayDate", today_date)
    return new_string


@then(parsers.parse("set expected_response['{placeholder}'] = '{value}'"), target_fixture='expected_response_json')
def set_expected_response_json_value(placeholder, value, expected_response_json):
    new_string = expected_response_json.replace(placeholder, value)
    return new_string


@then(parsers.parse("set expected_response['{placeholder}'] = response['{value}']"),
      target_fixture='expected_response_json')
def set_expected_response_json_with_response_value(placeholder, value, response, expected_response_json):
    new_string = expected_response_json.replace(placeholder, response.json()[value])
    return new_string


@then(parsers.parse("ignore in response comparison the family name Id"), target_fixture='response_json')
def set_ignore_path(response):
    response_json = response.json()
    del response_json['name'][0]['id']
    return response_json


@then("response body == expected_response")
def assert_response_is_expected_response(response_json, expected_response_json):
    expected_response = json.loads(expected_response_json)
    assert response_json == expected_response
