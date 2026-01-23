@ignore
Feature: Create a new PDS record at birth 

  Background:
    * url baseURL
  
  @invalidMethodCode  
  Scenario: Invalid Method error should be raised for create a new record at birth
    * path "Patient/$process-birth-details"
    * request {any: "request", should: "fail"}
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 403
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse

  @createRecordAtBirth  
  Scenario: create PDS record at birth
    * def queryParams = {}
    * if (typeof ignoreDuplicatesValue !== 'undefined' && ignoreDuplicatesValue != null) queryParams['ignore_potential_matches'] = ignoreDuplicatesValue
    * params queryParams
    * def createRecordAtBirthPayload = karate.get('createRecordAtBirthPayload', read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json'))
    * request createRecordAtBirthPayload
    * path "Patient/$process-birth-details"
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503 && responseStatus != 502
    * method post
    * match responseStatus == expectedStatus

  @createRecordAtBirthWithMaximalData  
  Scenario: create PDS record at birth
    * def queryParams = {}
    * if (typeof ignoreDuplicatesValue !== 'undefined' && ignoreDuplicatesValue != null) queryParams['ignore_potential_matches'] = ignoreDuplicatesValue
    * params queryParams
    * def createRecordAtBirthPayload = karate.get('createRecordAtBirthPayload', read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth-maximal.json'))
    * request createRecordAtBirthPayload
    * path "Patient/$process-birth-details"
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503 && responseStatus != 502
    * method post
    * match responseStatus == expectedStatus