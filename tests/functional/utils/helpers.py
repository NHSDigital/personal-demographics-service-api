import json
import urllib.parse
from typing import Optional, Dict, Union
from random import randint
import requests
import uuid

from pytest_check import check
import time
from ..configuration import config
import re
from ..data.pds_scenarios import retrieve
import logging
from pytest_nhsd_apim.identity_service import AuthorizationCodeConfig, AuthorizationCodeAuthenticator

LOGGER = logging.getLogger(__name__)
IDENTITY_SERVICE_BASE_URL = "https://int.api.service.nhs.uk/oauth2-mock"


def find_item_in_dict(obj={}, search_key=""):
    """
    Recursively searches through a dictionary for the key provided and returns its value
    Args:
        obj (dict): the object to search through
        key (string): the key to find
    """
    if search_key in obj:
        return obj[search_key]

    for key, val in obj.items():
        if isinstance(val, dict):
            item = find_item_in_dict(val, search_key)
            if item is not None:
                return item


def get_proxy_name(base_path, environment):
    if "-pr-" in base_path:
        return base_path.replace("/FHIR/R4", "")

    return f'{base_path.replace("/FHIR/R4", "")}-{environment}'


def generate_random_phone_number():
    return f"07784{randint(100000, 999999)}"


def get_add_telecom_phone_patch_body():
    return {
        "patches": [
            {
                "op": "add",
                "path": "/telecom/-",
                "value": {
                    "period": {"start": "2020-02-27"},
                    "system": "phone",
                    "use": "mobile",
                    "value": "07784123456",
                },
            }
        ]
    }


def add_auth_header(headers: Dict[str, str], auth: Optional[Dict[str, str]]):
    """
    Add the authorization header to the headers dict.

    If `auth` is empty, then do not add the header at all.
    """
    if not auth:
        return headers

    access_token = auth["access_token"] or ""
    token_type = auth.get("token_type", "Bearer")

    if access_token == "" and token_type == "":
        headers["Authorization"] = ""
    else:
        headers["Authorization"] = f"{token_type} {access_token}"

    return headers


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

        assert response_body["meta"] is not None


def assert_correct_patient_nhs_number_is_returned(response: requests.Response, expected_nhs_number: str) -> None:
    response_body = json.loads(response.text)

    with check:
        assert response_body["entry"][0]["resource"]["id"] is not None
        assert response_body["entry"][0]["resource"]["id"] == expected_nhs_number


def assert_is_sensitive_patient(response: requests.Response) -> None:
    response_body = json.loads(response.text)

    with check:
        assert response_body["entry"][0]["resource"]["meta"]["security"][0]["display"] == "restricted"


async def get_role_id_from_user_info_endpoint(token, identity_service_base_url) -> str:

    url = f'{identity_service_base_url}/userinfo'
    headers = {"Authorization": f"Bearer {token}"}

    user_info_resp = requests.get(url, headers=headers)
    user_info = json.loads(user_info_resp.text)

    assert user_info_resp.status_code == 200
    return user_info['nhsid_nrbac_roles'][0]['person_roleid']


def get_access_token_for_int_test_app(apigee_environment: str,
                                      nhsd_apim_config: dict,
                                      _test_app_credentials: dict,
                                      authorization_details: dict) -> str:
    user_restricted_app_config = AuthorizationCodeConfig(
        environment=apigee_environment,
        org=nhsd_apim_config["APIGEE_ORGANIZATION"],
        callback_url="https://example.org/callback",
        identity_service_base_url=IDENTITY_SERVICE_BASE_URL,
        client_id=_test_app_credentials["consumerKey"],
        client_secret=_test_app_credentials["consumerSecret"],
        scope="nhs-cis2",
        login_form=authorization_details['login_form']
    )

    authenticator = AuthorizationCodeAuthenticator(config=user_restricted_app_config)

    token_response = authenticator.get_token()
    assert "access_token" in token_response
    access_token = token_response["access_token"]

    LOGGER.info(f'token: {access_token}')

    return access_token


def get_role_id(access_token: str, identity_base_url: str) -> str:
    url = f'{identity_base_url}/userinfo'
    headers = {"Authorization": f"Bearer {access_token}"}

    user_info_resp = requests.get(url, headers=headers)
    user_info = json.loads(user_info_resp.text)

    assert user_info_resp.status_code == 200
    role_id = user_info['nhsid_nrbac_roles'][0]['person_roleid']
    return role_id


def get_headers(apigee_environment: str,
                nhsd_apim_config: dict,
                _test_app_credentials: dict,
                authorization_details: dict) -> dict:
    access_token = get_access_token_for_int_test_app(apigee_environment,
                                                     nhsd_apim_config,
                                                     _test_app_credentials,
                                                     authorization_details)

    role_id = get_role_id(access_token, IDENTITY_SERVICE_BASE_URL)

    headers = {
        "X-Request-ID": str(uuid.uuid1()),
        "X-Correlation-ID": str(uuid.uuid1()),
        "NHSD-Session-URID": role_id,
        "Authorization": f'Bearer {access_token}'
    }

    return headers