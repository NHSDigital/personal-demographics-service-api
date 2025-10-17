Feature: Get Coverage-not permitted for application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')

  Scenario: Fail to retrieve a Coverage resource with application-restricted users
    * def display = "Cannot GET resource with application-restricted access token"
    * call read('classpath:patients/common/getCoverage.feature@accessDenied')