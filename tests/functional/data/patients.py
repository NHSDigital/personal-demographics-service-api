from dataclasses import dataclass
from tests.functional.data.updates import Update
from ..configuration.config import SPINE_HOSTNAME


@dataclass
class Patient:
    nhs_number: str = ''
    demographic_details: dict = None
    expected_response: dict = None
    update: Update = None


DEFAULT = Patient(nhs_number='9693632109')
SELF = Patient(nhs_number='9912003071',
               update=Update(nhs_number='9912003071',
                             path='telecom/0'))
SELF_1 = Patient(nhs_number='9472063845')

related_person_response = {
        "entry": [
            {
                "fullUrl": f"{SPINE_HOSTNAME}/personal-demographics/FHIR/R4/Patient/9693633679/RelatedPerson/qWyGt",
                "resource": {
                    "active": True,
                    "id": "qWyGt",
                    "patient": {
                        "identifier": {
                            "system": "https://beta.api.digital.nhs.uk",
                            "value": "9693633687"
                        },
                        "reference": "https://beta.api.digital.nhs.uk/Patient/9693633687",
                        "type": "Patient"
                    },
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "code": "SPS",
                                    "display": "spouse",
                                    "system": "http://hl7.org/fhir/ValueSet/relatedperson-relationshiptype"
                                },
                                {
                                    "code": "Personal",
                                    "display": "Personal relationship with the patient",
                                    "system": "https://fhir.nhs.uk/R4/CodeSystem/UKCore-AdditionalRelatedPersonRole"
                                },
                                {
                                    "code": "N",
                                    "display": "Next-of-Kin",
                                    "system": "http://hl7.org/fhir/ValueSet/relatedperson-relationshiptype"
                                }
                            ]
                        }
                    ],
                    "resourceType": "RelatedPerson"
                }
            }
        ],
        "resourceType": "Bundle",
        "total": 1,
        "type": "searchset"
    }
WITH_RELATED_PERSON = Patient(nhs_number='9693633679', expected_response=related_person_response)
SELF_WITH_RELATED_PERSON = Patient(nhs_number='9472063845')
