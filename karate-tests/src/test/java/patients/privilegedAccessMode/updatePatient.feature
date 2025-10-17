@no-oas @test_luck
Feature: Update patient details - not permitted for privileged-application-restricted users

Background:
  * def utils = karate.callSingle('classpath:helpers/utils.feature')
  * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
  * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
  * configure headers = requestHeaders 
  
Scenario: Invalid Method error should be raised when privileged-application-restricted user try to update patient details
  * def display = "Cannot update resource with privileged-application-restricted access token"
  * call read('classpath:patients/common/updatePatient.feature@invalidMethodCode') 