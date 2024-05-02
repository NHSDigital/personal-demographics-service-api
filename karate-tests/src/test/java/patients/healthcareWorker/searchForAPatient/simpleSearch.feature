@sandbox
Feature: Search for a patient - Healthcare worker access mode - "Simple search"

These tests authenticate as one of the available test healthcare workers,
darren.mcdrew@nhs.net

Background:
  # schemas and validators that are required by the main schema checks
  * def utils = call read('classpath:helpers/utils.feature')
  * json generalPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json addressSchema = karate.readAsString('classpath:schemas/Address.json')
  * json humanNameSchema = karate.readAsString('classpath:schemas/HumanName.json')
  * json patientSearchResultEntry = karate.readAsString('classpath:schemas/patientSearchResultEntry.json')
  
  # auth
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

Scenario:Search for a patient using parameters
  * path "Patient"
  * param family = "Jones"
  * param gender = "male"
  * param birthdate = "ge1992-01-01"
  * param _max-results = "6"
  * method get
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:patients/healthcareWorker/searchForAPatient/patientSearchBundle.json')
  * status 200
