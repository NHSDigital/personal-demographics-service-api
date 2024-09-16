
Feature: Patch patient - Add and remove data
  
    This feature tests adding data to a patient and then remove it.
    We have extensive integration tests for the patch operations in TestBase scripts
    in the spineii repo, so we aren't going for exhaustive testing here, but rather
    illustrative tests that explain how to add and remove properties. 

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    
    * configure headers = call read('classpath:auth/auth-headers.js')
    
    * url baseURL
    * def nhsNumber = '5900056449'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def patientObject = response
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * copy originalNameArray = response.name

  @sandbox
  Scenario: Add and remove patient data
    * match response.name == "#[1]"
    
    # 1. Add a new name to the array of patient names
    # ===============================================
    #
    # Note how we set {"use": "old"} here, as we can't have multiple "usual" names
    * def newName = 
    """
    {
      "use": "old",
      "period": {"start": "2019-12-31"},
      "prefix": ["Dr"],
      "given": ["Joe", "Horation", "Maximus"],
      "family": "Bloggs",
      "suffix": ["PhD"],
    }
    """
    # the returned name object will be the same, with an additional id field
    * copy expectedName = newName
    * set expectedName.id = "#string"

    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
    * method patch
    * status 200
    * match response.name == "#[2]"
    * match response.name[1] == expectedName
    * match parseInt(response.meta.versionId) == originalVersion + 1
    
    # 2. Remove the name we just added
    # ================================
    #
    # Now remove the name. To illustrate the remove behaviour, we do two tests here:
    # 1. We try to remove the name without first testing for it, which should fail
    # 2. We test for the name and then remove it, which should succeed
    * def originalVersion = parseInt(response.meta.versionId)
    * def nameID = response.name[1].id
    * def etag = karate.response.header('etag')
    
    # 2.1. You can't call a "remove" operation without first calling a "test" operation
    * def diagnostics = "Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = call read('classpath:auth/auth-headers.js')
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/1"}]}
    * method patch
    * status 400
    * match response == expectedBody

    # 2.2. How to remove the name object correctly - define the id of the object 
    # you want to remove in the "test" operation
    * def patchBody = 
      """
      {"patches":[
          {"op":"test","path":"/name/1/id","value":"#(nameID)"}
          {"op":"remove","path":"/name/1"}
      ]}
      """
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    * path 'Patient', nhsNumber
    * request patchBody 
    * method patch
    * status 200
    * match response.name == "#[1]"
    * match response.name == originalNameArray
    * match parseInt(response.meta.versionId) == originalVersion + 1

    # 3. Add a suffix array 
    # =====================
    * def originalVersion = parseInt(response.meta.versionId)
    * match response.name[0].suffix == "#notpresent"

    * def suffixArray = ["PhD", "MBBS"]
    
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches": [
        { "op": "add", "path": "/name/0/id", "value": "#(patientObject.name[0].id)" },
        { "op": "add", "path": "/name/0/suffix", "value": "#(suffixArray)" }
      ]}
      """
    * method patch
    * status 200
    * match response.name[0].suffix == suffixArray
    * match parseInt(response.meta.versionId) == originalVersion + 1
    
    # 4. Remove one of the suffixes we just added
    # ===========================================
    # We added an array of suffixes; now we're going to remove one of the suffixes in the
    # array.
    * def originalVersion = parseInt(response.meta.versionId)

    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')      
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches":[
        { "op": "test", "path": "/name/0/id", "value": "#(patientObject.name[0].id)" },
        { "op": "remove","path": "/name/0/suffix/0" }
      ]}
      """ 
    * method patch
    * status 200
    * match response.name[0].suffix == ["MBBS"]
    * match parseInt(response.meta.versionId) == originalVersion + 1

    # 5. Add new suffix to the array
    # ==============================
    # You can also add a new suffix to an existing array of suffixes
    * def originalVersion = parseInt(response.meta.versionId)

    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request
      """
      {"patches":[
        { "op": "add", "path": "/name/0/id", "value": "#(patientObject.name[0].id)" },
        { "op": "add", "path": "/name/0/suffix/0", "value": "Esquire" }
      ]}
      """
    * method patch
    * status 200
    * match response.name[0].suffix == ["Esquire", "MBBS"]
    * match parseInt(response.meta.versionId) == originalVersion + 1

    # 6. Remove the whole suffix array
    # ================================
    # And you can get rid of the whole array of suffixes
    * def originalVersion = parseInt(response.meta.versionId)

    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches":[
        { "op": "test", "path": "/name/0/id", "value": "#(patientObject.name[0].id)" },
        { "op": "remove", "path": "/name/0/suffix" }
      ]}
      """
    * method patch
    * status 200
    * match response.name[0].suffix == '#notpresent'
    * match parseInt(response.meta.versionId) == originalVersion + 1


  Scenario:  Healthcare worker can add and remove place of birth details(city and district)
    * def placeOfBirthNhsNumber = '5900077810'
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * path 'Patient', placeOfBirthNhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)

    #add place of birth details

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', placeOfBirthNhsNumber
    * def requestBody = read('classpath:patients/requestDetails/add/placeOfBirth.json')
    * def placeOBirthUrl = requestBody.patches[0].value.url
    * request requestBody
    * method patch
    * status 200 
    * def idAftPod = response.meta.versionId
    * def pobDetails = response.extension.find(x => x.url == placeOBirthUrl)
    # Test fails if the patient's place of birth details are not present in the record
  
    * if (pobDetails == null) {karate.fail('No value found for place of Birth, stopping the test.')}
    * def pobIndex = response.extension.findIndex(x => x.url == placeOBirthUrl)
    * def pobPath =  "/extension/" + pobIndex
    
     # remove place of birth details

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', placeOfBirthNhsNumber
    * request 
    """
      {
        "patches": [
          {
            "op": "test",
            "path": "#(pobPath)",
            "value": "#(pobDetails)"     
          },
          {
           "op": "remove",
            "path": "#(pobPath)" 
          }
        ]
      }
      """ 
    * method patch
    * status 200
    * match parseInt(response.meta.versionId) == parseInt(idAftPod)+ 1
    * match response.extension[1] == '#notpresent'

