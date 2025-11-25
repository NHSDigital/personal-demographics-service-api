Feature: Patch patient - add errors

Covers error scenarios that can arise when trying to add data to a patient resource.

Background:
  * def utils = call read('classpath:helpers/utils.feature')   
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * url baseURL

  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

@sandbox
Scenario: Forbidden update example - multiple usual names cannot be added
  * def nhsNumber = '5900059332'
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * match patientDetails.response.name == '#[1]'
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]

  * configure headers = call read('classpath:auth/auth-headers.js')

  * def diagnostics = "Forbidden update with error - multiple usual names cannot be added"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')
  * def newName = 
  """
  {
    "use": "usual",
    "period": {"start": "2019-12-31"},
    "prefix": ["Dr"],
    "given": ["Joe", "Horation", "Maximus"],
    "family": "Bloggs",
    "suffix": ["PhD"],
  }
  """
  * def requestBody = {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 403}
  * match response == expectedResponse

Scenario: Invalid Value - Add deceasedTime in yyyy-mm-ddTHH:MM:SS+01:00 format(PDS FHIR do not accepts Zero UTC offset)
  * def nhsNumber = '9736363287'
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00+01:00"
  * def requestBody = read('classpath:patients/requestDetails/add/deceasedDateTime.json')
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400} 
  * def diagnostics = `Invalid value - '${deceasedDate}' in field 'deceasedDateTime'`    
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  * match response == expectedResponse