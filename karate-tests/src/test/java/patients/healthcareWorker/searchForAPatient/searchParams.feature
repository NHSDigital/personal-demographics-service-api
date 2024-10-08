@sandbox
Feature: Search for a patient - Healthcare worker access mode 

These tests authenticate as one of the available test healthcare workers,
darren.mcdrew@nhs.net

Background:
  # schemas and validators that are required by the main schema checks
  * def utils = call read('classpath:helpers/utils.feature')
  * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json Address = karate.readAsString('classpath:schemas/Address.json')
  * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
  
  * json Patient = karate.readAsString('classpath:schemas/Patient.json')
  * json patientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/patientSearchResultEntry.json')
  * json SensitivePatient = karate.readAsString('classpath:schemas/SensitivePatient.json')
  * json sensitivePatientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/sensitivePatientSearchResultEntry.json')
  
  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL


Scenario:Search for a patient using parameters
  * path "Patient"
  * params  { family: "Jones", gender: "male", birthdate: "ge1992-01-01", _max-results: "6" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 1
  * match response.entry[0].resource.id == "5900035697"


@smoke-only
Scenario:Search for a patient using parameters (INT smoke test)
  * path "Patient"
  * params  { family: "Capon", gender: "male", birthdate: "eq1953-05-29" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 1
  * match response.entry[0].resource.id == "9693632117"

Scenario: Search for a "restricted" (sensitive) patient
  # When you get search results for a restricted patient, the response should not contain:
  # - address
  # - telecom
  # - generalPractitioner
  # this is reflected in the patientSearchBundleSensitive.json schema file
  * path 'Patient'
  * params { family: "Godsoe", gender: "male", birthdate: "eq1936-02-24" }
  * method get
  * status 200
  * match response.entry[0].resource.id == "9693632125"
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/sensitivePatientSearchBundle.json')
  * match response.entry[0].resource.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """

Scenario: Search without specifying gender
  * path 'Patient'
  * params { family: "Massam", birthdate: "eq1920-08-11" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.entry[0].resource.id == "9693632966"
  * match response.entry[0].resource.gender == "female"

Scenario: Search using a range for date of birth
  * path 'Patient'
  * params { family: "Massam", birthdate: "le1920-08-11" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.entry[0].resource.id == "9693632966"
  * match response.entry[0].resource.gender == "female"

Scenario: Wide search, multiple results
  * path 'Patient'
  * params { family: "YOUDS", birthdate: "1970-01-24" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 4
  * match each response.entry[*].resource.name[*].family == "YOUDS" 
  * match each response.entry[*].resource.birthDate == "1970-01-24"
  * match response.entry[*].resource.id == ["9693633679", "9693633687", "9693633695", "9693633709"]
  * match response.entry[*].resource.gender == ["male", "female", "unknown", "other"]

Scenario: Fuzzy match search - Family name is homophone of actual historic family name
  * path 'Patient'
  * params { _fuzzy-match: true, family: "Blogs", given: "Joe", birthdate: "1955-11-05" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 1
  * match response.entry[0].resource.name[0].family == "GARTON" 
  * match response.entry[0].resource.birthDate == "1955-11-05"
  * match response.entry[0].resource.id == "9693632109"

Scenario: Unicode search
  * path 'Patient'
  * params { _fuzzy-match: true, family: "ATTSÖN", given: "PÀULINÉ", birthdate: "1960-07-14" }
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 2
  * match response.entry[0].search.score == 0.9317
  * match response.entry[0].resource.id == "9693633148"
  * match response.entry[0].resource.gender == "female"
  * match response.entry[0].resource.birthDate == "1960-07-14"
  * match response.entry[0].resource.name[0].family == "attisón"
  * match response.entry[0].resource.name[0].given == ["Pauline"]

  * match response.entry[1].search.score == 0.9077
  * match response.entry[1].resource.id == "9693633121"
  * match response.entry[1].resource.gender == "female"
  * match response.entry[1].resource.birthDate == "1960-07-14"
  * match response.entry[1].resource.name[0].family == "attison"
  * match response.entry[1].resource.name[0].given == ["Pauline", "Mary", "Jane"]

Scenario: Too many matches
  # if you set _max-results to a number lower than the total number of matches for a query
  # then you get a Too Many Matches response...
  * path 'Patient'
  * params { family: "YOUDS", birthdate: "1970-01-24" }
  * method get
  * status 200
  * match response.total == 4
  
  * path 'Patient'
  * params { family: "YOUDS", birthdate: "1970-01-24", _max-results: 1 }
  * method get
  * status 200
  * match response == read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')

Scenario: Search should not return superseded patients record
  # 5900053636 was merged with 9732019395, search result shouldn't return 5900053636
  * path 'Patient'
  * def supersededRecord = '5900053636'
  * params { family: "CUFF", birthdate: "eq1926-01-07",gender: "female"}
  * method get
  * status 200
  * match response.total == 2
  * def idList = karate.jsonPath(response, "$.entry[*].resource.id")
  * match each idList != supersededRecord

Scenario: Simple search with other given name - Single match
  * def birthDateValue = "eq2000-05-05"
  * def genderValue =  "male"
  * def familyName = "Smith"
  * def givenNames = ["Sam","Bob" ]
  * path 'Patient'
  * params { family: '#(familyName)', gender: '#(genderValue)', birthdate: '#(birthDateValue)', given: '#(givenNames)' }
  * method get
  * status 200
  * assert response.total == 1
  * def givenNames = karate.jsonPath(response, "$.entry[*].resource.name[*].given[*]") 
  * match givenNames contains any ['Sam', 'Bob']

Scenario: Simple and Alphanumeric search with email and phone number - Multi match
  * def birthDateValue = "eq2000-05-05"
  * def emailValue = "test@test.com"
  * def phoneValue = "01234123123"
  * def genderValue =  "male"
  * path 'Patient'
  * params { family: "Smith", gender: '#(genderValue)', birthdate: '#(birthDateValue)', email: '#(emailValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * assert response.total > 1
  * def telecomValueList = karate.jsonPath(response, "$.entry[*].resource.telecom[*].value") 
  * match telecomValueList contains any ['#(phoneValue)', '#(emailValue)']
   # alphanumeric serach 
  * path 'Patient'
  * params { family: "Sm*", gender: '#(genderValue)', birthdate: '#(birthDateValue)', email: '#(emailValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * print response
  * assert response.total > 1
  * def telecomValueList = karate.jsonPath(response, "$.entry[*].resource.telecom[*].value") 
  * match telecomValueList contains any ['#(phoneValue)', '#(emailValue)']

Scenario: Simple and Alphanumeric search with email and phone number - no results
  * def birthDateValue = "eq2000-05-05"
  * def emailValue = "rubbish@test.com"
  * def phoneValue = "01234123123"
  * def genderValue =  "male"
  * path 'Patient'
  * params { family: "Smith", gender: '#(genderValue)', birthdate: '#(birthDateValue)', email: '#(emailValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * match response.total == 0
  # alphanumeric serach 
  * path 'Patient'
  * params { family: "Sm*",gender: '#(genderValue)', birthdate: '#(birthDateValue)', email: '#(emailValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * match response.total == 0

Scenario: Simple search with phone number including country code
  * def birthDateValue = "eq2017-09-06"
  * def familyValue = "Muir"
  * def phoneValue = "00917855986859"
  * def genderValue =  "male"
  * path 'Patient'
  * params { family: '#(familyValue)', gender: '#(genderValue)', birthdate: '#(birthDateValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * match response.total == 1
  * def telecomValueList = karate.jsonPath(response, "$.entry[*].resource.telecom[*].value") 
  * match telecomValueList contains ['#(phoneValue)'] 

Scenario: Include history flag for non fuzzy search
  * def birthDateValue = "eq2000-05-05"
  * def previousEmail = "Historic@historic.com"
  * def currentEmail = "New@new.com"  
  * def genderValue = "male"
  * def familyValue = "Smith"
  * path 'Patient'
  * params { family: '#(familyValue)', gender: '#(genderValue)', email: '#(previousEmail)', birthdate: '#(birthDateValue)' }
  * method get
  * status 200
  * match response.total == 0
  # include history flag
  * path 'Patient'
  * params { family: '#(familyValue)', gender: '#(genderValue)', birthdate: '#(birthDateValue)', email: '#(previousEmail)', _history: true }
  * method get
  * status 200
  * def emailValues = karate.jsonPath(response, "$.entry[*].resource.telecom[?(@.system == 'email')].value") 
  * print emailValues
  * match emailValues !contains previousEmail
  * match emailValues contains currentEmail
  * match response.total == 1

Scenario: Simple search with phone number including country code
  * def birthDateValue = "eq2017-09-06"
  * def familyValue = "Muir"
  * def phoneValue = "00917855986859"
  * def genderValue =  "male"
  * path 'Patient'
  * params { family: '#(familyValue)', gender: '#(genderValue)', birthdate: '#(birthDateValue)', phone: '#(phoneValue)' }
  * method get
  * status 200
  * match response.total == 1
  * def telecomValueList = karate.jsonPath(response, "$.entry[*].resource.telecom[*].value") 
  * match telecomValueList contains ['#(phoneValue)'] 

Scenario: wildcard search on postcode
  * def birthDate = "eq2000-05-05"
  * def gender = "male"
  * def family = "Smith"
  * def postcode = "DN17*"
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)',gender: '#(gender)', address-postalcode: '#(postcode)'}
  * method get
  * status 200
  * assert response.total >= 2
  * def postcodeList = karate.jsonPath(response, "$.entry[*].resource.address[*].postalCode")
  * def filteredList = karate.filter(postcodeList, function(x){ return x.startsWith('DN17') })
  * match filteredList != []

Scenario: Alphanumeric search with registered GP practice
  * def birthDate = "eq2015-10-22"
  * def family = "Me*"
  * def gp = "A20047"
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)', general-practitioner: '#(gp)'}
  * method get
  * status 200
  * assert response.total == 1
  * def gpList = karate.jsonPath(response, "$.entry[*].resource.generalPractitioner[*].identifier.value")
  * match gpList contains ['#(gp)']

Scenario: Simple search with date of death parameter
  * def birthDate = "ge1980-01-01"
  * def family = "TUNNEY"
  * def deathDate = "le2019-02-28"
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)', death-date: '#(deathDate)'}
  * method get
  * status 200
  * assert response.total == 1
  * def deceasedDate = karate.jsonPath(response, "$.entry[*].resource.deceasedDateTime")
  * match deceasedDate != null 

Scenario: Algorithm search with basic(given name, gender, date of birth and postal code) and phone number - no match -> single match -> multi match
  * def birthDate = "ge2000-05-03"
  * def family = "Smythe"
  * def gender = "male"
  * def given = "Mat"
  * def postcode = "DN17 4AA"
  * def email = "rubbish@work.com"
  * def phone = "01222111111"  
  # no search results 
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)', gender: '#(gender)', given: '#(given)', address-postalcode:'#(postcode)', email: '#(email)', phone: '#(phone)', _fuzzy-match: true }
  * method get
  * status 200
  * assert response.total == 0
  # single search result
  * def email = "test@test.com"
  * def nhsNumber = '5900022366'  
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)', gender: '#(gender)', given: '#(given)', address-postalcode:'#(postcode)', email: '#(email)', phone: '#(phone)', _fuzzy-match: true }
  * method get
  * status 200
  * assert response.total == 1 
  * match response.entry[0].resource.id == nhsNumber
  # Multi match
  * path 'Patient'
  * params { family: '#(family)', birthdate: '#(birthDate)', gender: '#(gender)', given: '#(given)', address-postalcode:'#(postcode)', _fuzzy-match: true }
  * method get
  * status 200
  * assert response.total >= 1 
  * def postcodeList = karate.jsonPath(response, "$.entry[*].resource.address[*].postalCode")
  * match postcodeList contains ['#(postcode)']

  Scenario: Search for a PDS record based on historic DOB, family name, gender
    * def historicDob = "2024-01-12"
    * def historicfamilyName = "HUME"
    * def historicGender = "female"
    * def givenName = "Casey"
    * def currentDob = "1999-09-09"
    * def currentGender = "male"
    * def currentFamilyName = "MED"
    # no pds records for non fuzzy search when historic dob is sent as query parameter
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(historicDob)', gender: '#(currentGender)' }
    * method get
    * status 200
    * assert response.total == 0
    # no pds records for non fuzzy search when historic gender is sent as query parameter
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(currentDob)', gender: '#(historicGender)' }
    * method get
    * status 200
    * assert response.total == 0
    # no pds records for non fuzzy search when historic family name is sent as query parameter
    * path 'Patient'
    * params { family: '#(historicfamilyName)', birthdate: '#(currentDob)', gender: '#(currentGender)' }
    * method get
    * status 200
    * assert response.total == 0
    #  Fuzzy matching should not return historic matches when historic dob is sent as query parameter
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(historicDob)', gender: '#(currentGender)', given: '#(givenName)', _fuzzy-match: true }
    * method get
    * status 200
    * assert response.total == 0
    # Fuzzy matching should return historic matches when historic gender is sent as query parameter
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(currentDob)', gender: '#(historicGender)', given: '#(givenName)', _fuzzy-match: true }
    * method get
    * status 200
    * assert response.total == 1
    * match response.entry[0].resource.gender == currentGender
    #  Fuzzy matching should return historic matches when historic family name is sent as query parameter
    * path 'Patient'
    * params { family: '#(historicfamilyName)', birthdate: '#(currentDob)', gender: '#(currentGender)', given: '#(givenName)', _fuzzy-match: true }
    * method get
    * status 200
    * assert response.total == 1
    * match response.entry[0].resource.name[0].family == currentFamilyName
    # Include history search should not return historic matches when historic dob is sent as query parameter
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(historicDob)', gender: '#(currentGender)', _history: true }
    * method get
    * status 200
    * assert response.total == 0
    #  Include history search should return historic matches when historic family name is sent as query parameter
    * path 'Patient'
    * params { family: '#(historicfamilyName)', birthdate: '#(currentDob)', gender: '#(currentGender)', _history: true }
    * method get
    * status 200
    * assert response.total == 1
    * match response.entry[0].resource.name[0].family == currentFamilyName

  Scenario: Historic matching shouldn't return hidden matches
    # Expect a record to exist with current given=Horace, dob=1956-05-02, family=LEEKE, postalcode=DN15 0AD, and hidden postalcode=DN16 3SS.
    * def hiddenPartialPostcode = "DN16 3SS"
    * def givenName = "Horace"
    * def currentDob = "1956-05-02"
    * def currentFamilyName = "LEEKE"
    # The query param postalcode should match the hidden postalcode, but not included in the result as the snippet is hidden instead of historic.
    * path 'Patient'
    * params { family: '#(currentFamilyName)', birthdate: '#(currentDob)', given: '#(givenName)', address-postalcode: '#(hiddenPartialPostcode)', _history: true }' }
    * method get
    * status 200
    * assert response.total == 0
