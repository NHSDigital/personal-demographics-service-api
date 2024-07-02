import pytest
import pytest_bdd

from functools import partial

from pytest_bdd import given

from tests.functional.data import patients
from tests.functional.data.patients import Patient
from tests.functional.data.updates import Update


@pytest.fixture()
def patient() -> Patient:
    return patients.SELF


@pytest.fixture()
def update(patient: Patient) -> Update:
    return patient.update


@given("I have another patient's NHS number", target_fixture="patient")
def patient_other() -> Patient:
    patient = patients.DEFAULT
    patient.update = Update(nhs_number=patient.nhs_number)
    return patient


auth_scenario = partial(pytest_bdd.scenario, './features/patient_access_authentication.feature')


@auth_scenario('Patient can retrieve self')
def test_retrieve_self():
    pass


@auth_scenario('Patient with P5 authorisation level cannot authenticate')
def test_retrieve_self_P5():
    pass


@auth_scenario('Patient with P0 authorisation level cannot authenticate')
def test_retrieve_self_P0():
    pass
