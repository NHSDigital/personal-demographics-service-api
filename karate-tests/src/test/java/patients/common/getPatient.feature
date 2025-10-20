@ignore
Feature: Get Patient 

 Background:
    * url baseURL

  @missingAuthHeader
  Scenario: Missing Authorization header
    * configure headers = noAuthHeaders
    * path "Patient"
    * method get
    * status 401
    * match response.issue[0].diagnostics == "Missing Authorization header"
   
  @invalidAuthHeader 
  Scenario: Authorization header issues
    # nb "expired header" isn't here...
    * configure headers = noAuthHeaders
    * header Authorization = authorization_header
    * path "Patient"
    * method get
    * status 401
    * match response.issue[0].diagnostics == expected_diagnostics
    
   
  @tooManyMatches
    Scenario: Too many matches message when search result return more than one match
    * configure headers = requestHeaders 
    * path "Patient"
    * param family = "Ma*" 
    * param gender = "female"
    * param birthdate = "eq1957-07-23" 
    * method get
    * status 200
    * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
    * match response.total == 1
    * path "Patient"
    * param family = "Ma*" 
    * param gender = "female"
    * param birthdate = "ge1957-07-23" 
    * method get
    * status 200
    * match response == read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')    