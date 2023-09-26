from dataclasses import dataclass


@dataclass
class Patient:
    nhs_number: str = ''
    demographic_details: dict = None


DEFAULT = Patient('9693632109')

SEARCHABLE = Patient(nhs_number='9693632117',
                     demographic_details={"family": "Capon", "gender": "male", "birthdate": "eq1953-05-29"})

SENSITIVE = Patient(nhs_number='9693632125',
                    demographic_details={"family": "Godsoe", "gender": "male", "birthdate": "eq1936-02-24"})

UNKNOWN_GENDER = Patient(nhs_number='9693632966',
                         demographic_details={"family": "Massam", "birthdate": "eq1920-08-11"})

DOB_RANGE = Patient(nhs_number="9693632966",
                    demographic_details={"family": "Massam", "birthdate": "le1920-08-11"})
