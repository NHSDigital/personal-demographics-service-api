@sandbox @test_luck
Feature: Patch patient - Remove data errors

  # Tests more of the error scenarios that can arise when trying to remove data from a patient resource

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * url baseURL

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def nhsNumber = '5900057208'
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    
    * def patientObject = patientDetails.response
    * def etag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)

  Scenario: Error: attempt to remove name object from patient without prior test
    * def diagnostics = "Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def requestBody = {"patches":[{"op":"remove","path":"/name/1"}]}
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etag)",expectedStatus: 400}
    * match response == expectedBody

  Scenario: Error: attempt to remove name object that doesn't exist
    * match patientDetails.response.name == "#[1]"

    * def diagnostics = "Invalid update with error - Invalid patch - index '1' is out of bounds"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def requestBody = 
    """
    {"patches":[
      {"op":"test","path":"/name/1/id", "value":"123456"},
      {"op":"remove","path":"/name/1"}
      ]}
      """
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etag)",expectedStatus: 400}
    * match response == expectedBody

  Scenario: Error: attempt to remove suffix that doesn't exist
    * match patientDetails.response.name[0].suffix == "#notpresent"

    * def diagnostics = "Invalid update with error - Invalid patch - can't remove non-existent object '0'"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def requestBody = 
      """
      {"patches":[
        {"op":"test","path":"/name/0/id", "value": "#(patientDetails.response.name[0].id)"},
        {"op":"remove","path":"/name/0/suffix/0"}
      ]}
      """
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etag)",expectedStatus: 400}
    * match response == expectedBody