Feature: Search for a patient - MOAB cascading trace- application restricted access

Background:
  # schemas and validators that are required by the main schema checks
  * def utils = call read('classpath:helpers/utils.feature')
  * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json Address = karate.readAsString('classpath:schemas/Address.json')
  * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
  * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
  
  * json Patient = karate.readAsString('classpath:schemas/Patient.json')
  * json patientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/patientSearchResultEntry.json')
  * json SensitivePatient = karate.readAsString('classpath:schemas/SensitivePatient.json')
  * json sensitivePatientSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/sensitivePatientSearchResultEntry.json')
  
  # auth
  * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
  * def versionHeader = {'Accept': 'version=1.1'}
  * def mergeHeaders = karate.merge(requestHeaders, versionHeader)
  * configure headers = mergeHeaders 

  * url baseURL

Scenario: Search for a patient - correct DOB and transpose "given name" into "family name" field
  * def searchParams =
    """
    { _fuzzy-match: true, _exact-match: false, family: "amanda", given: "jak", gender: "female", birthdate: "1937-08-29", address-postcode: "DN20 8DU"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 1
  * match response.entry[0].resource.id == "9732019336"

Scenario: Search for a patient - incorrect DOB and correct family name and given name
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Magyn", given:"Jean", gender: "female", birthdate: "1957-09-23", address-postcode: "DN17 3AH"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response == read('classpath:schemas/searchSchemas/patientSearchBundle.json')
  * match response.total == 0 

Scenario: Search for a patient - incorrect DOB format and correct family name and given name
  * karate.set('expectedResponseStatus',400)
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Magyn", given:"Jean", gender: "female", birthdate: "19570723", address-postcode: "DN17 3AH"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * def diagnostics = "Invalid value - '19570723' in field 'birthdate'"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  * match response == expectedResponse  

@ignore
# need to investigate why this test is failing after data refresh and re-enable it 
Scenario: Search for a patient - include other name in the given name - joseph damien vs damien joseph
  * def searchParams =
    """
    { _fuzzy-match: true, family: "ALMOND", given:"Damien Joseph", gender: "male", birthdate: "2024-09-17"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1
  * match response.entry[0].resource.id == "9733163651"

Scenario: Search for a patient - Shortened forename - joseph vs Joe
  * def searchParams =
    """
    {_fuzzy-match: true, family: "ALMOND", given:"Joe", gender: "male", birthdate: "2024-09-17", address-postcode:"DN17 1BX"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1

Scenario: Search for a patient - fuzzy search with wild cards
  * karate.set('expectedResponseStatus',400)
  * def searchParams =
    """
    { _fuzzy-match: true, family: "ALMOND", given:"Joe*", gender: "male", birthdate: "2024-09-17", address-postcode:"DN17 1BX"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * def diagnostics = "Invalid search data provided - 'A fuzzy search was requested however the data given did not meet the fuzzy search criteria'"
  * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')
  * match response == expectedResponse

Scenario: Search for a patient - matching gp code
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "poole", given:"mark", gender: "male", birthdate: "1941-10-24", general-practitioner:"V81997"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1
  * match response.entry[0].resource.id == "9733163562" 

Scenario: Search for a patient - mismatching gp code 
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "poole", given:"mark", gender: "male", birthdate: "1941-10-24", general-practitioner:"V8198", address-postcode:"DN15 8JY"}
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "9733163562"  

Scenario: Search for a patient - Bad format postcode
  * def searchParams =
    """
    { _fuzzy-match: true, family: "poole", given:"mark", gender: "male", birthdate: "1941-10-24", address-postcode:"DN15258JY" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "9733163562" 

Scenario: Search for a patient - typo in postcode
  * def searchParams =
    """
    { _fuzzy-match: true, family: "poole", given:"mark", gender: "male", birthdate: "1941-10-24", address-postcode:"DN18 8JY" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "9733163562" 
   
 Scenario: Search for a patient - zz99 postcode
  * def searchParams =
    """
    { _fuzzy-match: true, family: "ORTON", given:"Ben", gender: "male", birthdate: "2017-05-20", address-postcode:"ZZ99 7CZ" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 0 

Scenario: Search for a patient - multi match based on email
  * def searchParams =
    """
    { _fuzzy-match: true, family: "smythe", given:"sam", birthdate: "ge2000-05-03", email:"test@test.com" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response == read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')  

Scenario: Search for a patient - single match based on email - typos in email address
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "GWIN", given:"Edgar", birthdate: "2024-09-20", email:"ed.gwin@test.com" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 0 
 
Scenario: Search for a patient - search based on historic details- historic given name
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Gwin", given:"Austin", birthdate: "2020-01-06", gender:"female" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.entry[0].resource.id == "9733163708" 

Scenario: Search for a patient - Typo error in given name - Justen vs justin
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "Gwin", given:"Justen", birthdate: "2020-01-06", gender:"female" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1
  * match response.entry[0].resource.id == "9733163708"  

Scenario: Search for a patient - unicode 
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "ATTSÖN", given: "PÀULINÉ", birthdate: "1960-07-14" , address-postcode:"DN19 7DX" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1
  * match response.entry[0].resource.id == "9693633148" 

Scenario: Search for a sensitive patient
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Godsoe", gender: "male",given:"Rodney", birthdate: "1936-02-24" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response == read('classpath:schemas/searchSchemas/sensitivePatientSearchBundle.json')
  * match response.entry[0].resource.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """ 

Scenario: Search for a patient - mobile number includes country code
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Almond", given: "Joseph", birthdate: "2024-09-17" , phone:"0091 9948052441" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1
  * match response.entry[0].resource.id == "9733163651" 

Scenario: Search for a patient - typo in mobile phone number
  * def searchParams =
    """
    { _fuzzy-match: true, family: "Almond", given: "Joseph", birthdate: "2024-09-17" , phone:"0091 9948072441", address-postcode:"DN17 1BX" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "9733163651" 

@ignore  
Scenario: Search for a patient - middle name in surname - Jason Willis
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "GLUCK", given: "Willis", birthdate: "1975-02-21" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "9733162744"   

Scenario: Search for a patient - initials in given name
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "MARR", given: "Toby J", birthdate: "2010-10-22" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "5900114988"    

Scenario: Search for a patient - spaces in given name
  * def searchParams =
    """
    {  _fuzzy-match: true, family: "MARR", given: "Anne Marie J", birthdate: "2013-10-22" }
    """
  * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
  * match response.total == 1 
  * match response.entry[0].resource.id == "5900109615"    
 
  Scenario: Get a patients details - Add version details header
    * configure headers = requestHeaders 
    * def nhsNumber = '9733162825'
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * match response.id == nhsNumber   