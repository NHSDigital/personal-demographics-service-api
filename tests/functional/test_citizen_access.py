from tests.functional.config_files import config
import requests
import uuid

class TestUserRestrictedCitizenAccess:
    
    def test_citizen_access_happy_path(self, get_token_nhs_login_token_exchange):
        token = get_token_nhs_login_token_exchange["access_token"]
        
        headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": "Bearer " + token,
        "X-Request-ID": str(uuid.uuid4()),
    }
        r = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/9912003071", headers=headers)

        assert r.status_code == 200

    def test_citizen_access_non_matching_nhs_number(self, get_token_nhs_login_token_exchange):
        token = get_token_nhs_login_token_exchange["access_token"]
        
        headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": "Bearer " + token,
        "X-Request-ID": str(uuid.uuid4()),
    }
        r = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/123456789", headers=headers)

        assert r.status_code == 403

    def test_citizen_access_incorrect_path(self, get_token_nhs_login_token_exchange):

        token = get_token_nhs_login_token_exchange["access_token"]
        
        headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": "Bearer " + token,
        "X-Request-ID": str(uuid.uuid4()),
    }
        r = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?family=Smith&gender=female&birthdate=eq2010-10-22", headers=headers)

        assert r.status_code == 403