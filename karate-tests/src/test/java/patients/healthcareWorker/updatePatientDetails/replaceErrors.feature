@sandbox
Feature: Patch patient errors - Replace data

Demonstrates invalid "replace" operations on a patient resource.

Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * url baseURL 
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
 
  * def faker = Java.type('helpers.FakerWrapper')
  #generate patient with both home and temporary address and telecom details
  * def birthDate = utils.randomBirthDate()
  * def familyName = "ToRemove"
  * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
  * def prefix = ["#(utils.randomPrefix())"]
  * def gender = utils.randomGender()
  * def address = utils.randomAddress(birthDate)
  * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 } 

Scenario: Invalid patch - no address ID
  * def nhsNumber = createPatientResponse.response.id
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]

  * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')   
  * def requestBody = 
    """
    {"patches":[
      {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
      {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
    ]}
    """
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}    
  * match response == expectedBody

Scenario: Invalid patch - attempt to replace non-existent object
  * def nhsNumber = createPatientResponse.response.id
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]

  * def diagnostics = "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * def requestBody = 
    """
    {"patches":[
      {"op":"replace","path":"/address/0/id","value":"456"},
      {"op":"replace","path":"/address/0/line","value":["2 Trevelyan Square","Boar Lane","Leeds"]},
      {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
    ]}
    """
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}    
  * match response == expectedBody

Scenario: Invalid patch - invalid address ID
  * def nhsNumber = createPatientResponse.response.id
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]
  * def diagnostics = "Invalid update with error - no 'address' resources with object id '123456'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * def requestBody = 
    """
    {"patches":[
      {"op":"replace","path":"/address/0/id","value":"123456"},
      {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
      {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
    ]}
    """  
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}    
  * match response == expectedBody

Scenario: Invalid patch - invalid address ID only
  * def nhsNumber = createPatientResponse.response.id
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]

  * def diagnostics = "Invalid update with error - no 'address' resources with object id '123456'"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')
  * def requestBody = {"patches":[{"op":"replace","path":"/address/0/id","value":"123456"}]}
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}
  * match response == expectedBody

Scenario: Invalid patch - patient with no address
  * def nhsNumber = '5900059073'
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]  
  * def diagnostics = "Invalid update with error - Invalid patch - index '0' is out of bounds"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
  
  * configure headers = call read('classpath:auth/auth-headers.js')
  * def requestBody = 
  """
  {
    "patches":[
      {"op":"replace","path":"/address/0/id","value":"456"},
      {"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},
      {"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}
    ]
  }
  """
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}
  * match response == expectedBody

Scenario: Invalid patch - Patient with no address / Request without address ID
  * def nhsNumber = createPatientResponse.response.id
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0]  
  
  * def diagnostics = "Invalid update with error - no id or url found for path with root /address/0"
  * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

  * configure headers = call read('classpath:auth/auth-headers.js')

  * def requestBody = {"patches":[{"op":"replace","path":"/address/0/line/0","value":"2 Whitehall Quay"},{"op":"replace","path":"/address/0/postalCode","value":"LS1 4BU"}]}
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 400}
  * match response == expectedBody