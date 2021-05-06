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
