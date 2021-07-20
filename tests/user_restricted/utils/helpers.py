import json
import urllib.parse
from typing import Union
import requests
from pytest_check import check
import time
from ..configuration import config
import re
from ..data.pds_scenarios import retrieve


def retrieve_patient_deprecated_url(patient: str, headers) -> requests.Response:
    """Send a PDS Retrieve request to the deprecated URL

    Args:
        patient (str): NHS Number of Patient
        headers (dict, optional): Headers to include in request. Defaults to {}.
    Returns:
        requests.Response: Response from server
    """
    prNo = re.search("pr-[0-9]+", config.PDS_BASE_PATH)
    prString = f"-{prNo.group()}" if prNo is not None else ""

    response = requests.get(
        f"{config.BASE_URL}/personal-demographics{prString}/Patient/{patient}", headers=headers
    )
    return response


def retrieve_patient(patient: str, headers) -> requests.Response:
    """Send a PDS Retrieve request

    Args:
        patient (str): NHS Number of Patient
        headers (dict, optional): Headers to include in request. Defaults to {}.
    Returns:
        requests.Response: Response from server
    """
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers
    )
    return response


def retrieve_patient_related_person(patient: str, headers) -> requests.Response:
    """Send a PDS Retrieve request

    Args:
        patient (str): NHS Number of Patient
        headers (dict, optional): Headers to include in request. Defaults to {}.
    Returns:
        requests.Response: Response from server
    """
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{patient}/RelatedPerson", headers=headers
    )
    return response


# A function to send a PDS Retrieve request. Arguments accepted are the Query Parameters & Header.
def search_patient(query_params: Union[dict, str], headers={}) -> requests.Response:
    if type(query_params) != str:
        query_params = urllib.parse.urlencode(query_params)
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?{query_params}", headers=headers
    )
    return response


# A function to send a PDS Update request.  Argument accepted are Patient_ID, Patients record version,
# Patch Payload, and any additional Headers.
def update_patient(patient: str, patient_record: str, payload: dict, extra_headers={}) -> requests.Response:
    headers = {
        "Content-Type": "application/json-patch+json",
        "If-Match": patient_record,
    }
    headers.update(extra_headers)
    response = requests.patch(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers, json=payload
    )
    return response


# A function to send a PDS Update request where the standard headers need to be amended.
# Argument accepted are Patient_ID, Patch Payload, and any additional Headers.
def update_patient_invalid_headers(patient: str, payload: dict, headers=None) -> requests.Response:
    response = requests.patch(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers, json=payload
    )
    return response


# A function to send a PDS Retrieve Related Person request. Arguments accepted are the Patient_ID & Header.
def retrieve_related_person(patient: str, headers={}) -> requests.Response:
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{patient}/RelatedPerson", headers=headers
    )
    return response


def poll_message(content_location: str, headers={}) -> requests.Response:
    time.sleep(2)
    response = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/{content_location}", headers=headers)
    return response


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


def check_retrieve_related_person_response_body(response: requests.Response, expected_response: dict) -> None:
    response_body = remove_time_stamp_on_search_response(json.loads(response.text))
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
def check_response_headers(response: requests.Response, expected_headers={}) -> None:
    if "X-Request-ID" in expected_headers:
        with check:
            assert (
                response.headers["X-Request-ID"] == expected_headers["X-Request-ID"]
            ), (
                f"UNEXPECTED RESPONSE: "
                f"actual X-Request-ID is: {response.headers['X-Request-ID']} "
                f"expected X-Request-ID is: {expected_headers['X-Request-ID']}"
            )
    else:
        with check:
            assert "X-Request-ID" not in response.headers, (
                f"UNEXPECTED RESPONSE: expected X-Request-ID not to be present "
                f"but {response.headers['X-Request-ID']} found in response header"
            )

    if "X-Correlation-ID" in expected_headers:
        with check:
            assert (
                response.headers["X-Correlation-ID"]
                == expected_headers["X-Correlation-ID"]
            ), (
                f"UNEXPECTED RESPONSE: "
                f"actual X-Correlation-ID is: {response.headers['X-Correlation-ID']} "
                f"expected X-Correlation-ID is: {expected_headers['X-Correlation-ID']}"
            )

    else:
        with check:
            assert "X-Correlation-ID" not in response.headers, (
                f"UNEXPECTED RESPONSE: expected X-Correlation-ID not to be present "
                f"but {response.headers['X-Correlation-ID']} found in response header"
            )


def remove_time_stamp_on_search_response(response_body: dict) -> dict:
    if "timestamp" in response_body:
        response_body.pop("timestamp")
    return response_body


def ping_request() -> requests.Response:
    """Send a Ping request

    Returns:
        requests.Response: Response from server
    """
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/_ping"
    )
    return response


def check_health_check_endpoint(headers=dict) -> requests.Response:
    response = requests.get(
        f"{config.BASE_URL}/{config.PDS_BASE_PATH}/healthcheck", headers=headers
    )
    return response


def check_retrieve_response_body_shape(response: requests.Response) -> None:
    """
    Check the shape of the response body of a patient retrieval.
    scenario "retrieve_patient" in pds_scenarios.py.

    Args:
        response (request.Response): Response
    Returns:
        None
    """
    response_body = json.loads(response.text)
    with check:
        # check id matches
        assert response_body["id"] == retrieve[0]["patient"]
        assert response_body["resourceType"] == "Patient"

        # check the shape of response
        assert response_body["address"] is not None
        assert isinstance(response_body["address"], list)

        assert response_body["birthDate"] is not None
        assert isinstance(response_body["birthDate"], str)
        assert len(response_body["birthDate"]) > 1

        assert response_body["gender"] is not None
        assert isinstance(response_body["gender"], str)

        assert response_body["name"] is not None
        assert isinstance(response_body["name"], list)
        assert len(response_body["name"]) > 0

        assert len(response_body["identifier"]) > 0
        assert isinstance(response_body["identifier"], list)

        assert len(response_body["extension"]) > 0
        assert isinstance(response_body["extension"], list)

        assert response_body["meta"] is not None
