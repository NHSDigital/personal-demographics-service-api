@sandbox
Feature: Create patient - not permitted for application-restricted users

Background:
  * def accessToken = karate.callSingle('classpath:patients/appRestricted/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/appRestricted/app-restricted-headers.js')
  * configure headers = requestHeaders  
  * url baseURL

Scenario: Invalid Method error should be raised
  * path "Patient"
  * request {any: "request", should: "fail"}
  * method post
  * status 403
  * def display = "Cannot create resource with application-restricted access token"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
  * match response == expectedResponse