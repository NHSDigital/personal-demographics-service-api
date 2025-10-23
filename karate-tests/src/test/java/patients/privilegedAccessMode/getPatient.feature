@no-oas
Feature: get /Patient - privileged-application-restricted access mode

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * def noAuthHeaders = call read('classpath:auth-jwt/no-auth-headers.js')

    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json') 
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')
    * json patientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/patientSearchResultEntry.json')
    * url baseURL

  Scenario: All headers provided - privileged-application-restricted user can search for a patient and get a single match result returned
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@singleMatch')

  Scenario: Missing Authorization header with privileged application restricted access
    * call read('classpath:patients/common/getPatient.feature@missingAuthHeader')
    
  Scenario Outline: Authorization header issues with privileged application restricted access - <expected_diagnostics>
     * call read('classpath:patients/common/getPatient.feature@invalidAuthHeader')
    
    Examples:
      | authorization_header                | expected_diagnostics            |
      |                                     | Empty Authorization header      |
      | Bearer INVALID_TOKEN!!!             | Invalid Access Token            |
      | Bearer                              | Missing access token            |
    
  Scenario: NHSD-SESSION-URID header is not required - privileged-application-restricted access mode
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@noSessionHeader')

    @oas-bug
  Scenario: PDS FHIR API rejects request for more than one result - privileged-application-restricted access mode
    # This test is expected to fail due to a discrepancy between the OAS definition and the implementation:
    # https://nhsd-jira.digital.nhs.uk/browse/SPINEDEM-3187
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@multiMatchError')

  Scenario: PDS FHIR API accepts request for one result - privileged-application-restricted access mode
     * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@maxResultSet')
    
  Scenario: Too many matches message when search result return more than one match - privileged-application-restricted access mode
    * call read('classpath:patients/common/getPatient.feature@tooManyMatches')

  Scenario: Patient search response should not include address, telecoms, registered GP details for privileged access
    * configure headers = requestHeaders 
    * path "Patient"
    * param family = "GOUGH" 
    * param gender = "female"
    * param birthdate = "1993-12-02"
    * param given = 'Fancy'
    * param phone = '07556588324'
    * method get
    * status 200
    * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
    * match response.entry[0].resource.address == '#notpresent'
    * match response.generalPractitioner == '#notpresent'