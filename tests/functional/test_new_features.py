import copy
import json
import pytest
import requests

from jsonschema import validate
from pytest_bdd import scenarios, given, when, then, parsers


### copied from elsewhere
import jwt
import requests
import time
import uuid

from tests.functional.configuration import config


from typing import Optional, Dict


def add_auth_header(headers: Dict[str, str], auth: Optional[Dict[str, str]]):
    """
    Add the authorization header to the headers dict.

    If `auth` is empty, then do not add the header at all.
    """
    if not auth:
        return headers

    access_token = auth["access_token"] or ""
    token_type = auth.get("token_type", "Bearer")

    if access_token == "" and token_type == "":
        headers["Authorization"] = ""
    else:
        headers["Authorization"] = f"{token_type} {access_token}"

    return headers


@given("I am authenticating using unattended access", target_fixture="auth")
def auth():
    return {}



@given("I have a request context", target_fixture="context")
def context():
    return {}


@given("I have a valid access token")
def set_valid_access_token(auth, context):

    # Get new access token
    claims = {
        "sub": config.APPLICATION_RESTRICTED_API_KEY,
        "iss": config.APPLICATION_RESTRICTED_API_KEY,
        "jti": str(uuid.uuid4()),
        "aud": f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        "exp": int(time.time()) + 300,
    }

    # If one exists, use the client_id of the test app instead
    if "app" in context:
        claims.update(
            {
                "sub": context["app"].get_client_id(),
                "iss": context["app"].get_client_id(),
            }
        )

    headers = {"kid": config.KEY_ID}

    encoded_jwt = jwt.encode(
        claims, config.SIGNING_KEY, algorithm="RS512", headers=headers
    )

    response = requests.post(
        f"{config.BASE_URL}/{config.OAUTH_PROXY}/token",
        data={
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        },
    )

    token_response = response.json()
    print(token_response)

    # Does our response object contain the expected keys (maybe others too):
    assert {"access_token", "expires_in", "token_type", "issued_at"} <= set(
        token_response.keys()
    )

    assert token_response["access_token"] is not None
    assert token_response["token_type"] == "Bearer"
    assert token_response["expires_in"] and int(token_response["expires_in"]) > 0

    auth["response"] = token_response
    auth["access_token"] = token_response["access_token"]
    auth["token_type"] = token_response["token_type"]
    

#### NEW CODE
    

scenarios("./features/a__search_for_a_patient/search__application_restricted.feature")


@given(parsers.parse('path "{path}"'), target_fixture="full_url")
def set_url_path(path: str, pds_url: str) -> str:
    if path[0] != "/":
        path = f"/{path}"
    return f"{pds_url}{path}"


@given(parsers.parse("params\n{url_params:json}", extra_types=dict(json=json.loads)), target_fixture="url_params")
def set_url_parameters(url_params: dict) -> dict:
    return url_params


@when("GET request", target_fixture="response")
def make_get_request(full_url: str, auth: dict, url_params: dict) -> requests.Response:
    headers = add_auth_header(
        {
            "NHSD-SESSION-URID": "123",
            "X-Request-ID": str(uuid.uuid4()),
        },
        auth
    )
    
    response = requests.get(
        full_url,
        headers=headers,
        params=url_params,
    )
    return response


@then(parsers.parse("status {expected_status:d}"))
def assert_expected_status(expected_status: int, response: requests.Response):
    assert response.status_code == expected_status
    

@then(parsers.parse("response body\n{expected_response:json}", extra_types=dict(json=json.loads)), target_fixture="response_body")
def assert_expected_response_body(expected_response: dict, response: requests.Response) -> dict:
    
    
    valid_datetime = ""
    valid_integer = 102
    
    schema = {
        "type": "object",
        "properties": {
          "resourceType": {"type": "#string"},
          "timestamp":{"type": "#date-time"},
          "total": {"type": "#integer"},
          "_type": {"type": "#string"}
        }
    }
    
    # rename any key called "type", since this will confuse the jsonschema validator
    cleaned_response = copy.deepcopy(response.json())
    pytest.set_trace()
    
    cleaned_response["_type"] = cleaned_response.pop["type"]
    
    validate(instance=response.json(), schema=schema)  
    return expected_response