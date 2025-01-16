
@ignore @no-oas
Feature: Patient Access (Update Coverage details)

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json patientCoverageResultEntry  = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageResultEntry.json')
    * json coverageBundle = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageBundle.json')
    
    * configure url = baseURL

  @sandbox
   Scenario: Happy path - update patient coverage details
    * def p9number = '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = p9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/update-patient-request.json')
    * method post
    * status 200
    * match parseInt(response.meta.versionId) == originalVersion + 1
    

  
