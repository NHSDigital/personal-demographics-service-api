@ignore
Feature: Get Patient 
# This feature validates patient search behavior for various conditions
# including single match, missing headers, and permission errors.

 Background:
    * url baseURL
    * def utils = karate.callSingle('classpath:helpers/utils.feature')

  @singleMatch
  Scenario: All headers provided - restricted user can search for a patient and get a single match result returned
    * configure headers = requestHeaders 
    * path "Patient"
    * param family = "Smith" 
    * param gender = "female"
    * param birthdate = "eq2018-06-08" 
    * method get
    * status 200
    * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
    * match response.total == 1
  
  @noSessionHeader
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

  @multiMatchError
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
   
  @maxResultSet
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