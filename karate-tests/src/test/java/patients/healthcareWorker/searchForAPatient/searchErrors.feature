@ignore
Feature: Search for a patient - error scenarios

  Background:
    * def utils = call read('classpath:helpers/utils.feature')  
    * def nhsNumber = '9693632109'
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * url baseURL
  
  Scenario: Missing authorization header
    * remove requestHeaders.authorization
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * params { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
    * method get
    * status 401
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def diagnostics = "Missing Authorization header"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
    * match response == expectedResponse
  
    # Given I am a healthcare worker user
    # And I don't have an Authorization header

    # When I search for the patient's PDS record

    # Then I get a 401 HTTP response code
    # And the X-Request-ID response header matches the request
    # And the X-Correlation-ID response header matches the request
    # And the response body is the Missing Authorization header response
    # And the response body does not contain id

  # Scenario: Empty authorization header
  #   Given I am a healthcare worker user
  #   And I have an empty Authorization header

  #   When I search for the patient's PDS record

  #   Then I get a 401 HTTP response code
  #   And the X-Request-ID response header matches the request
  #   And the X-Correlation-ID response header matches the request
  #   And the response body does not contain id
  #   And the response body is the Empty Authorization header response

  # Scenario: Invalid authorization header
  #   Given I am a healthcare worker user
  #   And I have a header Authorization value of "Bearer abcdef123456789"

  #   When I search for the patient's PDS record

  #   Then I get a 401 HTTP response code
  #   And the X-Request-ID response header matches the request
  #   And the X-Correlation-ID response header matches the request
  #   And the response body does not contain id
  #   And the response body is the Invalid Access Token response

  # Scenario: Empty x-request-id header
  #   Given I am a healthcare worker user
  #   And I have an empty X-Request-ID header

  #   When I search for the patient's PDS record

  #   Then I get a 400 HTTP response code
  #   And the response header does not contain X-Request-ID
  #   And the X-Correlation-ID response header matches the request
  #   And the response body does not contain id
  #   And the response body is the Empty X-Request ID response

  # Scenario: Invalid x-request-id header
  #   Given I am a healthcare worker user
  #   And I have a header X-Request-ID value of "1234"

  #   When I search for the patient's PDS record

  #   Then I get a 400 HTTP response code
  #   And the X-Request-ID response header matches the request
  #   And the X-Correlation-ID response header matches the request
  #   And the response body does not contain id
  #   And the response body is the Invalid X-Request ID response

  # Scenario: Missing x-request-id header
  #   Given I am a healthcare worker user
  #   And I don't have a X-Request-ID header

  #   When I search for the patient's PDS record

  #   Then I get a 400 HTTP response code
  #   And the response header does not contain X-Request-ID
  #   And the X-Correlation-ID response header matches the request
  #   And the response body does not contain id
  #   And the response body is the Missing X-Request ID response
