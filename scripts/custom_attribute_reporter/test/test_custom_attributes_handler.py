import json

import pytest

from scripts.custom_attribute_reporter.CustomAttributesHandler import CustomAttributesHandler

MOCK_APP_ID_ONE = "9fa61a6a-dfc1-4395-9966-b105680adace"


@pytest.fixture
def basic_app_meta_data() -> dict:
    return {
        "appId": MOCK_APP_ID_ONE,
        "name": "Test App",
        "attributes": [
            {
                "name": "DisplayName",
                "value": "Mock App One",
            }
        ]
    }


# Example app metadata containing the relevant custom attributes but not the relevant key/product name
@pytest.fixture
def partial_app_meta_data() -> dict:
    return {
        "appId": MOCK_APP_ID_ONE,
        "name": "Test App",
        "attributes": [
            {
                "name": "DisplayName",
                "value": "Mock App One",
            },
            {
                "name": "apim-app-flow-vars",
                "value": json.dumps({
                    "some-other-key": "test"
                })
            },
            {
                "name": "ratelimiting",
                "value": json.dumps({
                    "some-identity-product-dev": {
                        "quota": {"bla": 100}
                    }
                })
            }
        ]
    }


# Example app metadata containing both a relevant rate limit and apim-flow variable
@pytest.fixture
def full_app_meta_data() -> dict:
    return {
        "appId": MOCK_APP_ID_ONE,
        "name": "Test App",
        "attributes": [
            {
                "name": "DisplayName",
                "value": "Mock App One",
            },
            {
                "name": "apim-app-flow-vars",
                "value": json.dumps({
                    "test-flow-var-key": {"app-restricted": {"something": "true"}},
                    "some-other-key": "test"
                })
            },
            {
                "name": "ratelimiting",
                "value": json.dumps({
                    "some-identity-product-dev": {
                        "quota": {"bla": 100}
                    },
                    "test-product-dev": {
                        "quota": {"bla": 120}
                    }
                })
            }
        ]
    }


@pytest.fixture
def basic_custom_attr_handler(basic_app_meta_data) -> CustomAttributesHandler:
    return CustomAttributesHandler(basic_app_meta_data)


def test_custom_attribute_list_empty_when_attributes_not_present():
    custom_attr_handler = CustomAttributesHandler({})
    assert len(custom_attr_handler.custom_attributes) == 0


def test_custom_attributes_are_parsed_correctly(basic_custom_attr_handler):
    assert basic_custom_attr_handler.custom_attributes[0].name == "DisplayName"
    assert basic_custom_attr_handler.custom_attributes[0].value == "Mock App One"


def test_get_method_returns_attribute_by_name(basic_custom_attr_handler):
    display_name_attribute = basic_custom_attr_handler.get("DisplayName")
    assert display_name_attribute is not None
    assert display_name_attribute.name == "DisplayName"
    assert display_name_attribute.value == "Mock App One"


def test_get_method_returns_none_if_attr_does_not_exist(basic_custom_attr_handler):
    assert basic_custom_attr_handler.get("Does not exist") is None


def test_find_rate_limit_for_product_returns_none_if_attr_does_not_exist(basic_custom_attr_handler):
    assert basic_custom_attr_handler.find_rate_limit_for_product("test-product-dev-patient-access") is None


def test_find_rate_limit_for_product_retrieves_info_based_on_product(full_app_meta_data):
    custom_attr_handler = CustomAttributesHandler(full_app_meta_data)
    assert custom_attr_handler.find_rate_limit_for_product("test-product-dev-patient-access") == {
        "quota": {"bla": 120}
    }


def test_find_rate_limit_for_product_returns_none_if_product_limit_does_not_exist(partial_app_meta_data):
    custom_attr_handler = CustomAttributesHandler(partial_app_meta_data)
    assert custom_attr_handler.find_rate_limit_for_product("test-product-dev-patient-access") is None


def test_find_apim_flow_var_returns_none_if_attr_does_not_exist(basic_custom_attr_handler):
    assert basic_custom_attr_handler.find_apim_flow_var("test-flow-var-key") is None


def test_find_apim_flow_var_finds_info_based_on_key(full_app_meta_data):
    custom_attr_handler = CustomAttributesHandler(full_app_meta_data)
    assert custom_attr_handler.find_apim_flow_var("test-flow-var-key") == {
        "app-restricted": {"something": "true"}
    }


def test_find_apim_flow_var_returns_none_if_key_does_not_exist(partial_app_meta_data):
    custom_attr_handler = CustomAttributesHandler(partial_app_meta_data)
    assert custom_attr_handler.find_apim_flow_var("test-flow-var-key") is None
