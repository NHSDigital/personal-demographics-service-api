import pytest
import uuid
import time


@pytest.fixture(params=[{"prefer": False}])
def additional_headers(request):
    headers = {"X-Request-ID": str(uuid.uuid1()), "X-Correlation-ID": str(uuid.uuid1())}
    if request.param["prefer"] == True:
        headers["Prefer"] = "respond-async"
    return headers


@pytest.fixture()
def set_delay():
    """time delay to prevent exceeding proxy rate limit"""
    return time.sleep(1.5)
