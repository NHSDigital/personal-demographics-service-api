from dataclasses import dataclass


@dataclass
class Patient:
    nhs_number: str = ''
    demographic_details: dict = None


DEFAULT = Patient(nhs_number='9693632109')
