@no-oas
Feature: Check PDS FHIR requests are rejected as "unauthorized" for interaction free test apps

Background:
  * def utils = call read('classpath:helpers/utils.feature')

  # auth
  * url baseURL

Scenario: Make request to PDS endpoint that is rejected as "unauthorized"
  * def nhsNumber = '9693632109'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * path 'Patient', nhsNumber
  * method get
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised"

Scenario: Make request to PDS coverage endpoint that is rejected as "unauthorized"(app doesn't have interaction for Coverage)
  * def p9number = '9733162868'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret'),userID: p9number, scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * path 'Coverage'
  * param beneficiary:identifier = p9number
  * method get
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised"
