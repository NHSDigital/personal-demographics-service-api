@ignore
Feature: Get a patient - Healthcare worker access mode

Background:
 
  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

Scenario: Get an "unrestricted" patient
  * def nhsNumber = '9693632109'
  * path 'Patient', nhsNumber
  * method get
  