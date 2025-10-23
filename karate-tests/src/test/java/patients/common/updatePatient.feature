@ignore
Feature: Update patient details

  Background:
    * url baseURL
    * def utils = call read('classpath:helpers/utils.feature')

  @updatePatientDetails  
  Scenario: Update coverage details
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * path 'Patient', nhsNumber
    * configure retry = { count: 5, interval: 4000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * request requestBody
    * method patch
    * match responseStatus == expectedStatus