
Feature: Get Coverage-not permitted for application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')

    * url baseURL

  Scenario: Fail to retrieve a Coverage resource
    * configure headers = requestHeaders 
    * path "Coverage"
    * param "subscriber:identifier" = "9999999999"
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = "Cannot GET resource with application-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse