
Feature: Patch patient - Replace data

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * url baseURL

  @sandbox
  Scenario: Replace attribute of an object
    # To replace the attribute of an object, you need to provide the id of the object you want to replace
    # in a preceding operation. (This is simlar to, but different from removing an object - we call 
    # "replace" instead of "test")
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '5900056597'
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def givenName = response.name[0].given[0]

    * def options = ["Anne", "Mary", "Jane"]
    * def newGivenName = utils.pickDifferentOption(options, givenName)

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches":[
        {"op":"replace","path":"/name/0/id","value":"#(response.name[0].id)"}
        {"op":"replace","path":"/name/0/given/0","value":"#(newGivenName)"}
      ]}
      """
    * method patch
    * status 200
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
    * method patch
    * status 200
    * def newValue = response[property]
    * match newValue == targetValue
    * match parseInt(response.meta.versionId) == originalVersion + 1

    Examples:
      | nhsNumber     | property      | options!                             |  
      | 5900059243    | gender        | ['male', 'female', 'unknown']        |
      | 5900043320    | birthDate     | ["1985-10-26", "1955-11-05"]         |

    Scenario: Healthcare worker can add, update and remove patient's emergency contact details
      * def nhsNumber = '5900079066'
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
      * request read('classpath:patients/requestDetails/add/emergencyContact.json')
      * method patch
      * status 200
      * def versionIdAftAdd = response.meta.versionId
      * def contactDetails = response.contact
      * match response contains {contact: '#notnull' }
      * def relationshipDetails = contactDetails[0].relationship
      * def contactId = contactDetails[0].id
      * def indexToUpdate = response.contact.findIndex(x => x.id == contactId)
      * def contactPathToUpdateAndRemove = "/contact/" + indexToUpdate

      # update emergency contact
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
          "path":"#(contactPathToUpdateAndRemove)",
          "value":{
            "id": "#(contactId)",
            "relationship":"#(relationshipDetails)",
            "telecom":[
              {"system":"phone",
              "value":"#(newMobileNumber)"}
              ]}}]}
       """       
      * method patch
      * status 200
      * def updatedContact = response.contact.find(x => x.id == contactId)
      * def telecomValue = updatedContact.telecom[0].value
      * def versionIdAftUpdate = response.meta.versionId
      * match parseInt(versionIdAftUpdate) == parseInt(versionIdAftAdd) + 1
      * match telecomValue == newMobileNumber
     
      
      # remove emergency contact details
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
              "path": "#(contactPathToUpdateAndRemove)",
              "value":"#(updatedContact)"       
            },
            {
            "op": "remove",
              "path": "#(contactPathToUpdateAndRemove)"
            }
          ]
        }
      """
      * request patchRequest
      * method patch
      * status 200
      * def versionIdAftRemove = response.meta.versionId
      * match parseInt(versionIdAftRemove) == parseInt(versionIdAftUpdate) + 1
    Scenario: Healthcare worker can update communication language-interpreter details
      * def nhsNumber = '5900071413'
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
      * method patch
      * status 400
      * def display = 'Patient cannot perform this action'
      * def diagnostics = "Invalid update with error - interpreterRequired cannot be removed"
      * match response == read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')