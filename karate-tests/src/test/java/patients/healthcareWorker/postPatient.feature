Feature: Create a patient - Healthcare worker access mode

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders  
    * url baseURL

Scenario: Post patient, required request data only
    * def familyName = 'Karate-test-' + utils.randomInt()
    * def body =
    """
    {
        "nhsNumberAllocation": "Done",
        "name": {
            "use": "L",
            "name.familyName": "#(familyName)"
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
    """
    * path "Patient"
    * request body
    * method post
    * status 201
    * def nhsNumber = response.id
    * def expectedResponse = read('classpath:stubs/patient/new-nhs-number-response-template.json')
    * match response == expectedResponse


Scenario: Negative path: invalid request body
    * path "Patient"
    * request { bananas: "in pyjamas" }
    * method post
    * status 400
    * def diagnostics = response.issue[0].diagnostics
    * match response == read('classpath:stubs/patient/errorResponses/missing_value.json')
