Feature: Validator for the Human Name Schema

Background:
* json Period = karate.readAsString('classpath:schemas/Period.json')
* json humanNameSchema = karate.readAsString('classpath:schemas/HumanName.json')


Scenario: Required fields only
* def requiredFields = 
    """
    {
        "given": ["John"],
        "family": "Smith"
    }
    """
* match requiredFields == humanNameSchema

Scenario: All fields
* def allFields =
    """
    {
        "id": "anyoldstring1234",
        "use": "usual",
        "given": ["John", "Towner"],
        "family": "Williams",
        "prefix": ["Mr", "Doctor"],
        "suffix": ["KBE"]
    }
    """
* match allFields == humanNameSchema