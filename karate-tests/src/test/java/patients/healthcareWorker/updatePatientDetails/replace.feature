Feature: Patch patient - Replace data

Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def faker = Java.type('helpers.FakerWrapper')
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * url baseURL
  * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
  * configure headers = requestHeaders 
  * def familyName = "ToRemove"
  * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
  * def prefix = ["#(utils.randomPrefix())"]
  * def gender = utils.randomGender()
  * def birthDate = utils.randomBirthDate()
  * def randomAddress = utils.randomAddress(birthDate)
  * def address = randomAddress
  * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }

@sandbox @testluck
Scenario: Replace attribute of an object
  # To replace the attribute of an object, you need to provide the id of the object you want to replace
  # in a preceding operation. (This is simlar to, but different from removing an object - we call 
  # "replace" instead of "test")
  * def nhsNumber = karate.env.includes('sandbox') ? '9000000009' : createPatientResponse.response.id 
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalVersion = parseInt(patientDetails.response.meta.versionId)
  * def givenName = patientDetails.response.name[0].given[0]
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
  * def options = ["Anne", "Mary", "Jane"]
  * def newGivenName = utils.pickDifferentOption(options, givenName)
  
  * def requestBody = 
  """
    {"patches":[
      {"op":"replace","path":"/name/0/id","value":"#(patientDetails.response.name[0].id)"}
      {"op":"replace","path":"/name/0/given/0","value":"#(newGivenName)"}
    ]}
    """
  * configure headers = call read('classpath:auth/auth-headers.js')   
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ expectedStatus: 200, nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)"}
  * match response.name[0].given[0] == newGivenName
  * match parseInt(response.meta.versionId) == originalVersion + 1

@sandbox
Scenario Outline: Replace the <property> property
  # Unlike replacing a property that is an object, there's no need to make a 
  # preceding test operation
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)

  * def currentValue = response[property]
  * def targetValue = utils.pickDifferentOption(options, currentValue)

  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * path 'Patient', nhsNumber
  * request {"patches": [{ "op": "replace", "path": "#('/' + property)", "value": "#(targetValue)" }]}
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * method patch
  * status 200
  * def newValue = response[property]
  * match newValue == targetValue
  * match parseInt(response.meta.versionId) == originalVersion + 1

  Examples:
    | nhsNumber     | property      | options!                             |  
    | 9736363066    | gender        | ['male', 'female', 'unknown']        |
    | 9736363074    | birthDate     | ["1985-10-26", "1955-11-05"]         |

Scenario: Healthcare worker can add, update and remove patient's emergency contact details
  * def nhsNumber = '9736363082'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)

# add emergency contact details
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * path 'Patient', nhsNumber
  * def mobileNumber = '0788548987'
  * request read('classpath:patients/requestDetails/add/emergencyContact.json')
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * method patch
  * status 200
  * match response contains {contact: '#notnull' }
  * match response.contact[*].telecom[*].value contains mobileNumber

  # update emergency contact
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)
  * def relationshipDetails = response.contact.find(c => c.telecom.some(t => t.value == mobileNumber && t.system == 'phone'))?.relationship
  * def contactId = response.contact.find(c => c.telecom.some(t => t.value == mobileNumber && t.system == 'phone'))?.id
  * def indexToUpdate = response.contact.findIndex(x => x.id == contactId)
  * def contactPathToUpdate = "/contact/" + indexToUpdate
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * def newMobileNumber = faker.phoneNumber()
  * path 'Patient', nhsNumber
  * request 
  """
  {
    "patches":[
      {"op":"replace",
      "path":"#(contactPathToUpdate)",
      "value":{
        "id": "#(contactId)",
        "relationship":"#(relationshipDetails)",
        "telecom":[
          {"system":"phone",
          "value":"#(newMobileNumber)"}
          ]}}]}
    """    
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502          
  * method patch
  * status 200
  * def versionIdAftUpdate = response.meta.versionId
  * match parseInt(versionIdAftUpdate) == originalVersion + 1
  * match response.contact[*].telecom[*].value contains newMobileNumber
    
    
  # remove emergency contact details
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)
  * def contactId = response.contact.find(c => c.telecom.some(t => t.value == newMobileNumber && t.system == 'phone'))?.id || 'Not Found'
  * def indexToRemove = response.contact.findIndex(x => x.id == contactId)
  * def contactPathToRemove = "/contact/" + indexToRemove
  * def contactValue = response.contact.find(x => x.id == contactId)
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * path 'Patient', nhsNumber

  * def patchRequest = 
  """
    {
      "patches": [
        {
          "op": "test",
          "path": "#(contactPathToRemove)",
          "value":"#(contactValue)"       
        },
        {
        "op": "remove",
          "path": "#(contactPathToRemove)"
        }
      ]
    }
  """
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * request patchRequest
  * method patch
  * status 200
  * def versionIdAftRemove = response.meta.versionId
  * match parseInt(versionIdAftRemove) == originalVersion + 1
  * match response.contact !contains contactValue
  
