import pytest_bdd
from pytest_bdd import then, parsers
from functools import partial
from .utils.helpers import get_role_id_from_user_info_endpoint
import pytest
from pytest_check import check
import uuid
from jsonpath_rw import parse
from pytest_nhsd_apim.apigee_apis import ApiProductsAPI

related_person_scenario = partial(pytest_bdd.scenario, './features/related_person.feature')


@related_person_scenario('Retrieve a related person')
def test_retrieve_related_person():
    pass


@pytest.fixture(autouse=True)
def add_proxies_to_products_user_restricted(products_api: ApiProductsAPI,
                                            nhsd_apim_proxy_name: str):
    product_name = nhsd_apim_proxy_name.replace("-asid-required", "")

    default_product = products_api.get_product_by_name(product_name=product_name)
    if nhsd_apim_proxy_name not in default_product['proxies']:
        default_product['proxies'].append(nhsd_apim_proxy_name)
        products_api.put_product_by_name(product_name=product_name, body=default_product)


@pytest.fixture(scope='function')
def headers_with_authorization(_nhsd_apim_auth_token_data: dict,
                               identity_service_base_url: str,
                               add_asid_to_testapp: None) -> dict:
    """Assign required headers with the Authorization header"""

    access_token = _nhsd_apim_auth_token_data.get("access_token", "")

    headers = {"X-Request-ID": str(uuid.uuid1()),
               "X-Correlation-ID": str(uuid.uuid1()),
               "Authorization": f'Bearer {access_token}'
               }

    role_id = get_role_id_from_user_info_endpoint(access_token, identity_service_base_url)
    headers.update({"NHSD-Session-URID": role_id})

    return headers


@then(
    parsers.cfparse(
        '{value:String} is {_:String} {type_convertor:String} at {path:String} in the response body',
        extra_types=dict(String=str)
    ))
def check_value_in_response_body_at_path(response_body: dict, value: str, type_convertor: str, path: str) -> None:
    matches = parse(path).find(response_body)
    with check:
        assert matches, f'There are no matches for {value} at {path} in the response body'
        for match in matches:
            assert match.value == eval(type_convertor)(value), \
                f'{match.value} is not the expected value, {value}, at {path}'
