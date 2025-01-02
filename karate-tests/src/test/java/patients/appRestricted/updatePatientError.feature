Feature: Update patient details - not permitted for application-restricted users

Background:
  * def utils = karate.callSingle('classpath:helpers/utils.feature')
  * def accessToken = karate.callSingle('classpath:patients/appRestricted/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/appRestricted/app-restricted-headers.js')
  * configure headers = requestHeaders 
  * url baseURL
Scenario: Invalid Method error should be raised when app restricted user try to update patient details
    * def nhsNumber = '9733162817'
    * path 'Patient', nhsNumber
    * method get
    * status 200

  # add emergency contact details
    * configure headers = call read('classpath:patients/appRestricted/app-restricted-headers.js')
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * def mobileNumber = '0788848687'
    * request read('classpath:patients/requestDetails/add/emergencyContact.json')
    * method patch
    * status 403
    * def display = "Cannot update resource with Application-Restricted access token"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse