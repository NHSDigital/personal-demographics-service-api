@no-oas
Feature: Create a new PDS record at birth - not permitted for application-restricted users
  
Background:
  * def utils = call read('classpath:helpers/utils.feature') 
  * url baseURL
  
Scenario: Invalid Method error should be raised for create a new record at birth
  * def p9number = '9912003071'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * path "Patient/$process-birth-details"
  * request {any: "request", should: "fail"}
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 403
  * def display = "Cannot create resource with patient-access access token"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
  * match response == expectedResponse