Feature: get /Patient - privileged-application-restricted access mode

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * def noAuthHeaders = call read('classpath:auth-jwt/no-auth-headers.js')

    * def utils = call read('classpath:helpers/utils.feature')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json') 
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')
    * json patientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/patientSearchResultEntry.json')
    * url baseURL

  Scenario: All headers provided - privileged-application-restricted user can search for a patient and get a single match result returned
    * configure headers = requestHeaders 
    * path "Patient"
    * param family = "Smith" 
    * param gender = "female"
    * param birthdate = "eq2018-06-08" 
    * method get
    * status 200
    * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
    * match response.total == 1

  Scenario: Missing Authorization header
    * configure headers = noAuthHeaders
    * path "Patient"
    * method get
    * status 401
    * match response.issue[0].diagnostics == "Missing Authorization header"
    
  Scenario Outline: Authorization header issues
    # nb "expired header" isn't here...
    * configure headers = noAuthHeaders
    * header Authorization = authorization_header
    * path "Patient"
    * method get
    * status 401
    * match response.issue[0].diagnostics == expected_diagnostics
    
    Examples:
      | authorization_header                | expected_diagnostics            |
      |                                     | Empty Authorization header      |
      | Bearer INVALID_TOKEN!!!             | Invalid Access Token            |
      | Bearer                              | Missing access token            |
    
  Scenario: NHSD-SESSION-URID header is not required
    * configure headers =       
      """
      {
        "authorization": "#(requestHeaders['authorization'])",
        "x-request-id": "#(utils.randomUUID())",
        "x-correlation-id": "#(utils.randomUUID())",
      }
      """
    * path "Patient"
    * param family = "Smith" 
    * param gender = "female"
    * param birthdate = "2010-10-22" 
    * method get
    * status 200
    * match response ==
      """
      {
        "resourceType": "Bundle",
        "timestamp": "#? utils.isValidTimestamp(_)",
        "total": "#number",
        "type": "searchset"
      }  
      """  

  @oas-bug
  Scenario: PDS FHIR API rejects request for more than one result
    # This test is expected to fail due to a discrepancy between the OAS definition and the implementation:
    # https://nhsd-jira.digital.nhs.uk/browse/SPINEDEM-3187
    * configure headers = requestHeaders
    * path "Patient"
    * param family = "Magin" 
    * param gender = "female"
    * param birthdate = "1957-07-23" 
    * param _max-results = 2
    * method get
    * status 403
    * match response.issue[0].diagnostics == "Your app has insufficient permissions to perform this search. Please contact support."

  Scenario: PDS FHIR API accepts request for one result
    * configure headers = requestHeaders 
    * path "Patient"
    * param family = "Smith" 
    * param gender = "female"
    * param birthdate = "2010-10-22" 
    * param email = "jane.smith@example.com" 
    * param phone = "01632960587"
    * param _max-results = 1
    * method get
    * status 200
    * match response ==
    """
    {
      "resourceType": "Bundle",
      "timestamp": "#? utils.isValidTimestamp(_)",
      "total": "#number",
      "type": "searchset"
    }  
    """
  
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

  Scenario: Get a patients details
  * configure headers = requestHeaders  
  * def nhsNumber = '9733162825'
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * match response.id == nhsNumber
  
  Scenario: Get a patient details- RemovalReasonExitCode should be Armed Forces (notified by Armed Forces) AFN
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def nhsNumber = '9733162981'  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "AFN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Armed Forces (notified by Armed Forces)"
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'