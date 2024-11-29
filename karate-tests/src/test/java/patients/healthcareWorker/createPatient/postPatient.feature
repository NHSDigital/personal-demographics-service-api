
Feature: Create a patient - Healthcare worker access mode

Note the use of the Karate retry functionality in this feature:

  - `* retry until responseStatus != 429 && responseStatus != 503`

We're using it because:
- the post patient functionality is subject to a spike arrest policy, 
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
    
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders  
  * url baseURL

  # Use this family name if the test is going to create patients - this is used by a batch job that cleans up the system database
  * def familyName = "ToRemove"

  
@sandbox 
Scenario: Post patient - new patient
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
  * def expectedResponse = read('classpath:patients/healthcareWorker/new-nhs-number-response-template.json')
  * match response == expectedResponse
  # In our request body, we send an array of address lines that include blank lines (" ") - but in the response, blank lines are removed,
  # so the array is shorter. We need to account for this in our match statement.
  * match response.address[0].line[0] == address.line[1]
  # the city may or may not get capitalised...
  * match response.address[0].line[1].toUpperCase() == address.line[3].toUpperCase()
  * match response.address[0].postalCode == address.postalCode

@sandbox 
Scenario: Fail to create a record for a new patient, single demographics match found
  # we rely on data that's already in the database for our existing record
  * def nhsNumber = "5900054586"
  * def familyName = "McMatch-Single"
  * def givenName = ["Mickey"]
  * def prefix = ["Mr"]
  * def gender = "male"
  * def birthDate = "1954-10-26"
  * def address = 
    """
    {
      "period": { "start": "2024-05-09"},
      "use": "home",
      "postalCode": "BAP 4WG",
      "line": ["", "317 Stuart Streets", "", "Glasgow"]
    }
    """
    
  # we get one match in the database for these demographics
  * def demographics = ({ family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": address.postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 1

  # so when we try to create a new patient using the same demographics, we get the single_match_found error
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * configure retry = { count: 5, interval: 6000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 200
  * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')

@sandbox 
Scenario: Fail to create a record for a new patient, multiple demographics matches found
  # we rely on data that's already in the database for our existing records
  * def givenName = ["Leandro", "Gerry"]
  * def familyName = "McMatch-Multiple"
  * def gender = "male"
  * def birthDate = "1997-08-20"
  * def address = 
    """
    {
      "period": { "start": "2024-03-19"},
      "use": "home",
      "postalCode": "DN19 7UD",
      "line": ["1 Jasmine Court"]
    }
    """
  # we get two matches in the database for these demographics
  * def demographics = ({ given: givenName, family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": address.postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 2

  # so when we try to create a new patient using the same demographics, we get the multiple_matches_found error
  * def requestBody = read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  * eval delete requestBody.name[0].prefix
  
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request requestBody
  * configure retry = { count: 5, interval: 7000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 200
  * match response == read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')

@sandbox
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

  @sandbox 
  Scenario Outline: Negative path: invalid value in request body - <property>
    # this is not an exhaustive test of all possible invalid values - see the integration tests for this
    # we're really just proving a few of the main properties here
    * def validGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def validBirthDate = utils.randomBirthDate()
    * def validGender = utils.randomGender()
    * def validAddress = utils.randomAddress(validBirthDate)
    
    # so we can put an array in the examples table and pass it as an array instead of a string,
    # convert the values to json as standard.
    * json jsonValue = invalidValue

    * def givenName = property == "givenName" ? jsonValue : validGivenName
    * def familyName = "ToRemove"
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = property == "gender" ? jsonValue : validGender
    * def birthDate = property == "birthDate" ? jsonValue : validBirthDate
    * def address = property == "address" ? jsonValue : validAddress
    
    * path "Patient"
    * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')

    * configure retry = { count: 5, interval: 10000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  
    Examples:
      | property            | invalidValue                | diagnostics                                                 |
      | givenName           | not an array                | Invalid value - 'not an array' in field 'name/0/given'      |
      | address             | ['another', 'array']        | Invalid value - '['another', 'array']' in field 'address/0' |
      | gender              | other                       | Invalid value - 'other' in field 'gender'         |
      | birthDate           | not-a-date                  | Invalid value - 'not-a-date' in field 'birthDate'           |

    
    Scenario: Negative path: invalid "line" array defined as part of address
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def validAddress = utils.randomAddress(birthDate)
  
    # our "validAddress" has a valid array for the "line" property. let's change that.
    # we only want one item in the array
    * def invalidLine = validAddress.line[1]
    * copy invalidAddress = validAddress
    * set invalidAddress.line = [invalidLine]
    * def address = invalidAddress
    
    # you can't create a new patient if the line property doesn't match the spec
    * path "Patient"
    * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * def diagnostics = "Invalid patient create data provided - 'address lines 1 and 4 or 2 and 4 must be completed as a minimum'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_CREATE.json')

  Scenario: Negative path: Address key url's and extensions are mandatory
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def address =
              """
              {
                  "use": "home",
                  "period": {
                      "start": "2020-01-01"
                  },
                  "id": "456",
                  "line": [
                      "1 High Street",
                      "",
                      "Doýnna TOPSONÔ",
                      "Leeds",
                      "West Yorkshire"
                  ],
                  "postalCode": "LS1 6AE",
                  "extension": [
                    {         
                  "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey"
                },
                {
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "code": "UPRN",
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType"
                            }
                        },
                        {
                            "url": "value",
                            "valueString": "123456789012"
                        }
                    ],
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey"
                }
                  ]
              }
              """
  
    # you can't create a new patient if the line property doesn't match the spec
    * path "Patient"
    * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * def diagnostics = `Missing value - 'address/0/extension/0/extension'`
    * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
  
  Scenario:Negative path: Create new patient with invalid telecom details
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
    * def patientPayload = read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
    * def telecom = 
    """
      [
        {
            "use": "home",
            "system": "email",
            "value": "testemail",
            "period": {
                "start": "2020-01-02",
                "end": "2021-01-02"
            }
        }
    ]
    """
    * patientPayload.telecom = telecom
    
    * path "Patient"
    * request patientPayload
    * configure retry = { count: 5, interval: 5000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * def diagnostics = "Invalid patient create data provided - 'email format is invalid'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_CREATE.json')
  
  @allocation-fix 
  Scenario Outline: Negative path: too many values in request body - <property>
    # this is not an exhaustive test of all possible too many values  values - see the integration tests for this
    # we're really just proving a few of the main properties here
    * def validGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def validBirthDate = utils.randomBirthDate()
    * def validGender = utils.randomGender()
    * def validAddress = utils.randomAddress(validBirthDate)
    
    # so we can put an array in the examples table and pass it as an array instead of a string,
    # convert the values to json as standard.
    * json jsonValue = invalidValue

    * def givenName = property == "givenName" ? jsonValue : validGivenName
    * def familyName = "ToRemove"
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = property == "gender" ? jsonValue : validGender
    * def birthDate = property == "birthDate" ? jsonValue : validBirthDate
    * def address = property == "address" ? jsonValue : validAddress
    
    * path "Patient"
    * request read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')

    * configure retry = { count: 5, interval: 10000 }
    * retry until responseStatus != 429 && responseStatus != 503
    * method post
    * status 400
    * match response == read('classpath:mocks/stubs/errorResponses/TOO_MANY_VALUES_SUBMITTED.json')
  
    Examples:
      | property            | invalidValue                                    | diagnostics                                                 |
      | givenName           | ["One", "Two", "Three", "Four", "Five", "six"]  | Too many values submitted - ['One', 'Two', 'Three', 'Four', 'Five', 'six'] in field 'name/0/given'      |

  