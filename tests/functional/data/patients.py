from dataclasses import dataclass
from tests.functional.data.updates import Update


@dataclass
class Patient:
    nhs_number: str = ''
    demographic_details: dict = None
    update: Update = None


DEFAULT = Patient(nhs_number='9693632109')
SELF = Patient(nhs_number='9912003071',
               update=Update(nhs_number='9912003071',
                             path='telecom/0'))
SELF_WITH_RELATED_PERSON = Patient(nhs_number='9472063845')
WITH_RELATED_PERSON = Patient(nhs_number='9693633679')
