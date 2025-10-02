@no-oas
Feature: Create a new PDS record at birth - not permitted for application-restricted users
  
Background:
  * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
  * configure headers = requestHeaders  
  * url baseURL
  
Scenario: Invalid Method error should be raised for creat a new record at birth
  * path "Patient/$process-birth-details"
  * request {any: "request", should: "fail"}
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 403
  * def display = "Cannot create resource with application-restricted access token"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
  * match response == expectedResponse