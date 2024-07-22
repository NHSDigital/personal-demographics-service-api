@sandbox
Feature: Search for a patient - Healthcare worker access mode - "Simple search"

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

Scenario: Fuzzy match search
  * path 'Patient'
  * params { _fuzzy-match: true, family: "Garton", given: "Bill", birthdate: "1946-06-23" }
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