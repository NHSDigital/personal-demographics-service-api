
from ...scripts.environment import EnvVarWrapper


ENV = EnvVarWrapper(
    **{
        "environment": "APIGEE_ENVIRONMENT",
        "pds_base_path": "PDS_BASE_PATH",
        'client_id': 'CLIENT_ID',
        'client_secret': 'CLIENT_SECRET',
        'redirect_uri': 'REDIRECT_URI',
        'authenticate_url': 'AUTHENTICATE_URL',
        'test_patient_id': 'TEST_PATIENT_ID',
        'oauth_proxy': 'OAUTH_PROXY'
    }
)

# Api Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"  # Apigee proxy url

IDENTITY_SERVICE_MOCK_USER_ID = "656005750107"
OAUTH_PROXY = ENV["oauth_proxy"]

AUTHORIZE_URL = f"{BASE_URL}/{OAUTH_PROXY}/authorize"
TOKEN_URL = f"{BASE_URL}/{OAUTH_PROXY}/token"
SIM_AUTH_URL = f"{BASE_URL}/{OAUTH_PROXY}/simulated_auth"
AUTHENTICATE_URL = ENV["authenticate_url"]
CALLBACK_URL = f"{BASE_URL}/{OAUTH_PROXY}/callback"

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]

SPINE_HOSTNAME = (
    # This value is the url returned in the patients response payload which reflects a spine environment.
    # internal-qa environment points to spine int environment.
    "https://veit07.api.service.nhs.uk" if ENVIRONMENT == "internal-dev" else "https://int.api.service.nhs.uk"
)

# App details
CLIENT_ID = ENV["client_id"]
CLIENT_SECRET = ENV["client_secret"]
REDIRECT_URI = ENV["redirect_uri"]

# Endpoints
ENDPOINTS = {
    "authorize": AUTHORIZE_URL,
    "token": TOKEN_URL,
    "authenticate": AUTHENTICATE_URL,
    "callback": CALLBACK_URL,
    "sim_auth": SIM_AUTH_URL,
}

TEST_PATIENT_ID = ENV["test_patient_id"]
