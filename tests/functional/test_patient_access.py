import pytest_bdd
from functools import partial
import uuid
import pytest

# from tests.functional.utils.helper import (
#     generate_random_phone_number,
#     get_add_telecom_phone_patch_body,
# )

AUTH_PATIENT = {
    "api_name": "personal-demographics-service",
    "access": "patient",
    "level": "P9",
    "login_form": {"username": "9912003071"},
    "force_new_token": True
}

AUTH_PATIENT_P5 = {
    "api_name": "personal-demographics-service",
    "access": "patient",
    "level": "P5",
    "login_form": {"username": "9912003071"},
}

AUTH_PATIENT_p5 = {
    "api_name": "personal-demographics-service",
    "access": "patient",
    "level": "p5",
    "login_form": {"username": "9912003071"},
}

AUTH_PATIENT_P0 = {
    "api_name": "personal-demographics-service",
    "access": "patient",
    "level": "P0",
    "login_form": {"username": "9912003071"},
}

TEST_PATIENT_ID = "9912003071"


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

    return headers


retrieve_scenario = partial(pytest_bdd.scenario, './features/patient_access_retrieve.feature')
update_scenario = partial(pytest_bdd.scenario, './features/patient_access_update.feature')


@retrieve_scenario('Patient can retrieve self')
def test_retrieve_self():
    pass


@retrieve_scenario('Patient cannot retrieve another patient')
def test_cannot_retrieve_another_patient():
    pass


@retrieve_scenario('Patient retrieve uses incorrect path')
def test_cannot_retrieve_incorrect_path():
    pass


@update_scenario('Patient cannot update another patient')
def test_cannot_update_another_patient():
    pass


@update_scenario('Patient update uses incorrect path')
def test_cannot_update_incorrect_path():
    pass
