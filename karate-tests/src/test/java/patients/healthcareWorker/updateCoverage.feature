Feature: Update Coverage-not permitted for healthcare worker

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL
 
  Scenario: Fail to update a Coverage resource
    * def nhsNumber = '9733163031'
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalEtag = responseHeaders['Etag'] ? responseHeaders['Etag'][0] : responseHeaders['etag'][0]
    * def periodEndDate = utils.randomDateWithInYears(2)
    * def requestBody = read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * call read('classpath:patients/common/updateCoverage.feature@updateCoverageDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 403}
    * def display = "Cannot POST resource with user-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse