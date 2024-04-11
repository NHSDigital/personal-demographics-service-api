Feature: Get a patient - Healthcare worker - error scenarios

These tests authenticate as one of the available test healthcare workers,
darren.mcdrew@nhs.net

Background:
  * def utils = call read('classpath:helpers/utils.feature')  
  * def nhsNumber = '9693632109'
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * url baseURL

Scenario: Healthcare worker using deprecated url
  # Ask David what this scenario is all about
  * configure headers = requestHeaders 
  * url utils.buildDeprecatedURL()
  * path 'Patient', nhsNumber
  * method get
  * status 404
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)

Scenario: Attempt to retrieve a patient with missing authorization header
  * remove requestHeaders.authorization
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 401
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
  * def diagnostics = "Missing Authorization header"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/access_denied.json')
  * match response == expectedResponse

Scenario: Attempt to retrieve a patient with an empty authorization header
  * set requestHeaders.authorization = ""
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 401
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def diagnostics = "Empty Authorization header"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/access_denied.json')
  * match response == expectedResponse

Scenario: Attempt to retrieve a patient with an invalid authorization header
  * set requestHeaders.authorization = "Bearer abcdef123456789"
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 401 
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def diagnostics = "Invalid Access Token"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/access_denied.json')
  * match response == expectedResponse
  
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
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/invalid_value.json')

Scenario: Attempt to retrieve a patient with an invalid role
  * set requestHeaders.NHSD-Session-URID = "invalid"
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def diagnostics = "Invalid value - 'invalid' in header 'NHSD-Session-URID'. Refer to the guidance for this header in our API Specification https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/invalid_value.json')

Scenario: Attempt to retrieve a patient without Request ID header
  * remove requestHeaders.x-request-id
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 400
  * assert requestHeaders['x-correlation-id'] == karate.response.header('x-correlation-id')
  * def diagnostics = "Invalid request with error - X-Request-ID header must be supplied to access this resource"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/missing_value.json')

Scenario: Attempt to retrieve a patient with an invalid X-Request-ID
  * set requestHeaders.x-request-id = "1234"
  * configure headers = requestHeaders
  * path 'Patient', nhsNumber
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def diagnostics = "Invalid value - '1234' in header 'X-Request-ID'"
  * def expectedResponse = read('classpath:stubs/patient/errorResponses/invalid_value.json')