@ignore
Feature: Get (search for) patients based on demographics data
  Reusable feature to be used when we need to search for patients given 
  a set of demographics data

  Background:
    # schemas and validators that are required by the main schema checks
    * def utils = call read('classpath:helpers/utils.feature')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')
    * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
    * json patientSearchResultEntry = karate.readAsString('classpath:patients/healthcareWorker/searchForAPatient/schemas/patientSearchResultEntry.json')
  
    # auth
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
  

  Scenario: Get by demographics
    * path "Patient"
    * param family = karate.get('family')
    * param given = karate.get('given')
    * param gender = karate.get('gender')
    * param birthdate = karate.get('birthdate')
    * param address-postalcode = karate.get('address-postalcode')
    * param _max-results = "6"
    * method get
    * match response == read('classpath:patients/healthcareWorker/searchForAPatient/schemas/patientSearchBundle.json')
    * status 200
