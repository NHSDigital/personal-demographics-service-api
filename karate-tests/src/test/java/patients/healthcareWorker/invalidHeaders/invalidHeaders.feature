Feature: Invalid request headers
  For any PDS requests made as a healthcare worker, you need:
    - a valid authorization header
    - a valid x-request-id header

  The errors are the same no matter the request - here we have some scenarios
  that just fire through the different requests that can be made.
    - Get patient by NHS number (no query params)
    - Search for a patient without NHS number (using query params)

    
Background:
  * def utils = call read('classpath:helpers/utils.feature')  
  * def nhsNumber = '9693632109'
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * url baseURL

Scenario Outline: Auth errors: patient <operation> - <diagnostics> 
  * def query = operation == 'search' ? { family: "Capon", gender: "male", birthdate: "eq1953-05-29" } : null
  
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * requestHeaders.authorization = headerValue == 'no_header' ? null : headerValue
  * configure headers = requestHeaders
  
  * path 'Patient'
  * params query 
  * method get
  * status 401
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
  * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/${errorResponse}.json`)
  * match response == expectedResponse

  Examples:
    | operation    | headerValue                | diagnostics                    | errorResponse   |
    | get          | no_header                  | Missing Authorization header   | ACCESS_DENIED   |
    | search       | no_header                  | Missing Authorization header   | ACCESS_DENIED   |
    | get          | ""                         | Empty Authorization header     | ACCESS_DENIED   |
    | search       | ""                         | Empty Authorization header     | ACCESS_DENIED   |
    | get          | Bearer abcdef123456789     | Invalid Access Token           | ACCESS_DENIED   |
    | search       | Bearer abcdef123456789     | Invalid Access Token           | ACCESS_DENIED   |

Scenario Outline: x-request-id errors: patient <operation> - <diagnostics> 
  * def query = operation == 'search' ? { family: "Capon", gender: "male", birthdate: "eq1953-05-29" } : null
  
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * requestHeaders['x-request-id'] = headerValue == 'no_header' ? null : headerValue  
  * configure headers = requestHeaders
  
  * path 'Patient'
  * params query 
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
  * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/${errorResponse}.json`)
  * match response == expectedResponse

  Examples:
    | operation    | headerValue                | diagnostics                                                                                 | errorResponse   |
    | get          | no_header                  | Invalid request with error - X-Request-ID header must be supplied to access this resource   | MISSING_VALUE   |
    | search       | no_header                  | Invalid request with error - X-Request-ID header must be supplied to access this resource   | MISSING_VALUE   |
    | get          | ""                         | Invalid value - '' in header 'X-Request-ID'                                                 | INVALID_VALUE   |
    | search       | ""                         | Invalid value - '' in header 'X-Request-ID'                                                 | INVALID_VALUE   |
    | get          | 1234                       | Invalid value - '1234' in header 'X-Request-ID'                                             | INVALID_VALUE   |
    | search       | 1234                       | Invalid value - '1234' in header 'X-Request-ID'                                             | INVALID_VALUE   |
