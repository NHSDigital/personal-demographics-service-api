@ignore
Feature: Create patient 

Background:
  * url baseURL

@createPatient  
Scenario: Create patient
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * match responseStatus == expectedStatus