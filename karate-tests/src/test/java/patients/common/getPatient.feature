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

  @searchForAPatient
  Scenario: Retrieve patient details
    * def queryParams = {}
    * if (searchParams['_fuzzy-match'] != null) queryParams['_fuzzy-match'] = searchParams['_fuzzy-match']
    * if (searchParams['_exact-match'] != null) queryParams['_exact-match'] = searchParams['_exact-match']
    * if (searchParams['_history'] != null) queryParams['_history'] = searchParams['_history']
    * if (searchParams['_max-results'] != null) queryParams['_max-results'] = searchParams['_max-results']
    * if (searchParams['family'] != null) queryParams['family'] = searchParams['family']
    * if (searchParams['given'] != null) queryParams['given'] = searchParams['given']
    * if (searchParams['gender'] != null) queryParams['gender'] = searchParams['gender']
    * if (searchParams['birthdate'] != null) queryParams['birthdate'] = searchParams['birthdate']
    * if (searchParams['death-date'] != null) queryParams['death-date'] = searchParams['death-date']
    * if (searchParams['address-postcode'] != null) queryParams['address-postcode'] = searchParams['address-postcode']
    * if (searchParams['address-postalcode'] != null) queryParams['address-postalcode'] = searchParams['address-postalcode']
    * if (searchParams['general-practitioner'] != null) queryParams['general-practitioner'] = searchParams['general-practitioner']
    * if (searchParams['email'] != null) queryParams['email'] = searchParams['email']
    * if (searchParams['phone'] != null) queryParams['phone'] = searchParams['phone']
    * path 'Patient'
    * params queryParams
    * method get
    * match responseStatus == searchParams.expectedStatus
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)