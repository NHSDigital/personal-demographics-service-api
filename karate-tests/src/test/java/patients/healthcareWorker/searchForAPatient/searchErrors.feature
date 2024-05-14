@sandbox
Feature: Search errors

Background:
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * configure headers = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * url baseURL

Scenario: No params
  * path 'Patient'    
  * params {}
  * method get
  * status 400
  * match response == read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json')

Scenario: All invalid params
  * path 'Patient'  
  * params {manufacturer: "Ford", model: "focus", year: "2003" }
  * method get
  * status 400
  * def diagnostics = "Invalid request with error - Additional properties are not allowed ('manufacturer', 'year', 'model' were unexpected)"
  * match response == read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')
    
Scenario: One invalid param
  * path 'Patient'
  * params { family: "Smith", birthdate: "eq2010-10-22", year: "2003" }
  * method get
  * status 400
  * def diagnostics = "Invalid request with error - Additional properties are not allowed ('year' was unexpected)"
  * match response == read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')

Scenario: Invalid date format
  * path 'Patient'  
  * params { family: "Smith", given: "jane", gender: "female", birthdate: "20101022" } 
  * method get
  * status 400
  * def diagnostics = "Invalid value - '20101022' in field 'birthdate'"
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