Scenario: Healthcare worker can update communication language-interpreter details
  * def nhsNumber = '9736363090'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)
  * def commExtensionUrl = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication"
  * def commLanguageDtls = response.extension.find(x => x.url == commExtensionUrl)
  # Test fails if the patient's communication details are present in the record

  * if (commLanguageDtls == null) {karate.fail('No value found for communication Language, stopping the test.')}
  * def interpreterDls = commLanguageDtls[1]
  * def commLanguageindex = response.extension.findIndex(x => x.url == commExtensionUrl)
  * def interpreterPath = "/extension/" + commLanguageindex + "/extension/1"
  * def interpreter = response.extension[commLanguageindex].extension[1].valueBoolean
  * def oppositeInterpreter = karate.eval('function getOppositeBoolean(value) { return !value; } getOppositeBoolean(' + karate.toString(interpreter) + ')')
  
# update comminication language interpreter required details
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * path 'Patient', nhsNumber
  * request 
  """
  {
    "patches":[
      {"op":"replace",
      "path":"#(interpreterPath)",
      "value": {
                "url": "interpreterRequired",
                "valueBoolean": "#(oppositeInterpreter)"              
                } 
      }]}
    """     
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502          
  * method patch
  * status 200
  * match parseInt(response.meta.versionId) == originalVersion + 1
  
Scenario: Send empty field on the update - interpreterRequired url is empty
  * def nhsNumber = '5900076067'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)
  * def commExtensionUrl = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication"
  * def commLanguageDtls = response.extension.find(x => x.url == commExtensionUrl)
  # Test fails if the patient's communication language details are present in the record

  * if (commLanguageDtls == null) {karate.fail('No value found for NHS communication, stopping the test.')}
  * def interpreterDls = commLanguageDtls[1]
  * def commLanguageindex = response.extension.findIndex(x => x.url == commExtensionUrl)
  * def interpreterPath = "/extension/" + commLanguageindex + "/extension/1"
  * def interpreter = response.extension[commLanguageindex].extension[1].valueBoolean
  * def oppositeInterpreter = karate.eval('function getOppositeBoolean(value) { return !value; } getOppositeBoolean(' + karate.toString(interpreter) + ')')
  
# Empty value on the patch
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')
  * path 'Patient', nhsNumber
  * request 
  """
  {
    "patches":[
      {"op":"replace",
      "path":"#(interpreterPath)",
      "value": {
                "url": " ",
                "valueBoolean": "#(oppositeInterpreter)"              
                } 
      }]}
    """    
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502          
  * method patch
  * status 400
  * def display = 'Patient cannot perform this action'
  * def diagnostics = "Invalid update with error - interpreterRequired cannot be removed"
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

@sandbox
Scenario: Healthcare worker can't remove usual name and DOB
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')
  * def nhsNumber = '9733162043'
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalVersion = parseInt(response.meta.versionId)
  * def usualNameIndex = response.name.findIndex(x => x.use == 'usual')
  * def pathToUsualName = "/name/"+ usualNameIndex 
  * def usualNameDetails = response.name.find(x => x.use == 'usual')
  * def birthDateValue = response.birthDate
  * def etag = karate.response.header('etag')
  # remove usual name
  * def diagnostics = "Forbidden update with error - not permitted to remove usual name"
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = etag
  * path 'Patient', nhsNumber

  * def patchRequest = 
  """
    {
      "patches": [
        {
          "op": "test",
          "path": "#(pathToUsualName)",
          "value":"#(usualNameDetails)"       
        },
        {
        "op": "remove",
          "path": "#(pathToUsualName)"
        }
      ]
    }
  """
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * request patchRequest
  * method patch
  * status 403
  * match response == expectedResponse
  # remove date of birth
  * def diagnostics = "Forbidden update with error - source not permitted to remove 'birthDate'"
  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = etag
  * path 'Patient', nhsNumber

  * def patchRequest = 
  """
    {
      "patches": [
        {
          "op": "test",
          "path": "/birthDate",
          "value":"#(birthDateValue)"       
        },
        {
        "op": "remove",
          "path": "/birthDate"
        }
      ]
    }
  """
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * request patchRequest
  * method patch
  * status 403
  * match response == expectedResponse