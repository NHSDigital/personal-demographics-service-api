import datetime
import json
import re
import uuid

import aiohttp
import asyncio
import requests
import pytest


from lxml import html

from functools import partial
from polling2 import poll, TimeoutException
from pytest_bdd import given, when, then, parsers
import pytest_bdd

from tests.functional.conftest import set_quota_and_rate_limit
from tests.scripts.pds_request import PdsRecord

from .configuration.config import (PDS_BASE_PATH, CLIENT_ID, CLIENT_SECRET, OAUTH_PROXY)
from .utils.helpers import get_role_id_from_user_info_endpoint


scenario = partial(pytest_bdd.scenario, './features/post_patient_spike_arrest.feature')

@pytest.mark.skipif("asid-required" in PDS_BASE_PATH, reason="Don't run in asid-required environment")
@scenario('The rate limit is tripped when POSTing new Patients (>5tps)')
def test_post_patient_rate_limit():
    pass


#-FIXTURES------------------------------------------------------------------------------------------------------
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


#-SUPPORTING FUNCTIONS-------------------------------------------------------------------------------------------
async def make_async_calls(headers: dict, url: str, body: str):
    # set the request limit to be pretty fast
    aiohttp.TCPConnector(limit=50)

    request_details = []
    
    async def _make_call(headers, url, body):
        details = {'request_time': datetime.datetime.now(datetime.timezone.utc)}
        async with session.post(
            url=url,
            headers=headers,
            data=body) as resp:
                status = resp.status
                headers = resp.headers
                text = await resp.text()
                response_dict = json.loads(text)
                details['status'] = status
                details['response'] = response_dict
                request_details.append(details)

    async with aiohttp.ClientSession() as session:
        for _ in range(6):
            await _make_call(headers,url,body)

    return request_details


#-STEPS----------------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
@when("I post to the Patient endpoint more than 5 times per second", target_fixture='response')
def post_patient_multiple_times(healthcare_worker_auth_headers: dict, pds_url: str) -> requests.Response:
    url = f'{pds_url}/Patient'
    body = json.dumps({"nhsNumberAllocation": "Done"})
    results = asyncio.run(make_async_calls(healthcare_worker_auth_headers, url, body))
    times = [x['request_time'] for x in results]
    times.sort()
    elapsed_time = times[-1] - times[0]
    total_requests = len(results)
    tps = total_requests / elapsed_time.seconds
    assert tps > 5 
    spike_arrest_results = [x for x in results if x['status'] == 429]
    
    # # dubious approach
    # def _create_patient():
    #     response = requests.post(
    #         data=json.dumps({"nhsNumberAllocation": "Done"}),
    #         headers=healthcare_worker_auth_headers,
    #         url=f'{pds_url}/Patient'
    #     )
    #     return response

    # def _is_rate_limited_polling(response):
    #     return response.status_code == 429

    # try:
    #     response = poll(lambda: _create_patient(), timeout=5, step=0.01, check_success=_is_rate_limited_polling)
    #     return response
    # except TimeoutException:
    #     assert False, "Timeout Error: Rate limit with sync wrap request wasn't tripped within set timeout"


@then("returns a rate limit error message")
def rate_limit_error_message(response: requests.Response):
    # improve this when we get there
    import pytest; pytest.set_trace()
    code = response.json()["issue"][0]["details"]["coding"][0]["code"]
    assert code == "TOO_MANY_REQUESTS"
