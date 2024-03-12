Feature: Validator for the General Practitioner Reference Schema

Background:
* json periodSchema = karate.readAsString('classpath:schemas/Period.json')
* json gpRefSchema = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')

Scenario: Required fields only
* def requiredFields = 
    """
    {
        "identifier": {
            "value": "1A2B3C4D5E"
        }
    }
    """
* match requiredFields == gpRefSchema

Scenario: All fields
* def allFields = 
    """
    {
        "id": "254406A3",
        "type": "Clinic",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "A20047",
            "period": { "start": "2005-03-05" }
        }
    }
    """
* match allFields == gpRefSchema