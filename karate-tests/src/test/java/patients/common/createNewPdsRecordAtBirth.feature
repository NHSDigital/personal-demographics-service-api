@ignore
Feature: Create a new PDS record at birth 

  Background:
    * url baseURL
  
@invalidMethodCode  
  Scenario: Invalid Method error should be raised for creat a new record at birth
    * path "Patient/$process-birth-details"
    * request {any: "request", should: "fail"}
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 403
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse