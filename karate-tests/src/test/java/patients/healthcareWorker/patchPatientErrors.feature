@sandbox
Feature: Patch patient errors - Healthcare worker access mode

  # These tests are only run against the sandbox at the moment - until we have a better 
  # way of managing test data in the integration environment
  
  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    
    * url baseURL
    * def nhsNumber = karate.get('nhsNumber', '9000000009')
    * path 'Patient', nhsNumber
    * method get
    * status 200
    
    * def patientObject = response
    * def etag = karate.response.header('etag')
    * def originalVersion = parseInt(response.meta.versionId)
    
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    
  Scenario: No patch operations
    * def diagnostics = "Invalid update with error - No patches found"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * path 'Patient', nhsNumber
    * request {}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Incorrect resource version
    * def diagnostics = "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number."
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')
    
    * def incorrectResourceVersion = originalVersion + 1
    * header If-Match = incorrectResourceVersion
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 412
    * match response == expectedBody

  Scenario: Invalid x-request-id header
    * def invalidUUID = "12345"
    * def diagnostics = "Invalid value - '" + invalidUUID + "' in header 'X-Request-ID'"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
    
    * def badHeaders = requestHeaders
    * badHeaders["x-request-id"] = invalidUUID
    * configure headers = badHeaders
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 400
    * match response == expectedBody