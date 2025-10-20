@ignore
Feature: Update patient details

  Background:
    * url baseURL

  @invalidMethodCode 
  Scenario: Invalid Method error should be raised for restricted users
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
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse