Feature: Create a patient - Healthcare worker access mode

Note the use of the Karate retry functionality in this feature: we're
using it because the post patient functionality is subject to a spike
arrest policy, whereby requests can be rejected with a 429 response.

Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def faker = Java.type('helpers.FakerWrapper')
  * json periodSchema = karate.readAsString('classpath:schemas/Period.json')
  * json addressSchema = karate.readAsString('classpath:schemas/Address.json') 
  
  # the same registeringAuthority object is included in every request
  * def registeringAuthority = 
  """
  {
    "regAuthorityType.code": "x",
    "regAuthorityType.codeSystem": "2.16.840.1.113883.2.1.3.2.4.16.20",
    "regOrganisation.root": "2.16.840.1.113883.2.1.4.3",
    "regOrganisation.extension": "RWF",
    "authorPersonID": "",
    "authorSystemID": "230811201324",
    "deathStatus": "",
    "deceasedTime": "",
    "overallUpdateMode": "create"
  }
  """
  
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders  
  * url baseURL

  
Scenario: Post patient - new patient
  * def familyName = "Karate-test-" + utils.randomString(7)
  * def givenName = "Zebedee"
  * def prefix = "Mr"
  * def gender = "male"
  * def genderCode = "1"
  * def birthDate = utils.randomBirthDate()
  * def birthTime = birthDate.replaceAll("-","")
  * def postalCode = faker.postalCode()
  * def address = faker.streetAddress()
  
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/post-patient-request.json')
  * configure retry = { count: 5, interval: 1 }
  * retry until responseStatus != 429
  * method post
  * status 201
  * def nhsNumber = response.id
  * def expectedResponse = read('classpath:stubs/patient/new-nhs-number-response-template.json')
  * match response == expectedResponse
  * match response.address[0].line[0] == address
  * match response.address[0].postalCode == postalCode


Scenario: Fail to create a record for a new patient, single demographics match found
  # we rely on data that's already in the database for our existing record
  * def nhsNumber = "5900027104"
  * def familyName = "Karate-test-somwzqz"
  * def givenName = "Zebedee"
  * def prefix = "Mr"
  * def gender = "male"
  * def genderCode = "1"
  * def birthDate = "1954-10-26"
  * def birthTime = birthDate.replaceAll("-","")
  * def postalCode = "BAP4WG"
  * def address = "317 Stuart Streets"

  # we get one match in the database for these demographics
  * def demographics = ({ family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 1

  # so when we try to create a new patient using the same demographics, we get the single_match_found error
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request read('classpath:patients/healthcareWorker/post-patient-request.json')
  * method post
  * configure retry = { count: 5, interval: 1 }
  * retry until responseStatus != 429
  * status 200
  * match response == read('classpath:stubs/patient/errorResponses/single_match_found.json')


Scenario: Fail to create a record for a new patient, multiple demographics matches found
  # we rely on data that's already in the database for our existing records
  * def nhsNumber = "5900036502"
  * def familyName = "McCOAG"
  * def gender = "male"
  * def genderCode = "1"
  * def birthDate = "1997-08-20"
  * def birthTime = birthDate.replaceAll("-","")
  * def postalCode = "DN19 7UD"
  * def address = "1 Jasmine Court"

  # we get two matches in the database for these demographics
  # (NB the matching for post patient doesn't seem to ignore the space in the postalCode value,
  # so for this functionality there are only actually 2 matches, not 3)
  * def demographics = ({ family: familyName, birthdate: birthDate, gender: gender, "address-postalcode": postalCode })
  * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/getPatientByDemographics.feature', demographics)
  * assert patientSearchResults.response.total == 3

  # so when we try to create a new patient using the same demographics, we get the multiple_matches_found error
  * def requestBody = read('classpath:patients/healthcareWorker/post-patient-request.json')
  # there are a couple of things we don't need in this body
  * eval delete requestBody["name"]["name.givenName.name1"]
  * eval delete requestBody["name"]["name.prefix"]
  
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders
  * path "Patient"
  * request requestBody
  * configure retry = { count: 5, interval: 1 }
  * retry until responseStatus != 429
  * method post
  * status 200
  * match response == read('classpath:stubs/patient/errorResponses/multiple_matches_found.json')


Scenario: Negative path: invalid request body
  * path "Patient"
  * request { bananas: "in pyjamas" }
  * configure retry = { count: 5, interval: 1 }
  * retry until responseStatus != 429
  * method post
  * status 400
  * def diagnostics = response.issue[0].diagnostics
  * match response == read('classpath:stubs/patient/errorResponses/missing_value.json')
