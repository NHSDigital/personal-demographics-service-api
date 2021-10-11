import pytest
import uuid
import time
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig


@pytest.fixture(params=[{"prefer": False}])
def additional_headers(request):
    """Set additional headers and optionally add prefer header"""
    headers = {"X-Request-ID": str(uuid.uuid1()), "X-Correlation-ID": str(uuid.uuid1())}
    if request.param["prefer"] is True:
        headers["Prefer"] = "respond-async"
    return headers


@pytest.fixture()
def set_delay():
    """time delay to prevent exceeding proxy rate limit"""
    return time.sleep(2.5)


@pytest.fixture(scope="session")
def api_test_config() -> APITestSessionConfig:
    return APITestSessionConfig()


@pytest.fixture(scope='function')
async def api_client(api_test_config: APITestSessionConfig):

    session_client = APISessionClient(api_test_config.base_uri)

    yield session_client

    await session_client.close()
