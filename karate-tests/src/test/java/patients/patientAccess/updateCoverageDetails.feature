Feature: Patient Access (Update Coverage details)

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json patientCoverageResultEntry  = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageResultEntry.json')
    * json coverageBundle = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageBundle.json')
    
    * configure url = baseURL
 
   @sandbox
   Scenario: Happy path - update patient coverage details
    * def nhsNumber = karate.env.includes('sandbox') ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param subscriber:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
    * retry until responseStatus != 503 && responseStatus != 502  
    * method post
    * status 201
    * match parseInt(response.meta.versionId) == originalVersion + 1
    * match response == coverageBundle
    * match response.entry[0].resource.status == 'active'
    * match response.entry[0].resource.period.end == periodEndDate