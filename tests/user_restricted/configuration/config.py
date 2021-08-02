from .environment import ENV


# Api Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"

IDENTITY_SERVICE = "oauth2-no-smartcard" if ENVIRONMENT == "int" else "oauth2"

AUTHORIZE_URL = f"{BASE_URL}/{IDENTITY_SERVICE}/authorize"
TOKEN_URL = f"{BASE_URL}/{IDENTITY_SERVICE}/token"
SIM_AUTH_URL = f"{BASE_URL}/{IDENTITY_SERVICE}/simulated_auth"
AUTHENTICATE_URL = ENV["authenticate_url"]
CALLBACK_URL = f"{BASE_URL}/{IDENTITY_SERVICE}/callback"

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]

SPINE_HOSTNAME = (
    BASE_URL if ENVIRONMENT != "internal-dev" else "https://veit07.api.service.nhs.uk"
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
