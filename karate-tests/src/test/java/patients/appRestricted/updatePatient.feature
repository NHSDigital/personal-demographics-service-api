Feature: Update patient details - not permitted for application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
  Scenario: Invalid Method error should be raised when app restricted user try to update patient details
    * def display = "Cannot update resource with application-restricted access token"
    * call read('classpath:patients/common/updatePatient.feature@invalidMethodCode') 