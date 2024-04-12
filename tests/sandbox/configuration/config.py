from .environment import ENV


# Sandbox Details
ENVIRONMENT = ENV["environment"]

if ENVIRONMENT.lower() == "local":
    SANDBOX_BASE_URL = "http://0.0.0.0:9000"
elif ENVIRONMENT.lower() == "docker":
    CONTAINER_IP = ENV["container_ip"]
    SANDBOX_BASE_URL = f"http://{CONTAINER_IP}:9090"
else:
    SERVICE_BASE_PATH = ENV["service_base_path"]
    SANDBOX_BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}"
