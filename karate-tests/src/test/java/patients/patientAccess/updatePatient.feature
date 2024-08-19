Feature: Patient updates their details

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')      
    * url baseURL
    * def p9number = '9912003071'
    * def p5number = '9912003072'

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

  @firsttest
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

    # patient can't remove their telecom entries
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
    * def newTelecom = { "id": "#(originalTelecom[9].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }
    * request { "patches": [{ "op": "replace", "path": "/telecom/9", "value": "#(newTelecom)" }]}
    * path 'Patient', p9number
    * method patch
    * status 200
    * assert originalTelecom.length == response.telecom.length
    * match response.telecom[*].id contains originalTelecom[9].id
    * def updatedObject = karate.jsonPath(response, "$.telecom[?(@.id=='" + originalTelecom[9].id + "')]")
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
