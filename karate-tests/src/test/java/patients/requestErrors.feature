@no-oas
Feature: Handle request errors

Background:
  # schemas and validators that are required by the schema checks
  * def utils = call read('classpath:helpers/utils.feature')

  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

Scenario: Make request to endpoint that is not supported
  * def nhsNumber = '9693632109'
  * path 'HelloWorld'
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.issue[0].diagnostics == "Unsupported path - '/HelloWorld'"

Scenario: Make request to invalid endpoint that is similar to valid endpoint
  * def nhsNumber = '9693632109'
  * path 'Patient!'
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.issue[0].diagnostics == "Unsupported path - '/Patient!'"

 Scenario: Make invalid put request to get patient endpoint 
  * def nhsNumber = '9693632109'
  * path 'Patient', nhsNumber
  * request 
  """
    {
    "id": 123,
    "name": "John Smith",
    "email": "john.smith@example.com"
    }
  """
  * method put
  * status 400
  * match response.issue[0].details.coding[0].display == "Unsupported Service"

 Scenario: Make invalid options request to get patient endpoint 
  * def nhsNumber = '9693632109'
  * path 'Patient', nhsNumber
  * method options
  * status 502
  * match response.issue[0].details.coding[0].display == "Unknown Error"

  Scenario: Make a request to invalid url - /Patient/<valid nhs number>?<query param>
  * def nhsNumber = '9693632109'
  * params  { family: "Jones", gender: "male", birthdate: "ge1992-01-01", _max-results: "6" }
  * path "Patient", nhsNumber
  * method get
  * status 400
  * match response == read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json')