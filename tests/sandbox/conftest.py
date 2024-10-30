import os
import pytest
import uuid
import time


@pytest.fixture(params=[{"prefer": False}])
def additional_headers(request):
    """Set additional headers and optionally add prefer header"""
    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "Authorization": f"Bearer {uuid.uuid4()}"}
    if request.param["prefer"] is True:
        headers["Prefer"] = "respond-async"
    return headers


@pytest.fixture()
def set_delay():
    """time delay to prevent exceeding proxy rate limit"""
    return time.sleep(2.5)


@pytest.fixture
def commit_id() -> str:
    return os.environ.get('SOURCE_COMMIT_ID', 'not-set')
