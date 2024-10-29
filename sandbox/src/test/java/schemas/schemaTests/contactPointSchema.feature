Feature: Validator for the ContactPoint Schema

Background:
* json Period = karate.readAsString('classpath:schemas/Period.json')
* json contactPointSchema = karate.readAsString('classpath:schemas/ContactPoint.json')
* json OtherContactSystem = karate.readAsString('classpath:schemas/extensions/OtherContactSystem.json')

Scenario: Required fields only
* def requiredFields = {"system": "phone", "value": "077113451234"}
* match requiredFields == contactPointSchema

Scenario: All fields
* def allFields =
    """
    {
        "period": { "start": "2010-11-30", "end": "2016-03-25" },            
        "system": "phone",
        "value": "077113451234",
        "use": "mobile",
        "extension": [{
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-OtherContactSystem",
            "valueCoding": {
                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-OtherContactSystem",
                    "code": "extension",
                    "display": "display value"
            }
        }]
    }
    """
* match allFields == contactPointSchema