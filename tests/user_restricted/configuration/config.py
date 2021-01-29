from .environment import ENV


# Api Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"
IDENTITY_PROXY = ENV['identity_proxy']

AUTHORIZE_URL = f"{BASE_URL}/{IDENTITY_PROXY}/authorize"
TOKEN_URL = f"{BASE_URL}/{IDENTITY_PROXY}/token"
SIM_AUTH_URL = f"{BASE_URL}/{IDENTITY_PROXY}/simulated_auth"
AUTHENTICATE_URL = ENV['authenticate_url']
CALLBACK_URL = f"{BASE_URL}/{IDENTITY_PROXY}/callback"

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]

# App details
CLIENT_ID = ENV['client_id']
CLIENT_SECRET = ENV['client_secret']
REDIRECT_URI = ENV['redirect_uri']

# Endpoints
ENDPOINTS = {
    'authorize': AUTHORIZE_URL,
    'token': TOKEN_URL,
    'authenticate': AUTHENTICATE_URL,
    'callback': CALLBACK_URL,
    'sim_auth': SIM_AUTH_URL
}
