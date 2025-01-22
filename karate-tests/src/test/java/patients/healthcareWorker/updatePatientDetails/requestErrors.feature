@sandbox
Feature: Patch patient errors - Healthcare worker access mode
  
  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    
    * url baseURL
    * def nhsNumber = '5900059073'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    
    * def patientObject = response
    * def etag = karate.response.header('etag')

  Scenario: No patch operations
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def diagnostics = "Invalid update with error - No patches found"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * path 'Patient', nhsNumber
    * request {}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Incorrect resource version
    * def originalVersion = response.meta.versionId
    
    * header Content-Type = "application/json-patch+json"
    * def incorrectResourceVersion = originalVersion + 1
    * header If-Match = 'W/"' + incorrectResourceVersion + '"'
        
    * path 'Patient', nhsNumber
    * request 
    """
    {"patches":[
      {"op":"test","path":"/name/0/id", "value": "#(response.name[0].id)"},
      {"op":"remove","path":"/name/0/suffix/0"}
    ]}
    """
    * method patch
    * status 409
    * match response == read('classpath:mocks/stubs/errorResponses/RESOURCE_VERSION_MISMATCH.json')

  Scenario: Invalid x-request-id header
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

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
    
  Scenario: Missing If-Match header
    * header Content-Type = "application/json-patch+json"

    * def diagnostics = "Invalid request with error - If-Match header must be supplied to update this resource"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')    
    
    * path 'Patient', nhsNumber
    * request
      """
      {"patches":[
        {"op":"test","path":"/name/0/id", "value": "#(response.name[0].id)"},
        {"op":"remove","path":"/name/0/suffix/0"}
      ]}
      """
    * method patch
    * status 412
    * match response == expectedBody
    
  Scenario: Invalid content-type header
    * header Content-Type = "application/bananas"
    * header If-Match = etag

    * def expectedBody = read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json')

    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def diagnostics = "Invalid value - 'bad_value' in field '0/op'"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')

    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"bad_value","path":"not a path"}]}
    * method patch
    * status 400
    * match response == expectedBody
    
  Scenario: Invalid NHS Number
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_RESOURCE_ID.json')

    * path 'Patient', '9000000000'
    * request
      """
      {"patches":[
        {"op":"test","path":"/name/0/id", "value": "#(response.name[0].id)"},
        {"op":"remove","path":"/name/0/suffix/0"}
      ]}
      """
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Patient not found
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def expectedBody = read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')

    * path 'Patient', '9111231130'
    * request 
      """
      {"patches":[
        {"op":"test","path":"/name/0/id", "value": "#(response.name[0].id)"},
        {"op":"remove","path":"/name/0/suffix/0"}
      ]}
      """
    * method patch
    * status 404
    * match response == expectedBody

  Scenario: Missing x-request-id header
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def diagnostics = "Invalid request with error - X-Request-ID header must be supplied to access this resource"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
    
    * def badHeaders = requestHeaders
    * remove badHeaders.x-request-id
    * configure headers = badHeaders
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 400
    * match response == expectedBody