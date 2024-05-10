Feature: Patient search - Healthcare worker - error scenarios

  Background:
    * def utils = call read('classpath:helpers/utils.feature')  
    * def nhsNumber = '9693632109'
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * url baseURL
  
  Scenario: Patient search - Missing authorization header
    * requestHeaders.authorization = null
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 401
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def diagnostics = "Missing Authorization header"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
    * match response == expectedResponse
  
  Scenario: Patient search - Empty authorization header
    * requestHeaders.authorization = ""
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 401
   * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def diagnostics = "Empty Authorization header"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
    * match response == expectedResponse
  
  Scenario: Patient search - Invalid authorization header
    * requestHeaders.authorization = "Bearer abcdef123456789"
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 401
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def diagnostics = "Invalid Access Token"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
    * match response == expectedResponse

  Scenario: Patient search - Missing x-request-id header
    * requestHeaders['x-request-id'] = null
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 400
    * assert requestHeaders['x-correlation-id'] == karate.response.header('x-correlation-id')
    * def diagnostics = "Invalid request with error - X-Request-ID header must be supplied to access this resource"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
      
  Scenario: Patient search - Invalid x-request-id header
    * requestHeaders['x-request-id'] = "1234"
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 400
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def diagnostics = "Invalid value - '1234' in header 'X-Request-ID'"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')

  Scenario: Patient search - Empty x-request-id header
    * requestHeaders['x-request-id'] = ""
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 400
    * assert requestHeaders['x-correlation-id'] == karate.response.header('x-correlation-id')
    * def diagnostics = "Invalid value - '' in header 'X-Request-ID'"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')