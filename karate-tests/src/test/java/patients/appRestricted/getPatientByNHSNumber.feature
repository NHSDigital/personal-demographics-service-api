    @no-oas
Feature: Get a patient - Application-restricted access

  Background:

    # auth
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

  Scenario: Retrieve a patient with an invalid NHS number format should return 'invalid resource' with app restricted access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@invalidResource')

  Scenario: Retrieve a patient with non-existent records should return 'RESOURCE_NOT_FOUND' with app restricted access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@resourceNotFound')

  Scenario: Retrieve a patient with invalidated records should return 'INVALIDATED_RESOURCE' with app restricted access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@invalidatedResource')
  
  Scenario: Get a patients details
    * configure headers = requestHeaders  
    * def nhsNumber = '9733162825'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.id == nhsNumber     