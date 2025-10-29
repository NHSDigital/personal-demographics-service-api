Feature: Get Coverage-not permitted for healthcare worker

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL

  Scenario: Fail to retrieve a Coverage resource
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:9693632109, expectedStatus: 403 }
    * def display = "Cannot GET resource with user-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse