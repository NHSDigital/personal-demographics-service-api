@ignore
Feature: Get Coverage-not permitted for restricted users

Background:
  * url baseURL

@accessDenied
Scenario: Fail to retrieve a Coverage resource
  * configure headers = requestHeaders 
  * path "Coverage"
  * param "subscriber:identifier" = "9999999999"
  * method get
  * status 403
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
  * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
  * match response == expectedResponse