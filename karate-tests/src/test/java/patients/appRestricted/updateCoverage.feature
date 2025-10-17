Feature:  Update Coverage details - not permitted for application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 

  Scenario: Fail to update a Coverage resource    
    * def display = "Cannot POST resource with application-restricted access token"
    * call read('classpath:patients/common/updateCoverage.feature@accessDenied') 