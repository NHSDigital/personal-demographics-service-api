import pytest_bdd
from functools import partial
import uuid
import pytest
from tests.functional.data import patients
from tests.functional.data.patients import Patient
from tests.functional.data.updates import Update
from pytest_bdd import given


@pytest.fixture(scope='function')
def headers_with_authorization(_nhsd_apim_auth_token_data: dict,
                               add_asid_to_testapp: None) -> dict:
    """Assign required headers with the Authorization header"""

    access_token = _nhsd_apim_auth_token_data.get("access_token", "")

    headers = {
        "X-Request-ID": str(uuid.uuid1()),
        "X-Correlation-ID": str(uuid.uuid1()),
        "Authorization": f'Bearer {access_token}'
    }
    return headers


@pytest.fixture()
def patient() -> Patient:
    return patients.SELF


@given("I have another patient's NHS number", target_fixture="patient")
def patient_other() -> Patient:
    patient = patients.DEFAULT
    patient.update = Update(nhs_number=patient.nhs_number)
    return patient


@pytest.fixture()
def update(patient: Patient) -> Update:
    return patient.update


retrieve_scenario = partial(pytest_bdd.scenario, './features/patient_access_retrieve.feature')
update_scenario = partial(pytest_bdd.scenario, './features/patient_access_update.feature')


@retrieve_scenario('Patient can retrieve self')
def test_retrieve_self():
    pass

@retrieve_scenario('Patient cannot retrieve self with P5 authorisation level')
def test_retrieve_self_P5():
    pass

@retrieve_scenario('Patient cannot retrieve self with P0 authorisation level')
def test_retrieve_self_P0():
    pass

@retrieve_scenario('Patient cannot retrieve another patient')
def test_cannot_retrieve_another_patient():
    pass


@retrieve_scenario('Patient attempts to search for a patient')
def test_cannot_search_for_a_patient():
    pass


@retrieve_scenario('Patient cannot retrieve their record with an expired token')
def test_cannot_retrieve_with_expired_token():
    pass


@retrieve_scenario("Patient can retrieve their record with a refreshed token")
def test_can_retrieve_with_refreshed_token():
    pass


@update_scenario('Patient can update their record')
def test_can_update_their_record():
    pass


@update_scenario('Patient cannot update another patient')
def test_cannot_update_another_patient():
    pass


@update_scenario('Patient update uses incorrect path')
def test_cannot_update_incorrect_path():
    pass
