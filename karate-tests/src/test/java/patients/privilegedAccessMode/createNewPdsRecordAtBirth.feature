Feature: Create a new PDS record at birth- privileged access

  Background:
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
  Scenario: Invalid Method error should be raised for creat a new record at birth with privileged access
    * def display = "Cannot create resource with privileged-application-restricted access token"
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@invalidMethodCode')