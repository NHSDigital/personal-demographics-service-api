import pytest

from .utils import helpers
import uuid
import random
from ..scripts import config


@pytest.fixture()
async def headers_with_token(_nhsd_apim_auth_token_data, request, identity_service_base_url):
    """Assign required headers with the Authorization header"""

    access_token = _nhsd_apim_auth_token_data.get("access_token", "")
    role_id = await helpers.get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)

    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "NHSD-Session-URID": role_id,
               "Authorization": f'Bearer {access_token}'
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
def create_random_date(request):
    day = str(random.randrange(1, 28)).zfill(2)
    month = str(random.randrange(1, 12)).zfill(2)
    year = random.randrange(1940, 2020)
    new_date = f"{year}-{month}-{day}"
    setattr(request.cls, 'new_date', new_date)
