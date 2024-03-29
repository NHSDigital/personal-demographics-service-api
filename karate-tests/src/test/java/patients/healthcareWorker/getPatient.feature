Feature: Get a patient - Healthcare worker access mode

  These tests authenticate as one of the available test healthcare workers,
  darren.mcdrew@nhs.net

  Background:
    # schemas and validators that are required by the main schema checks
    * def utils = call read('classpath:helpers/utils.feature')
    * json generalPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json periodSchema = karate.readAsString('classpath:schemas/Period.json')
    * json addressSchema = karate.readAsString('classpath:schemas/Address.json')
    * json humanNameSchema = karate.readAsString('classpath:schemas/HumanName.json')
    * json patientSearchResultEntry = karate.readAsString('classpath:schemas/patientSearchResultEntry.json')
    
    # auth
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

  @get
  Scenario: Get a patient, validate the schema
    # useful for more dynamic testing, where we can get any patient
    * def nhsNumber = karate.get('nhsNumber', '9693632109')
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match karate.response.header('x-request-id') == requestHeaders['x-request-id']
    * match karate.response.header('x-correlation-id') == requestHeaders['x-correlation-id']
    * match response.id == nhsNumber
    * def gender = response.gender
    * def birthDate = response.birthDate
    * def address = response.address
    * def name = response.name
    * match response == read('classpath:stubs/patient/patient-response-template.json')

  @getSpecific
  Scenario: Get a specific patient
    # useful for checking the data is what we expect... maybe?
    * def nhsNumber = '9693632109'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match karate.response.header('x-request-id') == requestHeaders['x-request-id']
    * match karate.response.header('x-correlation-id') == requestHeaders['x-correlation-id']
    * match response.id == nhsNumber
    * match response == read('patient.json')

  @search
  Scenario:Search for a patient using parameters
    * path "Patient"
    * param family = "Jones"
    * param gender = "male"
    * param birthdate = "ge1992-01-01"
    * param _max-results = "6"
    * method get
    * match response == read('classpath:schemas/patientSearchBundle.json')
    * status 200
