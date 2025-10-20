Feature: Get related person details - Application-restricted access mode

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

  Scenario: Patient has one related person with application-restricted access
    * call read('classpath:patients/common/getPatientsRelatedPerson.feature@patientWithOneRelatedPerson') 

  Scenario: Patient doesn't have a related person with application-restricted access
    * call read('classpath:patients/common/getPatientsRelatedPerson.feature@patientWithNoRelatedPerson')    