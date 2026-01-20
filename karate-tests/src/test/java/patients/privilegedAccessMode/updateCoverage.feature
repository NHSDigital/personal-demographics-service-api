@no-oas
Feature:  Update Coverage details - not permitted for privileged-application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 

  Scenario: Fail to update a Coverage resource with privileged access    
    * def display = "Cannot POST resource with privileged-application-restricted access token"
    * call read('classpath:patients/common/appRestrictedAndPriviledgedAccess/updateCoverage.feature@accessDenied') 