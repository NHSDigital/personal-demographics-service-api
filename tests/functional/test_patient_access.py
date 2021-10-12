from tests.functional.config_files import config
import requests
import uuid
import pytest

from tests.functional.config_files.config import PROXY_NAME
from tests.functional.utils.apigee_api import ApigeeDebugApi


@pytest.mark.asyncio
class TestUserRestrictedPatientAccess:
    async def test_patient_access_retrieve_happy_path(
        self, nhs_login_token_exchange
    ):
        token = await nhs_login_token_exchange()

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

    async def test_patient_access_retrieve_non_matching_nhs_number(
        self, nhs_login_token_exchange
    ):

        token = await nhs_login_token_exchange()

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

    async def test_patient_access_retrieve_incorrect_path(
        self, nhs_login_token_exchange
    ):

        token = await nhs_login_token_exchange()

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

    async def test_patient_access_update_nhsd_patient_header_sent_downstream(
        self, nhs_login_token_exchange
    ):
        token = await nhs_login_token_exchange()

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
        new_gender = "female" if r.json()["gender"] == "male" else "male"

        patch_body = {
            "patches": [{"op": "replace", "path": "/gender", "value": new_gender}]
        }

        request_id = str(uuid.uuid4())

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": request_id,
            "If-Match": Etag,
            "Content-Type": "application/json-patch+json",
        }

        debug_session = ApigeeDebugApi(PROXY_NAME)
        debug_session.create_debug_session(request_id)

        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
            json=patch_body,
        )

        nhsd_patient_header = debug_session.get_apigee_header("NHSD-Patient")
        assert r.status_code == 200
        assert nhsd_patient_header == f"P9:{config.TEST_PATIENT_ID}"

    async def test_patient_access_update_happy_path(
        self, nhs_login_token_exchange, create_random_date
    ):
        token = await nhs_login_token_exchange()

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
        version_id = r.json()["meta"]["versionId"]
        new_gender = "female" if r.json()["gender"] == "male" else "male"

        patch_body = {
            "patches": [{"op": "replace", "path": "/gender", "value": new_gender}]
        }

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
            "If-Match": Etag,
            "Content-Type": "application/json-patch+json",
        }
        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/{config.TEST_PATIENT_ID}",
            headers=headers,
            json=patch_body,
        )

        assert r.status_code == 200
        assert int(r.json()["meta"]["versionId"]) == int(version_id) + 1

    async def test_patient_access_update_non_matching_nhs_number(
        self, nhs_login_token_exchange, create_random_date
    ):
        token = await nhs_login_token_exchange()

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

    async def test_patient_access_update_incorrect_path(
        self, nhs_login_token_exchange, create_random_date
    ):
        token = await nhs_login_token_exchange()

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

    async def test_patient_access_retrieve_P5_scope(
        self, nhs_login_token_exchange
    ):
        token = await nhs_login_token_exchange(scope="P5")

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

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )

    async def test_patient_access_retrieve_P0_scope(
        self, nhs_login_token_exchange
    ):
        token = await nhs_login_token_exchange(scope="P0")

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

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "ACCESS_DENIED"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Patient cannot perform this action"
        )
