@no-oas @interactionFree
Feature: Check PDS FHIR requests are rejected as "unauthorized" apps

Background:
  * def utils = call read('classpath:helpers/utils.feature')

  # auth
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

Scenario: Make request to PDS endpoint that is rejected as "unauthorized"
  * def nhsNumber = '9693632109'
  * path 'Patient', nhsNumber
  * method get
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised"

