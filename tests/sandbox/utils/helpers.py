from aiohttp import ClientResponse, ClientSession
from asyncio import sleep, wait_for, TimeoutError
from typing import Union, Callable, Awaitable, Dict
import json
import urllib.parse
import requests
from pytest_check import check
from pytest import fail
from ..configuration import config
from typing import List


def retrieve_patient(patient: str, headers={}) -> requests.Response:
    """Send a PDS Retrieve request

    Args:
        patient (str): NHS Number of Patient
        headers (dict, optional): Headers to include in request. Defaults to {}.

    Returns:
        requests.Response: Response from server
    """
    response = requests.get(
        f"{config.SANDBOX_BASE_URL}/Patient/{patient}", headers=headers
    )
    return response


# A function to send a PDS Retrieve request. Arguments accepted are the Query Parameters & Header.
def search_patient(query_params: Union[dict, str], headers={}) -> requests.Response:
    if isinstance(query_params, dict):
        query_params = urllib.parse.urlencode(query_params, doseq=True)  # converts list to mutliple query params
    response = requests.get(
        f"{config.SANDBOX_BASE_URL}/Patient?{query_params}", headers=headers
    )
    return response


# A function to send a PDS Update request.  Argument accepted are Patient_ID, Patients record version,
# Patch Payload, and any additional Headers.
def update_patient(patient: str, patient_record: str, payload: dict, extra_headers={}) -> requests.Response:
    headers = {
        "Content-Type": "application/json-patch+json",
        "If-Match": f'W/"{patient_record}"',
    }
    headers.update(extra_headers)
    response = requests.patch(
        f"{config.SANDBOX_BASE_URL}/Patient/{patient}", headers=headers, json=payload
    )
    return response


# A function to send a PDS Update request where the standard headers need to be amended.
# Argument accepted are Patient_ID, Patch Payload, and any additional Headers.
def update_patient_invalid_headers(patient: str, payload: dict, headers=None) -> requests.Response:
    response = requests.patch(
        f"{config.SANDBOX_BASE_URL}/Patient/{patient}", headers=headers, json=payload
    )
    return response


# A function to send a PDS Retrieve Related Person request. Arguments accepted are the Patient_ID & Header.
def retrieve_related_person(patient: str, headers={}) -> requests.Response:
    response = requests.get(
        f"{config.SANDBOX_BASE_URL}/Patient/{patient}/RelatedPerson", headers=headers
    )
    return response


def poll_message(content_location: str) -> requests.Response:
    response = requests.get(f"{config.SANDBOX_BASE_URL}{content_location}")
    return response


async def poll_until(url: str,
                     headers: Dict[str, str] = None,
                     until: Callable[[ClientResponse], Awaitable[bool]] = None,
                     timeout: int = 5) -> ClientResponse:
    last_response: ClientResponse = None

    async def _poll_until():
        while True:
            session = ClientSession()
            async with session.get(url, headers=headers) as response:
                last_response = response
                should_stop = await until(response)
                if not should_stop:
                    await sleep(1)
                    continue
                return last_response

    try:
        return await wait_for(_poll_until(), timeout=timeout)
    except TimeoutError:
        fail(f"""
                last status: {last_response.status}
                last headers:{last_response.headers}
                last body:{last_response.body}
            """)


#  A Function to check the Response Body of a Retrieve or Polling Request.
#  Arguments accepted are the actual Response & expected Response.
def check_retrieve_response_body(response: requests.Response, expected_response: dict) -> None:
    response_body = json.loads(response.text)
    with check:
        assert response_body == expected_response, (
            f"UNEXPECTED RESPONSE: "
            f"actual response_body is: {response_body}"
            f"expected response_body is: {expected_response}"
        )


#  A Function to check the Response Body of an Update Request.
#  Arguments accepted are the actual Response & expected Response.
def check_update_response_body(response: requests.Response, expected_response: dict) -> None:
    response_body = json.loads(response.text)
    with check:
        assert response_body == expected_response, (
            f"UNEXPECTED RESPONSE: "
            f"actual response_body is: {response_body}"
            f"expected response_body is: {expected_response}"
        )


#  A Function to check the Response Body of a Search & RelatedPerson Request.
#  Arguments accepted are the actual Response & expected Response.
def check_search_response_body(response: requests.Response, expected_response: dict) -> None:
    response_body = remove_time_stamp_on_search_response(json.loads(response.text))
    with check:
        assert response_body == expected_response, (
            f"UNEXPECTED RESPONSE: "
            f"actual response_body is: {response_body}"
            f"expected response_body is: {expected_response}"
        )


#  A Function to check the Response Status Code of a response.  Arguments accepted are the
#  actual Response & expected Response.
def check_response_status_code(response: requests.Response, expected_status: int) -> None:
    with check:
        assert response.status_code == expected_status, (
            f"UNEXPECTED RESPONSE: "
            f"actual response_status is: {response.status_code} "
            f"expected response_status is: {expected_status}"
        )


#  A Function to check the Response Headers.  Arguments accepted are the actual Response & expected Response.
def check_response_headers(response: requests.Response, expected_headers: Dict[str, str] = {}) -> None:
    expected_headers = {key.lower(): value for key, value in expected_headers.items()}
    actual_headers = {key.lower(): value for key, value in response.headers.items()}
    if "x-request-id" in expected_headers:
        with check:
            assert (
                actual_headers["x-request-id"] == expected_headers["x-request-id"]
            ), (
                f"UNEXPECTED RESPONSE: "
                f"actual X-Request-ID is: {actual_headers['x-request-id']} "
                f"expected X-Request-ID is: {expected_headers['x-request-id']}"
            )
    else:
        with check:
            assert "x-request-id" not in actual_headers, (
                f"UNEXPECTED RESPONSE: expected X-Request-ID not to be present "
                f"but {actual_headers['x-request-id']} found in response header"
            )

    if "x-correlation-id" in expected_headers:
        with check:
            assert (
                actual_headers["x-correlation-id"]
                == expected_headers["x-correlation-id"]
            ), (
                f"UNEXPECTED RESPONSE: "
                f"actual X-Request-ID is: {actual_headers['x-correlation-id']} "
                f"expected X-Request-ID is: {expected_headers['x-correlation-id']}"
            )

    else:
        with check:
            assert "x-correlation-id" not in actual_headers, (
                f"UNEXPECTED RESPONSE: expected X-Correlation-ID not to be present "
                f"but {actual_headers['x-correlation-id']} found in response header"
            )


def remove_time_stamp_on_search_response(response_body: dict) -> dict:
    if "timestamp" in response_body:
        response_body.pop("timestamp")
    return response_body


def dict_path(raw, path: List[str]):
    if not raw:
        return raw

    if not path:
        return raw

    res = raw.get(path[0])
    if not res or len(path) == 1 or not isinstance(res, dict):
        return res

    return dict_path(res, path[1:])
