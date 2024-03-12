Feature: Validator for the Patient NHS Number Allocation Schema

Background:
* json periodSchema = karate.readAsString('classpath:schemas/Period.json')
* json addressSchema = karate.readAsString('classpath:schemas/Address.json')
* json humanNameSchema = karate.readAsString('classpath:schemas/HumanName.json')
* json contactPointSchema = karate.readAsString('classpath:schemas/ContactPoint.json')
* json generalPractitionerSchema = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
* json schema = karate.readAsString('classpath:schemas/PatientNhsNumberAllocation.json')

Scenario: Required fields only
* def requiredFields = 
    """
    {
        "resourceType": "Patient",
        "gender": "unknown",
        "name": [{
        "given": ["John"],
        "family": "Smith"
        }],
        "address": [{
            "line": [
                "Flat 2",
                "The Road",
                "The Town",
                "The County"
            ]
        }],
        "birthDate": "20-04-2004"
    }
    """
* match requiredFields == schema