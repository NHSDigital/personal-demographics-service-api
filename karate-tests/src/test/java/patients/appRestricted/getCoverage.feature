Feature: Get Coverage-not permitted for application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')

  Scenario: Fail to retrieve a Coverage resource with application-restricted users
    * def display = "Cannot GET resource with application-restricted access token"
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:9999999999, expectedStatus: 403 }
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse
