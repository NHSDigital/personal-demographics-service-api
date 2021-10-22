from ..utils.helper import get_proxy_name
from ...scripts.environment import EnvVarWrapper

ENV = EnvVarWrapper(
    **{
        "signing_key": "APPLICATION_RESTRICTED_SIGNING_KEY_PATH",
        "signing_key_with_asid": "APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY_PATH",
        "application_restricted_api_key": "APPLICATION_RESTRICTED_API_KEY",
        "application_restricted_with_asid_api_key": "APPLICATION_RESTRICTED_WITH_ASID_API_KEY",
        "pds_base_path": "PDS_BASE_PATH",
        "environment": "APIGEE_ENVIRONMENT",
        "key_id": "KEY_ID",
        'client_id': 'CLIENT_ID',
        'client_secret': 'CLIENT_SECRET',
        'nhs_login_private_key': 'ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH',
        'jwt_private_key': 'JWT_PRIVATE_KEY_ABSOLUTE_PATH',
        'test_patient_id': 'TEST_PATIENT_ID',
        'auth_token_expiry_ms': 'AUTH_TOKEN_EXPIRY_MS',
        'auth_token_expiry_ms_int': 'AUTH_TOKEN_EXPIRY_MS_INT',
        'redirect_uri': 'REDIRECT_URI',
        'apigee_api_token': 'APIGEE_API_TOKEN'
    }
)

# Apigee Details
ENVIRONMENT = ENV["environment"]
APIGEE_API_TOKEN = ENV["apigee_api_token"]
APIGEE_API_URL = 'https://api.enterprise.apigee.com/v1/o/nhsd-nonprod'
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"

# Unattended access details
APPLICATION_RESTRICTED_API_KEY = ENV["application_restricted_api_key"]
APPLICATION_RESTRICTED_WITH_ASID_API_KEY = ENV["application_restricted_with_asid_api_key"]
APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY = ENV["signing_key_with_asid"]
SIGNING_KEY = ENV["signing_key"]
KEY_ID = ENV["key_id"]

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]
PROXY_NAME = get_proxy_name(PDS_BASE_PATH, ENVIRONMENT)

# App details
CLIENT_ID = ENV['client_id']
CLIENT_SECRET = ENV['client_secret']
TEST_PATIENT_ID = ENV['test_patient_id']
REDIRECT_URI = ENV['redirect_uri']

# JWT keys
ID_TOKEN_NHS_LOGIN_PRIVATE_KEY = ENV['nhs_login_private_key']
JWT_PRIVATE_KEY_ABSOLUTE_PATH = ENV['jwt_private_key']

AUTH_TOKEN_EXPIRY_MS = (
    ENV['auth_token_expiry_ms'] if ENVIRONMENT == "internal-dev" else ENV['auth_token_expiry_ms_int']
)
