@no-oas
Feature: Check PDS FHIR requests are rejected as "unauthorized" for interaction free test apps

Background:
  * url baseURL
  
Scenario: Make GET /Patient request from app that does not have pdsquery:PatientRetrieve interaction
  * def nhsNumber = '9693632109'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * path 'Patient', nhsNumber
  * method get
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised"

Scenario: Make GET /Coverage request from app that does not have pdsquery:CoverageRetrieve interaction
  * def p9number = '9733162868'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret'),userID: p9number, scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * path 'Coverage'
  * param beneficiary:identifier = p9number
  * method get
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised"

@ignore
Scenario: Make POST /Coverage request from app that does not have CoverageSelfUpdate interaction
  * def nhsNumber = '9733162922'
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('interactionFreeClientID'), clientSecret:karate.get('interactionFreeClientSecret'),userID: nhsNumber, scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * header Content-Type = "application/json"
  # hardcoded scn number as it's not possible to get the scn number from interaction free app
  * header If-Match = 'W/"1979"'
  * def utils = call read('classpath:helpers/utils.feature')
  * def periodEndDate = utils.randomDateWithInYears(4)
  * path "Coverage"
  * request read('classpath:patients/patientAccess/update-patient-coverage-request.json')
  * configure retry = { count: 15, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 401
  * match response.issue[0].details.coding[0].display == "Access Denied - Unauthorised" 