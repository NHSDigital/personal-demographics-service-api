import time

import pytest

from pytest import FixtureRequest
from pytest_bdd import given, parsers

from pytest_nhsd_apim.apigee_apis import ApiProductsAPI

from tests.functional.data import patients
from tests.functional.data.users import UserDirectory
from tests.functional.data.patients import Patient


@given('scope added to product')
def add_scope_to_products_patient_access(products_api: ApiProductsAPI,
                                         nhsd_apim_proxy_name: str,
                                         nhsd_apim_authorization: dict):
    scope = nhsd_apim_authorization['scope']
    product_name = nhsd_apim_proxy_name.replace("-asid-required", "")

    def is_scope_in_product() -> bool:
        return scope in products_api.get_product_by_name(product_name)['scopes']

    if is_scope_in_product():
        return

    product = products_api.get_product_by_name(product_name=product_name)
    product['scopes'].append(scope)
    products_api.put_product_by_name(product_name=product_name, body=product)

    max_wait, time_waited, wait_period = 10, 0, 1
    while not is_scope_in_product():
        if time_waited > max_wait:
            raise TimeoutError(f'Scope {scope} did not get added to'
                               f'product {product_name}')
        time.sleep(wait_period)
        time_waited += wait_period


@given('I am a patient with a related person', target_fixture='patient')
def self_patient_with_a_related_person() -> Patient:
    return patients.SELF_WITH_RELATED_PERSON


@given('I have a patient with a related person', target_fixture='patient')
def patient_with_a_related_person() -> Patient:
    return patients.WITH_RELATED_PERSON


@pytest.fixture(scope='session')
def user_directory() -> UserDirectory:
    return UserDirectory()


@given(
    parsers.cfparse(
        "I am a {access_level:String} user with the NHS number linked to an account",
        extra_types=dict(String=str)
    ), target_fixture='patient')
def set_user(access_level: str) -> Patient:
    patient = patients.OTHER_PATIENTS[access_level]
    return patient


# Keep the comments for easily finding via text search...
# Given I am a healthcare worker user
# Given I am a P9 user
@given(
    parsers.cfparse(
        "I am {_:String} {user_name:String} user",
        extra_types=dict(String=str)
    ))
def add_auth_marker(request: FixtureRequest, user_name: str, user_directory: UserDirectory) -> None:
    auth_details = user_directory[user_name.replace(' ', '_')
                                           .replace('-', '_')]
    request.node.add_marker(pytest.mark.nhsd_apim_authorization(auth_details))
