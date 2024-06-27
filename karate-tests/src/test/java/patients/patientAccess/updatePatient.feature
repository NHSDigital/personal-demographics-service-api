Feature: Patient updates their details

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')      
    * url baseURL
    * def p9number = '9912003071'

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

    * def newTelecom = { "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', p9number
    * request 
      """
        {"patches": [
          { "op":"test","path":"/telecom/0/id","value":"#(response.telecom[0].id)" }, 
          { "op": "remove", "path": "/telecom/0" },
          { "op": "add", "path": "/telecom/-", "value": "#(newTelecom)" }
        ]}
      """
    * method patch
    * status 200
    * def newValue = response.gender
    * match newValue == targetValue
    * match parseInt(response.meta.versionId) == originalVersion + 1


  # Scenario: Patient cannot update another patient
  #   Given I am a P9 user
  #   And scope added to product
  #   And I have another patient's NHS number

  #   When I update another patient's PDS record

  #   Then I get a 403 HTTP response code
  #   And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body
 
  # Scenario: Patient update uses incorrect path
  #   Given I am a P9 user
  #   And scope added to product

  #   When I update another patient's PDS record using an incorrect path

  #   Then I get a 403 HTTP response code
  #   And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body
