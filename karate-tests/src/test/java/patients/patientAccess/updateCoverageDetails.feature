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
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = responseHeaders['Etag'] ? responseHeaders['Etag'][0] : responseHeaders['etag'][0]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def periodEndDate = utils.randomDateWithInYears(4)
    * def requestBody = read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * call read('classpath:patients/common/updateCoverage.feature@updateCoverageDetails'){ requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 201}
    * match parseInt(response.meta.versionId) == originalVersion + 1
    * match response == coverageBundle
    * match response.entry[0].resource.status == 'active'
    * match response.entry[0].resource.period.end == periodEndDate