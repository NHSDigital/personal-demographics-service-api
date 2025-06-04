from unittest.mock import patch, Mock

import pytest
import requests

from scripts.custom_attribute_reporter.ApigeeApiHandler import ApigeeApiHandler


MOCK_APP_ID_ONE = "9fa61a6a-dfc1-4395-9966-b105680adace"
MOCK_APP_ID_TWO = "8aab6014-c002-43eb-84af-430a1d662f9c"


@pytest.fixture
def mock_get_app_ids_success_response() -> Mock:
    return Mock(
        status_code=200,
        json=Mock(return_value=[MOCK_APP_ID_ONE, MOCK_APP_ID_TWO]),
    )


@pytest.fixture
def mock_get_app_meta_data_success_response() -> Mock:
    return Mock(
        status_code=200,
        json=Mock(return_value={
            "appId": MOCK_APP_ID_ONE,
            "name": "Test",
            "attributes": [
                {
                    "name": "DisplayName",
                    "value": "Ipsum"
                }
            ]
        })
    )


@patch("requests.Session.request")
def test_get_app_ids_for_products_returns_app_id_list(mock_request, mock_get_app_ids_success_response):
    mock_request.return_value = mock_get_app_ids_success_response
    apigee_api_handler = ApigeeApiHandler("nhsd-test", "1234AccessToken")

    response = apigee_api_handler.get_app_ids_for_product("test-product")

    assert response == [MOCK_APP_ID_ONE, MOCK_APP_ID_TWO]
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args

    assert args[0] == "GET"
    assert args[1] == "https://api.enterprise.apigee.com/v1/organizations/nhsd-test/apiproducts/test-product"
    assert kwargs["params"] == {"query": "list", "entity": "apps"}
    assert apigee_api_handler._api_session.headers["Authorization"] == "Bearer 1234AccessToken"


@patch("requests.Session.request")
def test_get_app_ids_for_throws_error_for_non_success_status_code(mock_request):
    mock_request.return_value = Mock(status_code=418, text="I'm a teapot")
    apigee_api_handler = ApigeeApiHandler("nhsd-test", "1234AccessToken")

    expected_error = "Something went wrong:\n418\nI'm a teapot"

    with pytest.raises(requests.exceptions.HTTPError, match=expected_error):
        apigee_api_handler.get_app_ids_for_product("test-product")

    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args

    assert args[0] == "GET"
    assert args[1] == "https://api.enterprise.apigee.com/v1/organizations/nhsd-test/apiproducts/test-product"
    assert kwargs["params"] == {"query": "list", "entity": "apps"}
    assert apigee_api_handler._api_session.headers["Authorization"] == "Bearer 1234AccessToken"


@patch("requests.Session.request")
def test_get_app_meta_data_returns_full_response(
    mock_request,
    mock_get_app_meta_data_success_response
):
    mock_request.return_value = mock_get_app_meta_data_success_response
    apigee_api_handler = ApigeeApiHandler("nhsd-test", "1234AccessToken")

    result = apigee_api_handler.get_app_metadata(MOCK_APP_ID_ONE)

    assert result == mock_get_app_meta_data_success_response.json()
    mock_request.assert_called_once()
    args, _ = mock_request.call_args

    assert args[0] == "GET"
    assert args[1] == f"https://api.enterprise.apigee.com/v1/organizations/nhsd-test/apps/{MOCK_APP_ID_ONE}"
    assert apigee_api_handler._api_session.headers["Authorization"] == "Bearer 1234AccessToken"


@patch("requests.Session.request")
def test_get_custom_attributes_for_app_throws_error_for_non_success_status_code(mock_request):
    mock_request.return_value = Mock(status_code=418, text="I'm a teapot")
    apigee_api_handler = ApigeeApiHandler("nhsd-test", "1234AccessToken")

    expected_error = f"Something went wrong for apps/{MOCK_APP_ID_ONE}:\n418\nI'm a teapot"

    with pytest.raises(requests.exceptions.HTTPError, match=expected_error):
        apigee_api_handler.get_app_metadata(MOCK_APP_ID_ONE)

    mock_request.assert_called_once()
    args, _ = mock_request.call_args

    assert args[0] == "GET"
    assert args[1] == f"https://api.enterprise.apigee.com/v1/organizations/nhsd-test/apps/{MOCK_APP_ID_ONE}"
    assert apigee_api_handler._api_session.headers["Authorization"] == "Bearer 1234AccessToken"
