from .environment import ENV


# Apigee Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"

# Unattended access details
UNATTENDED_ACCESS_API_KEY = ENV["unattended_access_api_key"]
UNATTENDED_ACCESS_SIGNING_KEY_PATH = ENV["unattended_access_signing_key_path"]
KEY_ID = ENV["key_id"]

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]
