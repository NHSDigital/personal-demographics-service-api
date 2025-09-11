Feature: Patch patient - add errors

Covers error scenarios that can arise when trying to add data to a patient resource.

Background:
  * def utils = call read('classpath:helpers/utils.feature') 
  * def faker = Java.type('helpers.FakerWrapper')   
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * url baseURL

  * configure headers = call read('classpath:auth/auth-headers.js')

@sandbox
Scenario: Forbidden update example - multiple usual names cannot be added
  * def nhsNumber = '5900059332'
  * path 'Patient', nhsNumber
  * method get
  * status 200 
  * match response.name == '#[1]'

  * configure headers = call read('classpath:auth/auth-headers.js') 
  * header Content-Type = "application/json-patch+json"
  * header If-Match = karate.response.header('etag')

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
  * path 'Patient', nhsNumber
  * request {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * method patch
  * status 403
  * match response == expectedResponse

Scenario: Invalid Value - Add deceasedTime in yyyy-mm-ddTHH:MM:SS+01:00 format(PDS FHIR do not accepts Zero UTC offset)
  * def nhsNumber = '9736363287'
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * def originalEtag = karate.response.header('etag')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = originalEtag
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00+01:00"
  * path 'Patient', nhsNumber
  * request read('classpath:patients/requestDetails/add/deceasedDateTime.json')
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502    
  * method patch
  * status 400 
  * def diagnostics = `Invalid value - '${deceasedDate}' in field 'deceasedDateTime'`    
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  * match response == expectedResponse

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
  
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 201
  * def nhsNumber = response.id

  # Retrieve SCN number
  * configure headers = call read('classpath:auth/auth-headers.js')
  * path 'Patient', nhsNumber
  * retry until responseStatus != 503 && responseStatus != 502  
  * method get
  * status 200
  * def originalEtag = karate.response.header('etag')

  # Add deceased date - yyyy-mm-ddTHH:MM:SS+00:00 format
  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = originalEtag
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00+00:00"
  * path 'Patient', nhsNumber
  * request read('classpath:patients/requestDetails/add/deceasedDateTime.json')
  # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
  * retry until responseStatus != 503 && responseStatus != 502  
  * method patch
  * status 200 
  * match response.deceasedDateTime == deceasedDate
  * def etagAfterUpdate1 = karate.response.header('etag')

  # Replace deceased date - yyyy-mm-ddTHH:MM:SS format
  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = etagAfterUpdate1
  * def deceasedDate = utils.randomDateFromPreviousMonth() +"T00:00:00"
  * path 'Patient', nhsNumber
  * request {"patches": [{ "op": "replace", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }]}
  * method patch
  * status 200 
  # Response shows deceased time in yyyy-mm-ddTHH:MM:SS+00:00
  * match response.deceasedDateTime contains deceasedDate
  * def etagAfterUpdate2 = karate.response.header('etag')

   # Replace deceased date - yyyy-mm-dd format  
  * configure headers = call read('classpath:auth/auth-headers.js')
  * header Content-Type = "application/json-patch+json"
  * header If-Match = etagAfterUpdate2
  * def deceasedDate = utils.randomDateFromPreviousMonth()
  * path 'Patient', nhsNumber
  * request {"patches": [{ "op": "replace", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }]}
  * method patch
  * status 200 
  * match response.deceasedDateTime contains deceasedDate