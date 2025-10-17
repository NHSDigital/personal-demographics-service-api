    @no-oas
Feature: Get Coverage-not permitted for privileged-application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')

  Scenario: Fail to retrieve a Coverage resource with privileged access
    * def display = "Cannot GET resource with privileged-application-restricted access token"
    * call read('classpath:patients/common/getCoverage.feature@accessDenied')
    