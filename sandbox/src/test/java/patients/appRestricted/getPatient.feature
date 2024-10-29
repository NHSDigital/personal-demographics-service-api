Feature: get /Patient - Application-restricted access mode

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:patients/appRestricted/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/appRestricted/app-restricted-headers.js')
    * def noAuthHeaders = call read('classpath:patients/appRestricted/no-auth-headers.js')
    * url baseURL
    * param family = "Smith" 
    * param gender = "female"
    * param birthdate = "eq2010-10-22" 
    * param email = "jane.smith@example.com" 
    * param phone = "01632960587"

  Scenario: All headers provided
    * configure headers = requestHeaders 
    * path "Patient"
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
    * param _max-results = 2
    * method get
    * status 403
    * match response.issue[0].diagnostics == "Your app has insufficient permissions to perform this search. Please contact support."

  Scenario: PDS FHIR API accepts request for one result
    * configure headers = requestHeaders 
    * path "Patient"
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
