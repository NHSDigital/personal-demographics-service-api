import pytest
from unittest.mock import patch, MagicMock
from ..ApigeeApiSession import ApigeeApiSession


@pytest.fixture
def apigee_session():
    return ApigeeApiSession(
        apigee_org="some_org",
        auth_token="testtoken123"
    )


@patch("requests.Session.request")
def test_apigee_session_class_sets_url_and_headers_correctly(mock_request, apigee_session):
    mock_response = MagicMock()
    mock_request.return_value = mock_response

    apigee_session.get("endpoint")

    mock_request.assert_called_once()
    args, _ = mock_request.call_args

    assert args[0] == "GET"
    assert args[1] == "https://api.enterprise.apigee.com/v1/organizations/some_org/endpoint"
    assert apigee_session.headers["Authorization"] == "Bearer testtoken123"
