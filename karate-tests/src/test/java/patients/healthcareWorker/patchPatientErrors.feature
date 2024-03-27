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

    * def diagnostics = "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number."
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')
        
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 412
    * match response == expectedBody

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

    * def diagnostics = "Invalid update with error - If-Match header must be supplied to update this resource"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')    
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
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

    * def diagnostics = "Invalid patch: Operation `op` property is not one of operations defined in RFC-6902"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

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
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Patient not found
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def expectedBody = read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')

    * path 'Patient', '9111231130'
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 404
    * match response == expectedBody

  Scenario: Missing x-request-id header
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag

    * def expectedBody = read('classpath:mocks/stubs/errorResponses/MISSING_VALUE_x-request-id.json')
    
    * def badHeaders = requestHeaders
    * remove badHeaders.x-request-id
    * configure headers = badHeaders
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch - no address ID
    * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},{"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}]}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch - attempt to replace non-existent object
    * def diagnostics = "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
    * path 'Patient', nhsNumber
    * request
      """
      {"patches":[
        {"op":"replace","path":"/address/0/id","value":"456"},
        {"op":"replace","path":"/address/0/line","value":["2 Trevelyan Square","Boar Lane","Leeds"]},
        {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
      ]}
      """
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch - invalid address ID
    * def diagnostics = "Invalid update with error - no 'address' resources with object id 123456"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
    * path 'Patient', nhsNumber
    * request
      """
      {"patches":[
        {"op":"replace","path":"/address/0/id","value":"123456"},
        {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
        {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
      ]}
      """  
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch - invalid address ID only
    * def diagnostics = "Invalid update with error - no 'address' resources with object id 123456"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"replace","path":"/address/0/id","value":"123456"}]}
    * method patch
    * status 400
    * match response == expectedBody

  Scenario: Invalid patch - patient with no address
    * def nhsNumber = "9000000033"
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def etag = karate.response.header('etag')
    
    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
    * path 'Patient', nhsNumber
    * request 
    """
    {
      "patches":[
        {"op":"replace","path":"/address/0/id","value":"456"},
        {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
        {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
      ]
    }
    """
    * method patch
    * status 400
    * def diagnostics = "Invalid update with error - Invalid patch - index '0' is out of bounds"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
    * match response == expectedBody
 
  Scenario: Invalid patch - Patient with no address / Request without address ID
    * def nhsNumber = "9000000033"
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def etag = karate.response.header('etag')
    
    * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = requestHeaders
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag    
 
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},{"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}]}
    * method patch
    * status 400
    * match response == expectedBody