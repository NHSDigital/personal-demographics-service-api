Feature: Post Patient  
    
Background:
    Given I am a healthcare worker user
    
Scenario: Negative test - invalid request payload
    Given path "Patient"
    And request body: 
        {"blahblahblah":"blah"}
    When method POST
    Then status 400
    And response body:
        {
            "issue": [
                {
                "code": "required",
                "details": {
                    "coding": [
                    {
                        "code": "MISSING_VALUE",
                        "display": "Required value is missing",
                        "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                        "version": "1"
                    }
                    ]
                },
                "diagnostics": "Missing value - 'nhsNumberAllocation'",
                "severity": "error"
                }
            ],
            "resourceType": "OperationOutcome"
        }

Scenario: Valid request, basic payload
    Given path "Patient"
    And request body: 
        {
            "nhsNumberAllocation": "Done",
            "name": {
                "use": "L",
                "name.familyName": "Smith"
            },
            "registeringAuthority": {
                "regAuthorityType.code": "x",
                "regAuthorityType.codeSystem": "2.16.840.1.113883.2.1.3.2.4.16.20",
                "regOrganisation.root": "2.16.840.1.113883.2.1.4.3",
                "regOrganisation.extension": "RWF",
                "authorPersonID": "",
                "authorSystemID": "230811201324",
                "deathStatus": "",
                "deceasedTime": "",
                "overallUpdateMode": "create"
            }
        }
    When method POST
    Then status 201
    And expected_response template == read(valid_patient_post_response)
    And set expected_response['#nhsNumber'] = response['id']
    And set expected_response['#family'] = 'Smith'
    And ignore in response comparison the family name Id 
    And response body == expected_response


Scenario: The rate limit is tripped when POSTing new Patients (>5tps)
    When I post to the Patient endpoint more than 5 times per second
    Then I get a mix of 400 and 429 HTTP response codes
    And the 429 response bodies alert me that there have been too many Create Patient requests
