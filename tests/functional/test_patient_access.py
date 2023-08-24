from tests.functional.config_files import config
import requests
import uuid
import pytest

from tests.functional.utils.apigee_api import ApigeeDebugApi
from tests.functional.utils.helper import (
    generate_random_email_address,
    get_add_telecom_email_patch_body,
)
import logging

LOGGER = logging.getLogger(__name__)

AUTH_PATIENT = { 
    "access": "patient",
    "level": "P9",
    "login_form": {"username": "9912003071"},
}

AUTH_PATIENT_P5 = { 
    "access": "patient",
    "level": "P5",
    "login_form": {"username": "9912003071"},
}

AUTH_PATIENT_p5 = { 
    "access": "patient",
    "level": "p5",
    "login_form": {"username": "9912003071"},
}

AUTH_PATIENT_P0 = { 
    "access": "patient",
    "level": "P0",
    "login_form": {"username": "9912003071"},
}

@pytest.mark.asyncio
class TestUserRestrictedPatientAccess:

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_retrieve_happy_path(self, _nhsd_apim_auth_token_data):
        # token = await nhs_login_token_exchange()

        # LOGGER.info(f'token: {token}')
        LOGGER.info(f'_nhsd_apim_auth_token_data: {_nhsd_apim_auth_token_data}')

        token = _nhsd_apim_auth_token_data.get("access_token", "")

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }
        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
        )

        assert r.status_code == 200

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_retrieve_non_matching_nhs_number(self, _nhsd_apim_auth_token_data):

        token = _nhsd_apim_auth_token_data.get("access_token", "")

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }
        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/123456789",
            headers=headers,
        )
        body = r.json()

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_retrieve_incorrect_path(self, _nhsd_apim_auth_token_data):

        token = _nhsd_apim_auth_token_data.get("access_token", "")

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }
        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?family=Smith&gender=female&birthdate=eq2010-10-22",
            headers=headers,
        )
        body = r.json()

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_nhsd_patient_header_sent_downstream(self, _nhsd_apim_auth_token_data):
        """Requests to the PDS API should include the NHSD-NHSLogin-User header when in Patient Access mode"""

        token = _nhsd_apim_auth_token_data.get("access_token", "")

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }

        debug_session_get = ApigeeDebugApi(config.PROXY_NAME)
        debug_session_get.create_debug_session(headers["X-Request-ID"])

        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
        )

        # Check the GET request
        assert r.status_code == 200
        nhsd_patient_header_get = debug_session_get.get_apigee_header(
            "NHSD-NHSLogin-User"
        )
        assert nhsd_patient_header_get == f"P9:{config.TEST_PATIENT_ID}"

        body = r.json()

        # check if patient already has a telecom object, if so then amend the email address else
        # add a new telecom object
        if "telecom" in body:
            telecom_id = body["telecom"][0]["id"]
            patch_body = {
                "patches": [
                    {
                        "op": "replace",
                        "path": "/telecom/0",
                        "value": {
                            "id": telecom_id,
                            "system": "email",
                            "use": "work",
                            "value": generate_random_email_address(),
                        },
                    }
                ]
            }
        else:
            patch_body = get_add_telecom_email_patch_body()

        e_tag = r.headers["Etag"]
        request_id = str(uuid.uuid4())

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": request_id,
            "If-Match": e_tag,
            "Content-Type": "application/json-patch+json",
        }

        debug_session_patch = ApigeeDebugApi(config.PROXY_NAME)
        debug_session_patch.create_debug_session(request_id)

        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
            json=patch_body,
        )

        assert r.status_code == 200
        nhsd_patient_header_patch = debug_session_patch.get_apigee_header(
            "NHSD-NHSLogin-User"
        )
        assert nhsd_patient_header_patch == f"P9:{config.TEST_PATIENT_ID}"

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_update_happy_path(self, _nhsd_apim_auth_token_data):

        LOGGER.info(f'_nhsd_apim_auth_token_data: {_nhsd_apim_auth_token_data}')
        token = _nhsd_apim_auth_token_data.get("access_token", "")
        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }

        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
        )

        body = r.json()

        """ check if patient already has a telecom object, if so then amend the email address else
            add a new telecom object
        """
        if "telecom" in body:
            telecom_id = body["telecom"][0]["id"]
            patch_body = {
                "patches": [
                    {
                        "op": "replace",
                        "path": "/telecom/0",
                        "value": {
                            "id": telecom_id,
                            "system": "email",
                            "use": "work",
                            "value": generate_random_email_address(),
                        },
                    }
                ]
            }
        else:
            patch_body = get_add_telecom_email_patch_body()

        eTag = r.headers["Etag"]
        version_id = r.json()["meta"]["versionId"]

        LOGGER.info(f'version_id: {version_id}')

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
            "If-Match": eTag,
            "Content-Type": "application/json-patch+json",
        }
        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
            json=patch_body,
        )

        assert r.status_code == 200
        assert int(r.json()["meta"]["versionId"]) == int(version_id) + 1

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_update_non_matching_nhs_number(self, _nhsd_apim_auth_token_data, create_random_date):
        token = _nhsd_apim_auth_token_data.get("access_token", "")

        date = create_random_date

        patch_body = {
            "patches": [{"op": "replace", "path": "/birthDate", "value": date}]
        }

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }

        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
        )
        Etag = r.headers["Etag"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
            "If-Match": Etag,
            "Content-Type": "application/json-patch+json",
        }
        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/123456789",
            headers=headers,
            json=patch_body,
        )
        body = r.json()

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )

    @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT)
    async def test_patient_access_update_incorrect_path(self, _nhsd_apim_auth_token_data, create_random_date):
        token = _nhsd_apim_auth_token_data.get("access_token", "")

        date = create_random_date

        patch_body = {
            "patches": [{"op": "replace", "path": "/birthDate", "value": date}]
        }

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }

        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
        )
        Etag = r.headers["Etag"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
            "If-Match": Etag,
            "Content-Type": "application/json-patch+json",
        }
        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?family=Cox&gender=female&birthdate=eq1956-09-28",
            headers=headers,
            json=patch_body,
        )
        body = r.json()

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )

    # nhsd_apim_authorization throws an exception before sending the request to the proxy, as there is no matching scope
    # @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT_P5)
    # async def test_patient_access_retrieve_P5_scope(self, _nhsd_apim_auth_token_data):
    #     token = _nhsd_apim_auth_token_data.get("access_token", "")

    #     headers = {
    #         "NHSD-SESSION-URID": "123",
    #         "Authorization": "Bearer " + token,
    #         "X-Request-ID": str(uuid.uuid4()),
    #     }
    #     r = requests.get(
    #         f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
    #         headers=headers,
    #     )

    #     body = r.json()

    #     assert r.status_code == 403
    #     assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
    #     assert (
    #         body["issue"][0]["details"]["coding"][0]["display"]
    #         == "Patient cannot perform this action"
    #     )

    # nhsd_apim_authorization throws an exception before sending the request to the proxy, as there is no matching scope
    # @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT_P0)
    # async def test_patient_access_retrieve_P0_scope(self, _nhsd_apim_auth_token_data):
    #     token = _nhsd_apim_auth_token_data.get("access_token", "")

    #     headers = {
    #         "NHSD-SESSION-URID": "123",
    #         "Authorization": "Bearer " + token,
    #         "X-Request-ID": str(uuid.uuid4()),
    #     }
    #     r = requests.get(
    #         f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
    #         headers=headers,
    #     )

    #     body = r.json()

    #     assert r.status_code == 403
    #     assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
    #     assert (
    #         body["issue"][0]["details"]["coding"][0]["display"]
    #         == "Patient cannot perform this action"
    #     )

    # The new fixture throws exception for invalid level: e.g. p5
    # @pytest.mark.nhsd_apim_authorization(AUTH_PATIENT_p5)
    # async def test_patient_access_scope_case_sensitivity_with_p5(self, _nhsd_apim_auth_token_data):
    #     token = _nhsd_apim_auth_token_data.get("access_token", "")
    #     assert token["status_code"] == 401
    #     assert token["body"]["error"] == "unauthorized_client"
    #     assert (
    #         "you have tried to request authorization but your application"
    #         in token["body"]["error_description"]
    #     )
    #     assert (
    #         " is not configured to use this authorization grant type"
    #         in token["body"]["error_description"]
    #     )
