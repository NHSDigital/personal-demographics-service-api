@no-oas
Feature: Updating Patient's details(Healthcare worker access) - empty address lines
Background:
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')

    #generate patient with both home and temporary address and telecom details
    * def birthDate = utils.randomBirthDate()
    * def generateBothAddresses =
        """
        function(earliestStartDate) {
            const homeAddress = karate.call('classpath:helpers/utils.feature').randomAddress(earliestStartDate)
            const tempAddress = karate.call('classpath:helpers/utils.feature').randomTempAddress()
            return [homeAddress, tempAddress]
        }
        """
    * def familyName = "ToRemove"
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def suffix = ["PhD"]
    * def gender = utils.randomGender()
    * def telecomValue = faker.mobileNumber()
    * def telecomUse = "mobile"
    * def address = generateBothAddresses(birthDate)
    * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatientWithMaximalData') { expectedStatus: 201 } 
    
Scenario: Updating temporary address response should show empty address lines
    * def nhsNumber = createPatientResponse.response.id 
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]
    * def originalVersion = patientDetails.response.meta.versionId 
    * def randomAddress = utils.randomTempAddress()
    * def address = randomAddress
    * def tempAddressDetails = utils.removeNullsFromAddress(patientDetails.response.address.find(x => x.use == "temp"))
    * if (tempAddressDetails == null) {karate.fail('No value found for temporary address, stopping the test.')}
    * def tempAddressIndex = patientDetails.response.address.findIndex(x => x.use == "temp")
    * def path =  "/address/" + tempAddressIndex
    * def testOpValue = tempAddressDetails
  
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * def requestBody = read('classpath:patients/requestDetails/add/addressUpdate.json')
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}   
    * match parseInt(response.meta.versionId) == parseInt(originalVersion)+ 1
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true

Scenario: Updating contact details response should show empty address lines
    * def nhsNumber = createPatientResponse.response.id 
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalTelecom = patientDetails.response.telecom
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * def mobileIndex = utils.getIndexOfFirstMobile(originalTelecom)
    * def newTelecom = { "id": "#(originalTelecom[mobileIndex].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.mobileNumber())" }
    * def requestBody = 
    """
    { "patches": [{ "op": "replace", "path": "#('/telecom/' + mobileIndex)", "value": "#(newTelecom)" }]}
    """
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * assert originalTelecom.length == response.telecom.length
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true
