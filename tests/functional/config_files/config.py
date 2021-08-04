from .environment import ENV


# Apigee Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"

# Unattended access details
APPLICATION_RESTRICTED_API_KEY = ENV["application_restricted_api_key"]
SIGNING_KEY = ENV["signing_key"]
KEY_ID = ENV["key_id"]

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]

# App details
CLIENT_ID = ENV['client_id']
CLIENT_SECRET = ENV['client_secret']
TEST_PATIENT_ID = ENV['test_patient_id']

# JWT keys
ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH = ENV['nhs_login_private_key']
JWT_PRIVATE_KEY_ABSOLUTE_PATH = ENV['jwt_private_key']

AUTH_TOKEN_EXPIRY_MS = ENV['auth_token_expiry_ms']


AUTH_TOKEN_EXPIRY_MS = (
    ENV['auth_token_expiry_ms'] if ENVIRONMENT == "internal-dev" else ENV['auth_token_expiry_ms_int']
)
