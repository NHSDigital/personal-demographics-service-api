@ignore
Feature: Update patient details for restricted users

  Background:
    * url baseURL

  @invalidMethodCode 
  Scenario: Invalid Method error should be raised for restricted users
    * def nhsNumber = '9733162817'
    * def patientResource = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ expectedStatus: 200, nhsNumber:"#(nhsNumber)"}
    * def originalEtag = patientResource.responseHeaders.Etag[0]

    # add emergency contact details
    * configure headers = call read('classpath:auth-jwt/app-restricted-headers.js')
    * def mobileNumber = '0788848687'
    * def requestBody = read('classpath:patients/requestDetails/add/emergencyContact.json')
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ expectedStatus: 403}
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse