import pytest
from .utils.check_oauth import CheckOauth
import uuid
import random
from ..scripts import config


@pytest.fixture()
def headers_with_token(get_token, request):
    """Assign required headers with the Authorization header"""
    token = get_token
    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "NHSD-Session-URID": config.ROLE_ID,
               "Authorization": f'Bearer {token}'
               }
    setattr(request.cls, 'headers', headers)


@pytest.fixture()
def headers():
    """Assign required headers without the Authorization header"""
    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "NHSD-Session-URID": config.ROLE_ID
               }
    return headers


@pytest.fixture()
def get_token():
    """Get an access token"""
    oauth_endpoints = CheckOauth()
    token = oauth_endpoints.get_token_response()
    access_token = token['access_token']
    return access_token


@pytest.fixture()
def create_random_date(request):
    day = str(random.randrange(1, 28)).zfill(2)
    month = str(random.randrange(1, 12)).zfill(2)
    year = random.randrange(1940, 2020)
    new_date = f"{year}-{month}-{day}"
    setattr(request.cls, 'new_date', new_date)
