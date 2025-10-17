Feature: get /Patient - Application-restricted access

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * def noAuthHeaders = call read('classpath:auth-jwt/no-auth-headers.js')

    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json') 
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')
    * json patientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/patientSearchResultEntry.json')
    * url baseURL

    @smoke
  Scenario: All headers provided - app restricted user can search for a patient and get a single match result returned
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@singleMatch')

  Scenario: Missing Authorization header with application-restricted access
    * call read('classpath:patients/common/getPatient.feature@missingAuthHeader')
    
  Scenario Outline: Authorization header issues with application-restricted access - <expected_diagnostics>
    * call read('classpath:patients/common/getPatient.feature@invalidAuthHeader')
    
    Examples:
      | authorization_header                | expected_diagnostics            |
      |                                     | Empty Authorization header      |
      | Bearer INVALID_TOKEN!!!             | Invalid Access Token            |
      | Bearer                              | Missing access token            |
    
  Scenario: NHSD-SESSION-URID header is not required with application-restricted access 
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@noSessionHeader')

    @oas-bug
  Scenario: PDS FHIR API rejects request for more than one result with application-restricted access 
    # This test is expected to fail due to a discrepancy between the OAS definition and the implementation:
    # https://nhsd-jira.digital.nhs.uk/browse/SPINEDEM-3187
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@multiMatchError')

  Scenario: PDS FHIR API accepts request for one result with application-restricted access 
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/getPatient.feature@maxResultSet')
  Scenario: Too many matches message when search result return more than one match with application-restricted access 
    * call read('classpath:patients/common/getPatient.feature@tooManyMatches')