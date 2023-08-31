import os
import pytest

pytest_plugins = ["pytest_nhsd_apim.apigee_edge",
                  "pytest_nhsd_apim.secrets"]

@pytest.fixture()
def status_endpoint_api_key():
    return os.environ.get('STATUS_ENDPOINT_API_KEY', 'not-set')

@pytest.fixture()
def status_endpoint_header(status_endpoint_api_key):
    return {"apikey": status_endpoint_api_key}