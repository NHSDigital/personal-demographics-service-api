@no-oas
Feature: Update patient details - not permitted for privileged-application-restricted users

Background:
  * def utils = karate.callSingle('classpath:helpers/utils.feature')
  * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
  * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
  * configure headers = requestHeaders 
  * url baseURL
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * configure retry = { count: 2, interval: 6000 }
  * retry until responseStatus != 503 && responseStatus != 502  
Scenario: Invalid Method error should be raised when privileged-application-restricted user try to update patient details
    * def nhsNumber = '9733162817'
    * path 'Patient', nhsNumber
    * method get
    * status 200

  # add emergency contact details
    * configure headers = call read('classpath:auth-jwt/app-restricted-headers.js')
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * def mobileNumber = '0788848687'
    * request read('classpath:patients/requestDetails/add/emergencyContact.json')
    * method patch
    * status 403
    * def display = "Cannot update resource with privileged-application-restricted access token"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse