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
    * def familyName = "ToRemove"
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
    
    * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
    * def nhsNumber = karate.env.includes('sandbox') ? '9732110317' : createPatientResponse.response.id
	
	  * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
	
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
    * def requestBody = {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
    * def addedNameResponse = call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * def addedName = addedNameResponse.response.name.find(x => x.family == "Bloggs")
   
    * match addedName == expectedName
    * match parseInt(addedNameResponse.response.meta.versionId) == originalVersion + 1
    
    # 2. Remove the name we just added
    # ================================
    #
    # Now remove the name. To illustrate the remove behaviour, we do two tests here:
    # 1. We try to remove the name without first testing for it, which should fail
    # 2. We test for the name and then remove it, which should succeed

    # 2.1. You can't call a "remove" operation without first calling a "test" operation
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def etagAfterNameAddition = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
    * def nameID = patientDetails.response.name[1].id
    * def diagnostics = "Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')

    * configure headers = call read('classpath:auth/auth-headers.js')
    * def requestBody = {"patches":[{"op":"remove","path":"/name/1"}]}
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etagAfterNameAddition)",expectedStatus: 400}
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
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(patchBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * match response.name !contains { id: '#(nameID)' }
    * match parseInt(response.meta.versionId) == originalVersion + 1

  @sandbox
  Scenario: Add and remove patient suffix array
    # Create Patient
    * def familyName = "ToRemove"
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
    * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
    * def nhsNumber = karate.env.includes('sandbox') ? '9736363023' : createPatientResponse.response.id
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
    
    * def namePath = "/name/0/id" 
    * def nameId = createPatientResponse.response.name[0].id
    * def suffixPath = "/name/0/suffix"
    * def suffixArray = ["PhD", "MBBS"]
    
    # 3. Add a suffix array 
    # =====================
    
    * configure headers = call read('classpath:auth/auth-headers.js')
    * def requestBody =  
      """
      {"patches": [
        { "op": "add", "path": "#(namePath)", "value": "#(nameId)" },
        { "op": "add", "path": "#(suffixPath)", "value": "#(suffixArray)" }
      ]}
      """
    * def addSuffixResponse = call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * match addSuffixResponse.response.name[0].suffix == suffixArray
    * def scnAfterSuffixAddition = parseInt(addSuffixResponse.response.meta.versionId)
    * match scnAfterSuffixAddition == originalVersion + 1
    
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def etagAfterSuffix = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 

    # 4. Remove the whole suffix array
    # ================================
    # And you can get rid of the whole array of suffixes
    * configure headers = call read('classpath:auth/auth-headers.js')   
    * def requestBodyToRemoveSuffix = 
    """
    {"patches":[{"op":"test","path":"#(namePath)","value":"#(nameId)"},{"op":"remove","path":"#(suffixPath)"}]}
    """
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBodyToRemoveSuffix)", originalEtag:"#(etagAfterSuffix)",expectedStatus: 200}
    * match response.name[0].suffix == '#notpresent'
    * match parseInt(response.meta.versionId) == scnAfterSuffixAddition + 1
 
  @sandbox
  Scenario: Add suffix to the existing array of suffixes and then remove the same 
    # 1. Add new suffix to the array
    # ==============================
    # You can also add a new suffix to an existing array of suffixes
    # Create Patient
    * def familyName = "ToRemove"
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = ["#(randomAddress)"]
    * def suffix = ["PhD"]
    * def telecomValue = faker.mobileNumber()
    * def telecomUse = "mobile"
    * def createPatientResponse = call read('classpath:patients/common/createPatient.feature@createPatientWithMaximalData') { expectedStatus: 201 }
    * def nhsNumber =  karate.env.includes('sandbox') ? '9736363015' : createPatientResponse.response.id

    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
    * def firstNameIndexWithSuffix = patientDetails.response.name.findIndex(x => x.suffix != null)
    * def namePath = "/name/"+ firstNameIndexWithSuffix + "/id" 
    * def nameId = patientDetails.response.name.find(x => x.suffix != null).id
    * def suffixPath = "/name/"+ firstNameIndexWithSuffix + "/suffix/0"

  
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * def newSuffix = "Esquire"
    * def requestBody =
      """
      {"patches":[
        { "op": "add", "path": "#(namePath)", "value": "#(nameId)" },
        { "op": "add", "path": "#(suffixPath)", "value": "#(newSuffix)" }
      ]}
      """
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * match response.name[0].suffix contains newSuffix
    * match parseInt(response.meta.versionId) == originalVersion + 1
    
    # 2. Remove one of the suffixes we just added
    # ===========================================
    # We added an array of suffixes; now we're going to remove one of the suffixes in the
    # array.
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def scnVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 

    * def requestBody  = 
    """
    {"patches":[{"op":"test","path":"#(namePath)","value":"#(nameId)"},{"op":"remove","path":"#(suffixPath)"}]}
    """
    * configure headers = call read('classpath:auth/auth-headers.js')
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * match parseInt(response.meta.versionId) == scnVersion + 1 

  Scenario:  Healthcare worker can add and remove place of birth details(city and district)
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

    * def requestBody = read('classpath:patients/requestDetails/add/placeOfBirth.json')
    * def placeOBirthUrl = requestBody.patches[0].value.url
   
    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
    
    # add place of birth details
    * configure headers = call read('classpath:auth/auth-headers.js')   
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
    * def idAfterPlaceOfBirthUpdate = response.meta.versionId
    * def pobDetails = response.extension.find(x => x.url == placeOBirthUrl)
    * def etagAfterUpdate = responseHeaders.etag

    # Test fails if the patient's place of birth details are not present in the record
    * if (pobDetails == null) {karate.fail('No value found for place of Birth, stopping the test.')}
    * def pobIndex = response.extension.findIndex(x => x.url == placeOBirthUrl)
    * def pobPath =  "/extension/" + pobIndex

    #  remove place of birth details
    * def requestBody  = 
    """
    {
    "patches":[
        {
          "op":"test",
          "path":"#(pobPath)",
          "value":"#(pobDetails)"
        },
        {
          "op":"remove",
          "path":"#(pobPath)"
        }
    ]
    }
    """
    * configure headers = call read('classpath:auth/auth-headers.js')   
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(nhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(etagAfterUpdate)",expectedStatus: 200}
    * match parseInt(response.meta.versionId) == parseInt(idAfterPlaceOfBirthUpdate)+ 1
    * match response.extension[1] == '#notpresent'

Scenario:  Add an address to a PDS record that already contains a bad address- a temporary address without an end date

    # Leaving this test with static data , creating the nhsNumber is not allowed with temp address without an end date
    * def addressUpdateNhsNumber = '9733162515'
    * def addressType = "home"
    * def randomAddress = utils.randomAddress("2020-01-10")
    * def address = randomAddress

    * def patientDetails = call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(addressUpdateNhsNumber)", expectedStatus: 200 }
    * def originalVersion = parseInt(patientDetails.response.meta.versionId)
    * def originalEtag = patientDetails.responseHeaders['Etag'] ? patientDetails.responseHeaders['Etag'][0] : patientDetails.responseHeaders['etag'][0] 
    * def homeAddressIndex = patientDetails.response.address.findIndex(x => x.use == addressType)
    * def path = "/address/" + homeAddressIndex
    * def testOpValue = patientDetails.response.address[homeAddressIndex]
   
    * def requestBody = read('classpath:patients/requestDetails/add/addressUpdate.json')
    * call read('classpath:patients/common/updatePatient.feature@updatePatientDetails'){ nhsNumber:"#(addressUpdateNhsNumber)", requestBody:"#(requestBody)", originalEtag:"#(originalEtag)",expectedStatus: 200}
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