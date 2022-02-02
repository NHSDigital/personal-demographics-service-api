import pytest

from .utils import helpers
from .utils.check_oauth import CheckOauth
import uuid
import random
from ..scripts import config
from api_test_utils.fixtures import webdriver_service  # pylint: disable=unused-import
from api_test_utils.fixtures import webdriver_session  # pylint: disable=unused-import
from api_test_utils.fixtures import docker_compose_file  # pylint: disable=unused-import


@pytest.fixture()
async def headers_with_token(get_token, request):
    """Assign required headers with the Authorization header"""
    token = get_token
    role_id = await helpers.get_role_id_from_user_info_endpoint(token)

    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "NHSD-Session-URID": role_id,
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
async def get_token(docker_compose_file, webdriver_session):
    """Get an access token"""
    oauth_endpoints = CheckOauth()
    token = await oauth_endpoints.get_token_response(webdriver_session)
    access_token = token['access_token']
    return access_token


@pytest.fixture()
def create_random_date(request):
    day = str(random.randrange(1, 28)).zfill(2)
    month = str(random.randrange(1, 12)).zfill(2)
    year = random.randrange(1940, 2020)
    new_date = f"{year}-{month}-{day}"
    setattr(request.cls, 'new_date', new_date)
