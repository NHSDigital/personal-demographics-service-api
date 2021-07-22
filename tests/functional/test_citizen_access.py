from tests.functional.config_files import config
import requests
import uuid


class TestUserRestrictedCitizenAccess:
    def test_citizen_access_retrieve_happy_path(
        self, get_token_nhs_login_token_exchange
    ):
        token = get_token_nhs_login_token_exchange["access_token"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
        }
        r = requests.get(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071",
            headers=headers,
        )

        assert r.status_code == 200

    def test_citizen_access_retrieve_non_matching_nhs_number(
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
        assert body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_VALUE"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Cannot retrieve this result with NHS-login Restricted access token"
        )

    def test_citizen_access_retrieve_incorrect_path(
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
        assert body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_VALUE"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Cannot retrieve this result with NHS-login Restricted access token"
        )

    def test_citizen_access_update_happy_path(
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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071",
            headers=headers,
        )
        Etag = r.headers["Etag"]
        versionId = r.json()["meta"]["versionId"]

        headers = {
            "NHSD-SESSION-URID": "123",
            "Authorization": "Bearer " + token,
            "X-Request-ID": str(uuid.uuid4()),
            "If-Match": Etag,
            "Content-Type": "application/json-patch+json",
        }
        r = requests.patch(
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071",
            headers=headers,
            json=patch_body,
        )

        assert r.status_code == 200
        assert int(r.json()["meta"]["versionId"]) == int(versionId) + 1

    def test_citizen_access_update_non_matching_nhs_number(
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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071",
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
        assert body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_VALUE"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Cannot retrieve this result with NHS-login Restricted access token"
        )

    def test_citizen_access_update_incorrect_path(
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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071",
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
            f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?family=Smith&gender=female&birthdate=eq2010-10-22",
            headers=headers,
            json=patch_body,
        )
        body = r.json()

        assert r.status_code == 403
        assert body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_VALUE"
        assert (
            body["issue"][0]["details"]["coding"][0]["display"]
            == "Cannot retrieve this result with NHS-login Restricted access token"
        )
