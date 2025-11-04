@ignore
Feature: Create patient - Reusable feature to be used when we need create a patient

Background:
  * url baseURL

@createPatient  
Scenario: Create patient
  * path "Patient"
  * def patientPayload = karate.get('patientPayload', read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json'))
  * request patientPayload
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * match responseStatus == expectedStatus