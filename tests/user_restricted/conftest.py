import pytest
from .utils import helpers
# from ..functional.conftest import _product_with_full_access
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


@pytest.fixture()
def client():
    config = ApigeeNonProdCredentials()
    return ApigeeClient(config=config)


@pytest.fixture()
def api_products(client):
    return ApiProductsAPI(client=client)


@pytest.fixture()
def test_setup(api_products,
               client,
               nhsd_apim_test_app,
               nhsd_apim_config,
               nhsd_apim_authorization,
               _identity_service_proxy_name,
               _identity_service_proxy_names):
    # LOGGER.info('Testing class level fixture')
    # product = _product_with_full_access(api_products)
    # product.update_environments([functional_config.ENVIRONMENT], api_products=api_products)

    # LOGGER.info(f'product.proxies: {product.proxies}')

    # print("\nCreating Default App..")
    # # Create a new app
    # developer_apps = DeveloperAppsAPI(client=client)

    # app = ApigeeApiDeveloperApps()
    # create_app_response = app.create_new_app(
    #     callback_url="https://example.org/callback",
    #     status="approved",
    #     jwks_resource_url=functional_config.JWKS_RESOURCE_URL,
    #     products=[product.name],
    #     developer_apps=developer_apps
    # )

    # LOGGER.info(f'create_app_response: {create_app_response}')
    # yield create_app_response["name"]

    # developer_apps = DeveloperAppsAPI(client=client)
    # developer_email = "apm-testing-internal-dev@nhs.net"
    app = nhsd_apim_test_app()
    LOGGER.info(f'app:{app}')
    # app_name = app["name"]

    LOGGER.info(f'_identity_service_proxy_names: {_identity_service_proxy_names}')
    LOGGER.info(f'nhsd_apim_authorization: {nhsd_apim_authorization}')
    LOGGER.info(f'identity service proxy name:{_identity_service_proxy_name}')

    default_product_name = 'personal-demographics-pr-910'
    default_product = api_products.get_product_by_name(product_name=default_product_name)
    LOGGER.info(f'default_product: {default_product}')

    default_product['proxies'].append(functional_config.PROXY_NAME)
    proxies = default_product['proxies']
    LOGGER.info(f'proxies: {proxies}')

    default_product_updated = api_products.put_product_by_name(product_name=default_product_name, body=default_product)
    LOGGER.info(f'default_product_updated: {default_product_updated}')

    # # Updating app with new product
    # app = developer_apps.get_app_by_name(email=developer_email, app_name=app_name)
    # LOGGER.info(f'app: {app}')
    # LOGGER.info(f'app credentials: {app["credentials"]}')
    # new_product = _product_with_full_access(api_products)
    # new_product.update_environments([functional_config.ENVIRONMENT], api_products=api_products)

    # data = {
    #     "attributes": app['attributes'],
    #     "callbackUrl": app['callbackUrl'],
    #     "apiProducts": [new_product.name],
    #     "name": app_name,
    #     "status": app['status']
    # }

    # developer_apps.put_app_by_name(email=developer_email, app_name=app_name, body=data)

    # app = developer_apps.get_app_by_name(email=developer_email, app_name=app_name)
    # LOGGER.info(f'app updated: {app}')

# @pytest.fixture()
# @pytest.mark.nhsd_apim_authorization(AUTH_HEALTHCARE_WORKER)
# def authorisation_fixture(test_setup, headers_with_token):
#     """authorisation_fixture"""
#     new_app = test_setup
#     LOGGER.info(f'New Test app name: {new_app}')


@pytest.fixture()
async def headers_with_token(
    _nhsd_apim_auth_token_data,
    request,
    identity_service_base_url,
    nhsd_apim_test_app,
    client,
    api_products
):
    """Assign required headers with the Authorization header"""

    developer_apps = DeveloperAppsAPI(client=client)
    developer_email = "apm-testing-internal-dev@nhs.net"
    app = nhsd_apim_test_app()
    LOGGER.info(f'app:{app}')
    app_name = app["name"]

    # # Updating app with new product
    # app = developer_apps.get_app_by_name(email=developer_email, app_name=app_name)
    # LOGGER.info(f'app: {app}')
    # LOGGER.info(f'app credentials: {app["credentials"]}')
    # new_product = _product_with_full_access(api_products)
    # new_product.update_environments([functional_config.ENVIRONMENT], api_products=api_products)

    # data = {
    #     "attributes": app['attributes'],
    #     "callbackUrl": app['callbackUrl'],
    #     "apiProducts": [new_product.name],
    #     "name": app_name,
    #     "status": app['status']
    # }

    # developer_apps.put_app_by_name(email=developer_email, app_name=app_name, body=data)

    # app = developer_apps.get_app_by_name(email=developer_email, app_name=app_name)
    # LOGGER.info(f'app updated: {app}')

    # Check if the ASID attribute is already available
    app_attributes = developer_apps.get_app_attributes(email=developer_email, app_name=app_name)
    # LOGGER.info(f'app_attributes: {app_attributes}')
    custom_attributes = app_attributes['attribute']
    # LOGGER.info(f'custom_attributes: {custom_attributes}')
    existing_asid_attribute = None
    for attribute in custom_attributes:
        if attribute['name'] == 'asid':
            existing_asid_attribute = attribute['value']

    if not existing_asid_attribute:
        # Add ASID to the test app - To be refactored when we move to .feature files TODO
        custom_attributes.append({"name": "asid", "value": functional_config.ENV["internal_dev_asid"]})
        # LOGGER.info(f'custom_attributes: {custom_attributes}')
        data = {"attribute": custom_attributes}
        developer_apps.post_app_attributes(email=developer_email, app_name=app_name, body=data)
        # LOGGER.info(f'post_app_attributes_response: {response}')

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
