from tests.functional.config_files import config
from tests.user_restricted.data.pds_scenarios import retrieve, search, update
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

        expected_response = {'resourceType': 'OperationOutcome', 'issue': [{'severity': 'error', 'code': 'token', 'details': {'coding': [{'system': 'https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode', 'version': '1', 'code': 'INVALID_VALUE', 'display': 'Cannot retrieve this result with NHS-login Restricted access token'}]}, 'diagnostics': 'Your app has insufficient permissions to perform this search. Please contact support.'}]}

        token = get_token_nhs_login_token_exchange["access_token"]
        
        headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": "Bearer " + token,
        "X-Request-ID": str(uuid.uuid4()),
    }
        r = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient/123456789", headers=headers)
        body = r.json()

        assert r.status_code == 403
        assert body == expected_response
        

    def test_citizen_access_incorrect_path(self, get_token_nhs_login_token_exchange):

        expected_response = {'resourceType': 'OperationOutcome', 'issue': [{'severity': 'error', 'code': 'token', 'details': {'coding': [{'system': 'https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode', 'version': '1', 'code': 'INVALID_VALUE', 'display': 'Cannot retrieve this result with NHS-login Restricted access token'}]}, 'diagnostics': 'Your app has insufficient permissions to perform this search. Please contact support.'}]}

        token = get_token_nhs_login_token_exchange["access_token"]
        
        headers = {
        "NHSD-SESSION-URID": "123",
        "Authorization": "Bearer " + token,
        "X-Request-ID": str(uuid.uuid4()),
    }
        r = requests.get(f"{config.BASE_URL}/{config.PDS_BASE_PATH}/Patient?family=Smith&gender=female&birthdate=eq2010-10-22", headers=headers)
        body = r.json()

        assert r.status_code == 403
        assert body == expected_response