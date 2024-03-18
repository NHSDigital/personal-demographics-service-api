Feature: Create a patient - Healthcare worker access mode

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')
    
    # the same registeringAuthority object is included in every request
    * def registeringAuthority = 
    """
    {
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
    """

    # the addressSchema used for the create responses is not the same as what's defined elsewhere, so 
    # we'll use this schema until the schemas are harmonised...
    * def addressSchema = 
    """
    {
        "id": "#regex([0-9A-Z]+)",
        "line": [
            "#string"
        ],
        "period": {
            "start": "#? utils.isTodaysDate(_)"
        },
        "postalCode": "#? utils.isValidPostCode(_)",
        "use": "#regex(home)"
    }
    """

    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders  
    * url baseURL

    # we have to chill out a bit between requests in case we trigger the spike alert policy :-(
    * eval utils.sleep(2)

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
        "registeringAuthority": "#(registeringAuthority)"
    }
    """
    * path "Patient"
    * request body
    * method post
    * status 201
    * def nhsNumber = response.id
    * def expectedResponse = read('classpath:stubs/patient/new-nhs-number-response-template.json')
    * match response == expectedResponse

Scenario: Create a record for a new patient, demographics match found
# Given a user submits a 'Create a record for a new patient' request
# When a single exact match is found
# Then a response is returned to the user containing the found NHS number
# 200 response with the following description:
# Unable to create new patient.  NHS number <NHS number> found for supplied demographic data
    * def address = faker.streetAddress()
    * def postCode = faker.postCode()
    
    * def familyName = 'Karate-test-' + utils.randomInt()
    * def birthTime = utils.getRandomBirthDate().replaceAll("-","")
    * def body = 
    """
    {
        "nhsNumberAllocation": "Done",
        "name": {
            "use": "L",
            "name.familyName": "#(familyName)",
            "name.givenName": ["Zebedee"]
        },
        "gender": {
            "gender.code": "1"
        },
        "birthTime": {
            "birthTime.value": "#(birthTime)"},
        "address": {
            "use": "H",
            "address.postalCode": "#(postCode)",
            "address.AddressKey": "205",
            "address.addr.line1" : "#(address)"
        },
        "registeringAuthority": "#(registeringAuthority)"
    }
    """

    # first request works because the demographics are unique
    * path "Patient"
    * request body
    * method post
    * status 201
    * def nhsNumber = response.id
    * def expectedResponse = read('classpath:stubs/patient/new-nhs-number-response-template.json')
    * match response == expectedResponse
    * match response.address[0].line[0] == address
    * match response.address[0].postalCode == postCode

    * eval utils.sleep(1)

    # second request fails because the same demographics are used, and a match is found
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders
    * path "Patient"
    * request body
    * method post
    * status 200
    * match response == read('classpath:stubs/patient/errorResponses/single_match_found.json')

Scenario: Negative path: invalid request body
    * path "Patient"
    * request { bananas: "in pyjamas" }
    * method post
    * status 400
    * def diagnostics = response.issue[0].diagnostics
    * match response == read('classpath:stubs/patient/errorResponses/missing_value.json')
