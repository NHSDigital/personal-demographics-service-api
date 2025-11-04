@ignore
Feature:  Update Coverage details - Reusable feature to be used when we need to update coverage details
  Background:
    * url baseURL

  @updateCoverageDetails  
  Scenario: Update coverage details
    * header Content-Type = "application/json"
    * header If-Match = originalEtag 
    * path "Coverage"
    * request requestBody
    * method post
    * match responseStatus == expectedStatus
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
