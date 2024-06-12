@sandbox @no-oas @ignore
Feature: Create a patient - Healthcare worker access mode

Note the use of the Karate retry functionality in this feature:

  - `* retry until responseStatus != 429 && responseStatus != 503`

We're using it because:
- the post patient functionality is subject to a spik arrest policy, 
    whereby requests can be rejected with a 429 response.
- the system may also throw a SERVICE_UNAVAILABLE error - "The downstream 
  domain processing has not completed within the configured timeout period. 
  Using the same 'X-Request-ID' header, retry your request after the time 
  specified by the 'Retry-After' response header."

The intervals between retries are set to be different for each scenario,
to try to stagger the requests and avoid the spike arrest policy.

Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def faker = Java.type('helpers.FakerWrapper')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json addressSchema = karate.readAsString('classpath:schemas/Address.json') 
    
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders  
  * url baseURL

Scenario: Post patient - new patient
  # Don't change the familyName - this is used by a batch job that cleans up the system database
  * def familyName = "ToRemove"

  * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
  * def prefix = ["#(utils.randomPrefix())", "#(utils.randomPrefix())"]
  * def gender = utils.randomGender()
  * def birthDate = utils.randomBirthDate()

  * def address = utils.randomAddress()
  * def addressStartDate = utils.randomDate(birthDate)
  * def postalCode = address.postalCode
  * def street = `${utils.randomInt()} ${address.street}`
  * def address = ["#(street)", "#(address.city)", '{"hello": "world"}']
  
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * configure retry = { count: 5, interval: 5000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 201
  * def nhsNumber = response.id
  * def expectedResponse = read('classpath:patients/healthcareWorker/new-nhs-number-response-template.json')
  * match response == expectedResponse
  * match response.address[0].line[0] == address[0]
  # the city may or may not get capitalised...
  * match response.address[0].line[1].toUpperCase() == address[1].toUpperCase()
  * match response.address[0].postalCode == postalCode

Scenario: Fail to create a record for a new patient, single demographics match found
  # we rely on data that's already in the database for our existing record
  * def nhsNumber = "5900054586"
  * def familyName = "McMatch-Single"
  * def givenName = ["Mickey"]
  * def prefix = ["Mr"]
  * def gender = "male"
  * def birthDate = "1954-10-26"
  * def postalCode = "BAP 4WG"
  * def address = ["317 Stuart Streets"]
  * def addressStartDate = "2024-05-09"

  # we get one match in the database for these demographics
  * def demographics = ({ family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 1

  # so when we try to create a new patient using the same demographics, we get the single_match_found error
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * configure retry = { count: 5, interval: 6000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 200
  * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')

Scenario: Fail to create a record for a new patient, multiple demographics matches found
  # we rely on data that's already in the database for our existing records
  * def givenName = ["Leandro", "Gerry"]
  * def familyName = "McMatch-Multiple"
  * def gender = "male"
  * def birthDate = "1997-08-20"
  * def postalCode = "DN19 7UD"
  * def address = ["1 Jasmine Court"]
  * def addressStartDate = "2024-03-19"

  # we get two matches in the database for these demographics
  * def demographics = ({ given: givenName, family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 2

  # so when we try to create a new patient using the same demographics, we get the multiple_matches_found error
  * def requestBody = read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * eval delete requestBody.name[0].prefix
  
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request requestBody
  * configure retry = { count: 5, interval: 7000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 200
  * match response == read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')

Scenario Outline: Negative path: missing value in request body - missing <missingValue>
  * path "Patient"
  * request payload
  * configure retry = { count: 5, interval: 10000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 400
  * def diagnostics = `Missing value - '${missingValue}'`
  * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')

  Examples:
    | payload                                                                                                        | missingValue |
    | { "bananas": "in pyjamas" }                                                                                    | name         | 
    | { "name": { "family": "Smith" } }                                                                              | address      |
    | { "name": { "family": "Smith" }, "address": [{ "line": ["1"] }] }                                              | gender       |
    | { "name": { "family": "Smith" }, "address": [{ "line": ["1"] }], "gender": "male" }                            | birthDate    |

  Scenario Outline: Negative path: invalid value in request body - <invalidProperty>
    # this is not an exhaustive test of all possible invalid values - see the integration tests for this
    # we're really just proving a few of the main properties here
    * def givenName = property == "givenName" ? invalidValue : ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = property == "gender" ? invalidValue : utils.randomGender()
    * def birthDate = property == "birthDate" ? invalidValue : utils.randomBirthDate()
  
    * def address = property == "address" ? invalidValue : utils.randomAddress()
    * def addressStartDate = utils.randomBirthDate()
    * def postalCode = address.postalCode
    * def street = `${utils.randomInt()} ${address.street}`
    * def address = ["#(street)", "#(address.city)", '{"hello": "world"}']
    
    * path "Patient"
    * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')

    * configure retry = { count: 5, interval: 10000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  
    Examples:
      | property            | invalidValue      | diagnostics                                                 |
      | givenName           | not an array      | Invalid value - 'not an array' in field 'name/0/given'      |
      | address             | [not, an, object] | Invalid value - 'None' in field 'address/0/postalCode'      |
      | gender              | notAValidOption   | Invalid value - 'notAValidOption' in field 'gender'         |
      | birthDate           | not-a-date        | Invalid value - 'not-a-date' in field 'birthDate'           | 
      