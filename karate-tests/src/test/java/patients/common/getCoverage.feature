@ignore
Feature: Get Coverage-Reusable feature to be used when we need to get coverage details

Background:
  * url baseURL

@getCoverageDetails
Scenario: Retrieve a Coverage resource
  * configure headers = requestHeaders
  * path 'Coverage'
  * param subscriber:identifier = nhsNumber
  * method get
  * match responseStatus == expectedStatus
  * if (responseStatus == 200) {karate.set('originalEtag', responseHeaders['Etag'] ? responseHeaders['Etag'][0] : responseHeaders['etag'][0])}
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)