Feature: Get a patient - Healthcare worker - error scenarios

These tests authenticate as one of the available test healthcare workers,
darren.mcdrew@nhs.net

Background:
  * def utils = call read('classpath:helpers/utils.feature')  
  * def nhsNumber = '9693632109'
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * url baseURL

Scenario: Attempt to retrieve a patient without stating a role
    # we use a different user for this scenario - a healthcare worker with multiple roles, 656005750104
    * def accessToken = karate.call('classpath:patients/healthcareWorker/auth-redirect.feature', {userID: '656005750104'}).accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 400
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def diagnostics = "Invalid value - '' in header 'NHSD-Session-URID'. Refer to the guidance for this header in our API Specification https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  
  Scenario: Attempt to retrieve a patient with an invalid role
    * set requestHeaders.NHSD-Session-URID = "invalid"
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 400
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def diagnostics = "Invalid value - 'invalid' in header 'NHSD-Session-URID'. Refer to the guidance for this header in our API Specification https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  