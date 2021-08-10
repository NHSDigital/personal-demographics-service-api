from tests.functional.config_files import config
import requests
import uuid


class TestUserRestrictedPatientAccess:
    def test_patient_access_retrieve_happy_path(
        self, get_token_nhs_login_token_exchange
    ):
        token = get_token_nhs_login_token_exchange["access_token"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }
        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9693633172",
            headers=headers,
        )

        assert r.status_code == 200

    def test_patient_access_retrieve_non_matching_nhs_number(
        self, get_token_nhs_login_token_exchange
    ):

        token = get_token_nhs_login_token_exchange["access_token"]

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

    def test_patient_access_retrieve_incorrect_path(
        self, get_token_nhs_login_token_exchange
    ):

        token = get_token_nhs_login_token_exchange["access_token"]

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

    def test_patient_access_update_happy_path(
        self, get_token_nhs_login_token_exchange, create_random_date
    ):
        token = get_token_nhs_login_token_exchange["access_token"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }

        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9693633172",
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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9693633172",
            headers=headers,
            json=patch_body,
        )

        assert r.status_code == 200
        assert int(r.json()["meta"]["versionId"]) == int(version_id) + 1

    def test_patient_access_update_non_matching_nhs_number(
        self, get_token_nhs_login_token_exchange, create_random_date
    ):
        token = get_token_nhs_login_token_exchange["access_token"]

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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9693633172",
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

    def test_patient_access_update_incorrect_path(
        self, get_token_nhs_login_token_exchange, create_random_date
    ):
        token = get_token_nhs_login_token_exchange["access_token"]

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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9693633172",
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
