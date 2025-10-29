Feature: Patch patient - Add and remove data
  
    This feature tests adding data to a patient and then remove it.
    We have extensive integration tests for the patch operations in TestBase scripts
    in the spineii repo, so we aren't going for exhaustive testing here, but rather
    illustrative tests that explain how to add and remove properties. 

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def faker = Java.type('helpers.FakerWrapper') 
    * def requestHeaders = call read('classpath:auth/auth-headers.js')

    * configure headers = requestHeaders

    * url baseURL

    @sandbox
  Scenario: Add and remove patient name
    * def nhsNumber = '9732110317'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def nameAlreadyExists = response.name.find(x => x.family == "Bloggs") != null
    * def firstNameIndex = nameAlreadyExists ? response.name.findIndex(x => x.family == "Bloggs") : null
    * def nameIdPath = "/name/"+ firstNameIndex + "/id"
    * def nameId = nameAlreadyExists ? response.name[firstNameIndex].id : null
    * def namePath = "/name/"+ firstNameIndex 

    * def removePatientName =
    """
    function(body) {
      var result = karate.call('classpath:helpers/patchRequest.feature', {
          baseURL: baseURL,
          requestBody: body,
          endpoint: 'Patient/' + nhsNumber,
          etag: karate.response.header('Etag')
      });
      originalVersion += 1
      return result
    }
    """

    # Remove patient name if already exists. Failed pipelines can leave data in an incorrect state
    * def body = utils.buildRemovePatchBody(nameIdPath, nameId, namePath)
    * def response = (nameAlreadyExists) ? removePatientName(body) : { body: response, responseHeaders: responseHeaders }
    
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
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 200
    * def addedName = response.name.find(x => x.family == "Bloggs")
   
    * match addedName == expectedName
    * match parseInt(response.meta.versionId) == originalVersion + 1
    
    # 2. Remove the name we just added
    # ================================
    #
    # Now remove the name. To illustrate the remove behaviour, we do two tests here:
    # 1. We try to remove the name without first testing for it, which should fail
    # 2. We test for the name and then remove it, which should succeed
    * path 'Patient', nhsNumber
    * method get
    * status 200
    
    # 2.1. You can't call a "remove" operation without first calling a "test" operation
    * def diagnostics = "Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = call read('classpath:auth/auth-headers.js')
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"remove","path":"/name/1"}]}
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 400
    * match response == expectedBody

    # 2.2. How to remove the name object correctly - define the id of the object 
    # you want to remove in the "test" operation
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def nameID = response.name[1].id
    * def patchBody = 
      """
      {"patches":[
          {"op":"test","path":"/name/1/id","value":"#(nameID)"}
          {"op":"remove","path":"/name/1"}
      ]}
      """
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request patchBody 
    * method patch
    * status 200
    * match response.name !contains { id: '#(nameID)' }
    * match parseInt(response.meta.versionId) == originalVersion + 1

  @sandbox
  Scenario: Add and remove patient suffix array
    * def nhsNumber = '9736363023'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)

    * def namePath = "/name/0/id" 
    * def nameId = response.name[0].id
    * def suffixPath = "/name/0/suffix"
    * def suffixArray = ["PhD", "MBBS"]

    * def removePatientSuffix =
    """
    function(body) {
      var result = karate.call('classpath:helpers/patchRequest.feature', {
          baseURL: baseURL,
          requestBody: body,
          endpoint: 'Patient/' + nhsNumber,
          etag: karate.response.header('Etag')
      });
      originalVersion += 1
      return result
    }
    """

    # Remove patient name if already exists. Failed pipelines can leave data in an incorrect state
    * def body = utils.buildRemovePatchBody(namePath, nameId, suffixPath)
    * def response = (response.name[0].suffix == null) ? { body: response, responseHeaders: responseHeaders } : removePatientSuffix(body)
    
    # 3. Add a suffix array 
    # =====================
    * match response.name[0].suffix == "#notpresent"
    
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches": [
        { "op": "add", "path": "#(namePath)", "value": "#(nameId)" },
        { "op": "add", "path": "#(suffixPath)", "value": "#(suffixArray)" }
      ]}
      """
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 200
    * match response.name[0].suffix == suffixArray
    * match parseInt(response.meta.versionId) == originalVersion + 1

    # 4. Remove the whole suffix array
    # ================================
    # And you can get rid of the whole array of suffixes
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)    
    * def response = removePatientSuffix(body)
    * match response.response.name[0].suffix == '#notpresent'
    * match parseInt(response.response.meta.versionId) == originalVersion
 
  @sandbox
  Scenario: Add suffix to the existing array of suffixes and then remove the same 
    # 1. Add new suffix to the array
    # ==============================
    # You can also add a new suffix to an existing array of suffixes
    * def nhsNumber = '9736363015'
    * def suffix = "Esquire"

    * def removeSuffix =
    """
    function(body) {
      var result = karate.call('classpath:helpers/patchRequest.feature', {
          baseURL: baseURL,
          requestBody: body,
          endpoint: 'Patient/' + nhsNumber,
          etag: karate.response.header('Etag')
      });
      originalVersion += 1
      return result
    }
    """

    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def firstNameIndexWithSuffix = response.name.findIndex(x => x.suffix != null)
    * def namePath = "/name/"+ firstNameIndexWithSuffix + "/id" 
    * def nameId = response.name.find(x => x.suffix != null).id
    * def suffixPath = "/name/"+ firstNameIndexWithSuffix + "/suffix/0"

    # Remove suffix if already exists. Failed pipelines can leave data in an incorrect state
    * def body = utils.buildRemovePatchBody(namePath, nameId, suffixPath)
    * def response = (response.name[0].suffix.includes(suffix)) ? removeSuffix(body) : { body: response, responseHeaders: responseHeaders }
   
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', nhsNumber
    * request
      """
      {"patches":[
        { "op": "add", "path": "#(namePath)", "value": "#(nameId)" },
        { "op": "add", "path": "/name/0/suffix/0", "value": "#(suffix)" }
      ]}
      """
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 200
    * match response.name[0].suffix contains suffix
    * match parseInt(response.meta.versionId) == originalVersion + 1
    
    # 2. Remove one of the suffixes we just added
    # ===========================================
    # We added an array of suffixes; now we're going to remove one of the suffixes in the
    # array.
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
  
    * def body = utils.buildRemovePatchBody(namePath, nameId, suffixPath)
    * def response = removeSuffix(body)
    * match parseInt(response.response.meta.versionId) == originalVersion

  Scenario:  Healthcare worker can add and remove place of birth details(city and district)

    * def placeOfBirthNhsNumber = '9736363031'
    * def requestBody = read('classpath:patients/requestDetails/add/placeOfBirth.json')
    * def placeOBirthUrl = requestBody.patches[0].value.url
    
    * def removePlaceOfBirth =
    """
    function(body) {
    var result = karate.call('classpath:helpers/patchRequest.feature', {
        baseURL: baseURL,
        requestBody: body,
        endpoint: 'Patient/' + placeOfBirthNhsNumber,
        etag: karate.response.header('Etag')
    });
    return result
    }
    """

    # Check if place of birth exists and remove
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * path 'Patient', placeOfBirthNhsNumber
    * method get
    * status 200
    
    # Remove place of birth if already exists. Failed pipelines can leave data in an incorrect state
    * def originalVersion = parseInt(response.meta.versionId)
    * def pobIndex = response.extension ? response.extension.findIndex(x => x.url == placeOBirthUrl) : null
    * def pobPath =  "/extension/" + pobIndex
    * def pobDetails = response.extension ? response.extension.find(x => x.url == placeOBirthUrl) : null
    * def body = utils.buildRemovePatchBody(pobPath, pobDetails)
    * def response = (pobDetails == null) ? { body: response, responseHeaders: responseHeaders } : removePlaceOfBirth(body)

    #add place of birth details
    * header Content-Type = "application/json-patch+json"
    * def etagKey = Object.keys(response.responseHeaders).find(k => k.toLowerCase() === 'etag')
    * header If-Match = etagKey ? response.responseHeaders[etagKey][0] : null
    * path 'Patient', placeOfBirthNhsNumber
    * request requestBody
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 200 
    * def idAfterPlaceOfBirthUpdate = response.meta.versionId
    * def pobDetails = response.extension.find(x => x.url == placeOBirthUrl)

    # Test fails if the patient's place of birth details are not present in the record
    * if (pobDetails == null) {karate.fail('No value found for place of Birth, stopping the test.')}
    * def pobIndex = response.extension.findIndex(x => x.url == placeOBirthUrl)
    * def pobPath =  "/extension/" + pobIndex

    #  remove place of birth details
    * def body = utils.buildRemovePatchBody(pobPath, pobDetails)
    * def response = removePlaceOfBirth(body)
    * match parseInt(response.response.meta.versionId) == parseInt(idAfterPlaceOfBirthUpdate)+ 1
    * match response.response.extension[1] == '#notpresent'

Scenario:  Add an address to a PDS record that already contains a bad address- a temporary address without an end date

    * def addressUpdateNhsNumber = '9733162515'
    * def addressType = "home"
    * def randomAddress = utils.randomAddress("2020-01-10")
    * def address = randomAddress

    * path 'Patient', addressUpdateNhsNumber
    * method get
    * status 200 
    * def originalVersion = response.meta.versionId 
    * def homeAddressIndex = response.address.findIndex(x => x.use == addressType)
    * def path = "/address/" + homeAddressIndex
    * def testOpValue = response.address[homeAddressIndex]
  
    * header Content-Type = "application/json-patch+json"  
    * header If-Match = karate.response.header('etag')
    * path 'Patient', addressUpdateNhsNumber
    * request read('classpath:patients/requestDetails/add/addressUpdate.json')
    # Adding re-try when "sync-wrap failed to connect to spine"
    * retry until responseStatus != 503 && responseStatus != 502
    * method patch
    * status 200
    * def postcode = response.address[homeAddressIndex].postalCode
    * match parseInt(response.meta.versionId) == parseInt(originalVersion)+ 1
    * match postcode == randomAddress.postalCode

@no-oas
Scenario: Add deceasedTime in yyyy-mm-ddTHH:MM:SS+00:00 format and then replace it to yyyy-mm-dd
  # Create Patient
  * def familyName = "ToRemove"
  * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
  * def prefix = ["#(utils.randomPrefix())"]
  * def gender = utils.randomGender()
  * def birthDate = utils.randomBirthDate()
  * def randomAddress = utils.randomAddress(birthDate)
  * def address = randomAddress
  
  * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
  * def nhsNumber = createPatientResponse.response.id

  # Retrieve SCN number
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * def originalVersion = parseInt(patientDetails.response.meta.versionId)
  * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 

  # Add deceased date - yyyy-mm-ddTHH:MM:SS+00:00 format
  * configure headers = call read('classpath:auth/auth-headers.js')
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00+00:00"
  * def requestBody = read('classpath:patients/requestDetails/add/deceasedDateTime.json')
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
  * match response.deceasedDateTime == deceasedDate
  * def etagAfterUpdate1 = responseHeaders.etag

  # Replace deceased date - yyyy-mm-ddTHH:MM:SS format
  * configure headers = call read('classpath:auth/auth-headers.js')
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00"
  * def requestBody = {"patches": [{ "op": "replace", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }]}
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etagAfterUpdate1)",expectedStatus: 200}
  # Response shows deceased time in yyyy-mm-ddTHH:MM:SS+00:00
  * match response.deceasedDateTime contains deceasedDate
  * def etagAfterUpdate2 = responseHeaders.etag

   # Replace deceased date - yyyy-mm-dd format  
  * configure headers = call read('classpath:auth/auth-headers.js')
  * def deceasedDate = utils.randomDateFromPreviousMonth()
  * def requestBody = {"patches": [{ "op": "replace", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }]}
  * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etagAfterUpdate2)",expectedStatus: 200}
  * match response.deceasedDateTime contains deceasedDate    