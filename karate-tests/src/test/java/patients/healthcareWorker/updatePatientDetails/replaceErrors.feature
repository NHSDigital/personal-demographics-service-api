@sandbox
Feature: Patch patient errors - Replace data

Demonstrates invalid "replace" operations on a patient resource.

Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * url baseURL
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * configure retry = { count: 2, interval: 6000 }
  * retry until responseStatus != 503

Scenario: Invalid patch - no address ID
  * def nhsNumber = '5900046192'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200

  * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')    
  * path 'Patient', nhsNumber
  * request 
    """
    {"patches":[
      {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
      {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
    ]}
    """
  * method patch
  * status 400
  * match response == expectedBody

Scenario: Invalid patch - attempt to replace non-existent object
  * def nhsNumber = '5900046192'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200

  * def diagnostics = "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')    
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
  * def nhsNumber = '5900046192'

  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200

  * def diagnostics = "Invalid update with error - no 'address' resources with object id '123456'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')     
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
  * def nhsNumber = '5900046192'

  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200

  * def diagnostics = "Invalid update with error - no 'address' resources with object id '123456'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')     
  * path 'Patient', nhsNumber
  * request {"patches":[{"op":"replace","path":"/address/0/id","value":"123456"}]}
  * method patch
  * status 400
  * match response == expectedBody

Scenario: Invalid patch - patient with no address
  * def nhsNumber = '5900059073'
  
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  
  * def diagnostics = "Invalid update with error - Invalid patch - index '0' is out of bounds"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
  
  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')      
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
  * match response == expectedBody

Scenario: Invalid patch - Patient with no address / Request without address ID
  * def nhsNumber = '5900059073'
  
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  
  * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')      

  * path 'Patient', nhsNumber
  * request {"patches":[{"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},{"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}]}
  * method patch
  * status 400
  * match response == expectedBody