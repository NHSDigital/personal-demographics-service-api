from dataclasses import dataclass
from tests.functional.data.responses import RESPONSES


@dataclass
class Patient:
    nhs_number: str = ''
    demographic_details: dict = None
    expected_response: dict = None


DEFAULT = Patient(nhs_number='9693632109')
WITH_RELATED_PERSON = Patient(nhs_number='9693633679', expected_response=RESPONSES['Related person'])
