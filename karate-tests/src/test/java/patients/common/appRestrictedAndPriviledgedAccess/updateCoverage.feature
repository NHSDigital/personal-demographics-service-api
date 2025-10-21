@ignore
Feature: Get Coverage-not permitted for restricted users


  @accessDenied  
  Scenario: Fail to update a Coverage resource 
    * def nhsNumber = '9733162825'
    * def patientResource = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ expectedStatus: 200, nhsNumber:"#(nhsNumber)"}     
    * def originalEtag = patientResource.responseHeaders.Etag[0]
    * def periodEndDate = utils.randomBirthDate()
    * def requestBody = read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * call read('classpath:patients/common/updateCoverage.feature@updateCoverageDetails'){ expectedStatus: 403}
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse
  