from .environment import ENV


# Sandbox Details
ENVIRONMENT = ENV["environment"]

if ENVIRONMENT.lower() == "local":
    SANDBOX_BASE_URL = "http://0.0.0.0:9000"
else:
    PDS_BASE_PATH = ENV["pds_base_path"]
    SANDBOX_BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk/{PDS_BASE_PATH}"

