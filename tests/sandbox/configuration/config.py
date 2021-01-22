from .environment import ENV


# Apigee Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"

# PDS
PDS_BASE_PATH = ENV["pds_base_path"]
