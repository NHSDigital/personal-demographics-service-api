from .utils import helpers
import pytest
import uuid
from typing import Dict
from tests.functional.test_user_restricted import (
    retrieve_scenario,
    search_scenario,
    related_person_scenario,
    status_scenario
)

from pytest_nhsd_apim.auth_journey import AuthorizationCodeConfig, AuthorizationCodeAuthenticator

pytestmark = pytest.mark.smoke_test


@retrieve_scenario('Healthcare worker can retrieve patient')
def test_retrieve_patient():
    pass


@search_scenario('Healthcare worker can search for patient')
def test_search_patient():
    pass


@related_person_scenario('Retrieve a related person')
def test_retrieve_related_person():
    pass


@status_scenario('Healthcheck endpoint')
def test_healthcheck():
    pass


@pytest.fixture()
def identity_service_base_url():
    return "https://int.api.service.nhs.uk/oauth2-mock"


@pytest.fixture()
def headers_with_authorization(apigee_environment: str,
                               nhsd_apim_config: dict,
                               _test_app_credentials: dict,
                               identity_service_base_url: str,
                               user_directory: dict) -> Dict[str, str]:
    healthcare_worker_auth = user_directory['healthcare_worker']

    user_restricted_app_config = AuthorizationCodeConfig(
            environment=apigee_environment,
            org=nhsd_apim_config["APIGEE_ORGANIZATION"],
            callback_url="https://example.org/callback",
            identity_service_base_url=identity_service_base_url,
            client_id=_test_app_credentials["consumerKey"],
            client_secret=_test_app_credentials["consumerSecret"],
            scope="nhs-cis2",
            login_form=healthcare_worker_auth['login_form']
        )

    authenticator = AuthorizationCodeAuthenticator(config=user_restricted_app_config)

    token_response = authenticator.get_token()
    assert "access_token" in token_response
    access_token = token_response["access_token"]

    role_id = helpers.get_role_id_from_user_info_endpoint(access_token,
                                                          identity_service_base_url)

    headers = {
        "X-Request-ID": str(uuid.uuid1()),
        "X-Correlation-ID": str(uuid.uuid1()),
        "NHSD-Session-URID": role_id,
        "Authorization": f'Bearer {access_token}'
    }

    return headers
