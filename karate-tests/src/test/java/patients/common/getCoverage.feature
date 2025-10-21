@ignore
Feature: Get Coverage-not permitted for restricted users

Background:
  * url baseURL

@getCoverageDetails
Scenario: Retrieve a Coverage resource
  * configure headers = requestHeaders 
  * path "Coverage"
  * param "subscriber:identifier" = nhsNumber
  * method get
  * match responseStatus == expectedStatus
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)