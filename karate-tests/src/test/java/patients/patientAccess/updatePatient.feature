Feature: Patient updates their details

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')      
    * url baseURL
    * def p9number = '9912003071'
    * def p5number = '9912003072'
    # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
    * configure retry = { count: 2, interval: 6000 }
    * retry until responseStatus != 503

  Scenario: Patient cannot update their gender
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)

    * def currentValue = response.gender
    * def targetValue = utils.pickDifferentOption(['male', 'female', 'unknown'], currentValue)

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', p9number
    * request {"patches": [{ "op": "replace", "path": "/gender", "value": "#(targetValue)" }]}
    * method patch
    * status 400
    * def diagnostics = 'Invalid update with error - This user does not have permission to update the fields in the patches provided.'
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  Scenario: Patient can update their contact details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def originalTelecom = response.telecom

    # patient can't remove their non mobile telecom entries
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * path 'Patient', p9number
    * request { "patches": [{ "op": "test", "path": "/telecom/0/id", "value": "#(response.telecom[0].id)" }, { "op": "remove", "path": "/telecom/0"} ]}
    * method patch
    * status 400
    
    # "replace" will update the telecom object we identify
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * def mobileIndex = utils.getIndexOfFirstMobile(originalTelecom)
    * def newTelecom = { "id": "#(originalTelecom[mobileIndex].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }
    * request { "patches": [{ "op": "replace", "path": "#('/telecom/' + mobileIndex)", "value": "#(newTelecom)" }]}
    * path 'Patient', p9number
    * method patch
    * status 200
    * assert originalTelecom.length == response.telecom.length
    * match response.telecom[*].id contains originalTelecom[mobileIndex].id
    * def updatedObject = karate.jsonPath(response, "$.telecom[?(@.id=='" + originalTelecom[mobileIndex].id + "')]")
    * match updatedObject[0] == newTelecom

  Scenario: Patient cannot update another patient
    # same "replace" operation as in previous test, but this time on a different patient
    # just as a patient can't get another patient, they can't patch another patient either
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = "W/\"1\""
    * def newTelecom = { "id": "#(originalTelecom[0].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }
    * request { "patches": [{ "op": "replace", "path": "/telecom/0", "value": "#(newTelecom)" }]}
    * path 'Patient', p5number
    * method patch
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')



  Scenario: Send empty field on the update - communication Language code
    * def p9number = '9733162930'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def communicationUrl = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication"
    * def commLanguageDtls = response.extension.find(x => x.url == communicationUrl)
    # Test fails if the patient's communication language details are not available in the response 

    * if (commLanguageDtls == null) {karate.fail('No value found for NHS communication, stopping the test.')}
    * def commLanguageDtlsIndex = response.extension.findIndex(x => x.url == communicationUrl)
    * def communicationPath =  "/extension/" + commLanguageDtlsIndex
    
    # Empty value on communication extension
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', p9number
    * def requestbody = 
    """
      {
        "patches": [
          {
            "op": "test",
            "path": "#(communicationPath)",
            "value":{
              "url": "#(communicationUrl)",
              "extension":[
                  {
                  "url": "language",
                  "valueCodeableConcept": {
                          "coding": " "}
              },
              {
                  "url": "interpreterRequired",
                  "valueBoolean": false
              }]
              
          }
          },
            { "op": "remove", "path": "#(communicationPath)" }
        ]
      }
        """
      * request requestbody  
      * method patch
      * status 400 
      * def display = 'Patient cannot perform this action'
      * def diagnostics = "Invalid update with error - Invalid patch - {'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication', 'extension': [{'url': 'language', 'valueCodeableConcept': {'coding': [{'system': 'https://fhir.hl7.org.uk/CodeSystem/UKCore-HumanLanguage', 'version': '1.0.0', 'code': 'fr', 'display': 'French'}]}}, {'url': 'interpreterRequired', 'valueBoolean': True}]} (<class 'dict'>) is not equal to tested value {'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication', 'extension': [{'url': 'language', 'valueCodeableConcept': {'coding': ' '}}, {'url': 'interpreterRequired', 'valueBoolean': False}]} (<class 'dict'>)"
      * match response == read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')     
  

  Scenario: Patient can update their emergency contact details and place of birth
    * def p9number = '5900069176'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def placeOfBirthDls = read('classpath:patients/requestDetails/add/placeOfBirth.json')
    * def placeOBirthUrl = placeOfBirthDls.patches[0].value.url
    * def originalTelecom = response.contact[0].telecom[0].value
    * def contactID = response.contact[0].id
    * def relationshipDetails =  response.contact[0].relationship
    * def pobDetails = response.extension.find(x => x.url == placeOBirthUrl)
    * def pobDistrict = pobDetails.valueAddress.district
    * def pobcountry = pobDetails.valueAddress.country
    * def pobIndex = response.extension.findIndex(x => x.url == placeOBirthUrl)
    * def pobPath =  "/extension/" + pobIndex

    # update emergency contact details
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * def newMobileNumber = faker.phoneNumber()
    * path 'Patient', p9number
    * def requestbody =
    """
    {
      "patches":[
        {"op":"replace",
        "path":"/contact/0",
        "value":{
          "id": "#(contactID)",
          "relationship":"#(relationshipDetails)",
          "telecom":[
            {"system":"phone",
            "value":"#(newMobileNumber)"}
            ]}}]}
     """ 
    * request requestbody      
    * method patch
    * status 200
    * def contactDetails = karate.filter(response.contact, function(x){ return x.id == contactID && x.telecom[0].system == 'phone'})
    * match contactDetails[0].telecom[0].value == newMobileNumber
    * match parseInt(response.meta.versionId) == originalVersion + 1

    #update place of birth details
    * def cityName = faker.cityName()
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', p9number
    * request 
    """
    {
      "patches":[
        {"op":"replace",
        "path":"#(pobPath)",
        "value":{
          "url": "#(placeOBirthUrl)",
        "valueAddress": {
                "city": "#(cityName)",
                "district": "#(pobDistrict)",
                "country": "#(pobcountry)"
            }
        }}]}
     """  
    * method patch
    * status 200  
    * def updatedPobCity = response.extension[pobIndex].valueAddress.city
    * match updatedPobCity == cityName
    * match parseInt(response.meta.versionId) == originalVersion + 2

  Scenario: Patient can add and remove nominated pharmacy

    * def p9numberForPharmacy = '9446041481'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9numberForPharmacy, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * def requestBody = read('classpath:patients/requestDetails/add/nominatedPharmacy.json')
    * def nominatedPharmacyUrl = requestBody.patches[0].value.url
    * def utils = call read('classpath:helpers/utils.feature')
    
    * def removeNominatedPharmacy =
    """
    function(body) {
    var result = karate.call('classpath:helpers/patchRequest.feature', {
        baseURL: baseURL,
        requestBody: body,
        endpoint: 'Patient/' + p9numberForPharmacy,
        etag: karate.response.header('Etag')
    });
    return result
    }
    """

    * configure headers = requestHeaders
    * path 'Patient', p9numberForPharmacy
    * method get
    * status 200

    # Remove nominated pharmacy if already exists. Failed pipelines can leave data in an incorrect state
    * def pharmacyIndex = response.extension ? response.extension.findIndex(x => x.url == nominatedPharmacyUrl) : null
    * def pharmacyPath =  "/extension/" + pharmacyIndex
    * def pharmacyDetails = response.extension ? response.extension.find(x => x.url == nominatedPharmacyUrl) : null
    * def body = utils.buildRemovePatchBody(pharmacyPath, pharmacyDetails)
    * def response = (pharmacyDetails == null) ? { body: response, responseHeaders: responseHeaders } : removeNominatedPharmacy(body)
    
    # add nominated pharmacy
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', p9numberForPharmacy
    * request requestBody
    * method patch
    * status 200 
    * def idAfterPharmacyAdd = response.meta.versionId
    * def pharmacyDetails = response.extension.find(x => x.url == nominatedPharmacyUrl)
    
    # Test fails if the patient's nominated pharmacy is not present in the record
    * if (pharmacyDetails == null) {karate.fail('No value found for Nominated Pharmacy, stopping the test.')}
    * def pharmacyIndex = response.extension.findIndex(x => x.url == nominatedPharmacyUrl)
    * def pharmacyPath =  "/extension/" + pharmacyIndex
    
     # remove nominated pharmacy details
    * def body = utils.buildRemovePatchBody(pharmacyPath, pharmacyDetails)
    * def response = removeNominatedPharmacy(body)
    * match parseInt(response.response.meta.versionId) == parseInt(idAfterPharmacyAdd)+ 1
    * match response.response.extension[0] == '#notpresent'

  Scenario: Patient can add temporary address and remove it

    * def p9numberForAddress = '9733162868'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9numberForAddress, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def utils = call read('classpath:helpers/utils.feature')
    
    * def removeTemporaryAddress =
    """
    function(body) {
    var result = karate.call('classpath:helpers/patchRequest.feature', {
        baseURL: baseURL,
        requestBody: body,
        endpoint: 'Patient/' + p9numberForAddress,
        etag: karate.response.header('Etag')
    });
    return result
    }
    """
    
    * path 'Patient', p9numberForAddress
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)

    # Remove temporary address if already exists. Failed pipelines can leave data in an incorrect state
    * def tempAddressIndex = response.address ? response.address.findIndex(x => x.use == "temp") : null
    * def tempAddressPath =  "/address/" + tempAddressIndex
    * def tempAddressDetails = response.address ? response.address.find(x => x.use == "temp") : null
    * def body = utils.buildRemovePatchBody(tempAddressPath, tempAddressDetails)
    * def response = (tempAddressDetails == null) ? { body: response, responseHeaders: responseHeaders } : removeTemporaryAddress(body)

    * def randomAddress = utils.randomTempAddress()
    * def tempAddress = randomAddress
   
    # add temp address
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', p9numberForAddress
    * def requestBody = 
    """
      {
        "patches":
        [
            {
                "op": "add",
                "path": "/address/-",
                "value": "#(tempAddress)"
            }
        ]
    }
    """
    * request requestBody
    * method patch
    * status 200 
    * def idAfterTempAddress = response.meta.versionId
    * def tempAddressDetails = response.address.find(x => x.use == "temp")
   
    # Test fails if the patient's temp address details are not present in the record
    * if (tempAddressDetails == null) {karate.fail('No value found for temporary address, stopping the test.')}
    * def addressIndex = response.address.findIndex(x => x.use == "temp")
    * def tempAddressPath =  "/address/" + addressIndex
    
     # remove temp address details
    * def body = utils.buildRemovePatchBody(tempAddressPath, tempAddressDetails)
    * def response = removeTemporaryAddress(body)
    * match parseInt(response.response.meta.versionId) == parseInt(idAfterTempAddress)+ 1
    * match response.response.address[1] == '#notpresent'
