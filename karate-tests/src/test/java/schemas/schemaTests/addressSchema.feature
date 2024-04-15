Feature: Validator for the Address Schema

Background:
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json addressSchema = karate.readAsString('classpath:schemas/Address.json')


Scenario: Required fields only
    * def sampleAddress = 
        """
        {
            "line": [
                "Flat 2",
                "The Road",
                "The Town",
                "The County"
            ]
        }
        """
    * match sampleAddress == addressSchema
    
Scenario: All fields
    * def sampleAddress = 
        """
        {
            "id": "102",
            "period": { "start": "2010-11-30", "end": "2016-03-25" },
            "use": "home",
            "text": "Second Home",
            "line": [
                "Flat 2",
                "The Road",
                "The Town",
                "The County"
            ],
            "postalCode": "G73 4RW"
        }
        """
    * match sampleAddress == addressSchema
    