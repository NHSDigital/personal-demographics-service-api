import pytest

from .utils import helpers
import uuid
import random
from ..scripts import config
from tests.functional.config_files import config as functional_config
from pytest_nhsd_apim.apigee_apis import (
    ApigeeClient,
    ApigeeNonProdCredentials,
    ApiProductsAPI,
    DeveloperAppsAPI,
)
import logging

LOGGER = logging.getLogger(__name__)

AUTH_HEALTHCARE_WORKER = {
    "access": "healthcare_worker",
    "level": "aal3",
    "login_form": {"username": "656005750104"},
}
DEVELOPER_EMAIL = "apm-testing-internal-dev@nhs.net"


@pytest.fixture()
def client():
    config = ApigeeNonProdCredentials()
    return ApigeeClient(config=config)


@pytest.fixture()
def api_products(client):
    return ApiProductsAPI(client=client)


@pytest.fixture()
def developer_apps(client):
    return DeveloperAppsAPI(client=client)


@pytest.fixture()
def add_asid_to_testapp(developer_apps, nhsd_apim_test_app):
    app = nhsd_apim_test_app()
    LOGGER.info(f'app:{app}')
    app_name = app["name"]

    # Check if the ASID attribute is already available
    app_attributes = developer_apps.get_app_attributes(email=DEVELOPER_EMAIL, app_name=app_name)
    LOGGER.info(f'app_attributes: {app_attributes}')
    custom_attributes = app_attributes['attribute']
    LOGGER.info(f'custom_attributes: {custom_attributes}')
    existing_asid_attribute = None
    for attribute in custom_attributes:
        if attribute['name'] == 'asid':
            existing_asid_attribute = attribute['value']

    if not existing_asid_attribute and functional_config.ENV.contains("internal_dev_asid"):
        LOGGER.info(f'ASID attribute not found. Adding {functional_config.ENV["internal_dev_asid"]} to {app_name}')
        # Add ASID to the test app - To be refactored when we move to .feature files TODO
        custom_attributes.append({"name": "asid", "value": functional_config.ENV["internal_dev_asid"]})
        data = {"attribute": custom_attributes}
        response = developer_apps.post_app_attributes(email=DEVELOPER_EMAIL, app_name=app_name, body=data)
        LOGGER.info(f'Test app updated with ASID attribute: {response}')


@pytest.fixture()
async def headers_with_token(
    _nhsd_apim_auth_token_data,
    request,
    identity_service_base_url,
    nhsd_apim_test_app,
    client,
    api_products,
    add_asid_to_testapp
):
    """Assign required headers with the Authorization header"""

    LOGGER.info(f'_nhsd_apim_auth_token_data: {_nhsd_apim_auth_token_data}')
    access_token = _nhsd_apim_auth_token_data.get("access_token", "")
    role_id = await helpers.get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)

    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "NHSD-Session-URID": role_id,
               "Authorization": f'Bearer {access_token}'
               }

    setattr(request.cls, 'headers', headers)
    LOGGER.info(f'headers: {headers}')


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
