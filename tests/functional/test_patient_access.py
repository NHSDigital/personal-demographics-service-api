import pytest_bdd

from functools import partial


auth_scenario = partial(pytest_bdd.scenario, './features/patient_access_authentication.feature')


@auth_scenario('Patient with P5 authorisation level cannot authenticate')
def test_retrieve_self_P5():
    pass


@auth_scenario('Patient with P0 authorisation level cannot authenticate')
def test_retrieve_self_P0():
    pass
