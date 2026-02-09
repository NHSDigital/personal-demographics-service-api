@no-oas 
Feature: Create a new PDS record at birth 
  Background:
  * def utils = call read('classpath:helpers/utils.feature')
  * def faker = Java.type('helpers.FakerWrapper')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json addressSchema = karate.readAsString('classpath:schemas/Address.json') 
    
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * def familyName = "ToRemove"
  * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
  * def prefix = ["#(utils.randomPrefix())"]
  * def gender = "female"
  * def birthDate = utils.randomBirthDateBetween16And40()
  * def randomAddress = utils.randomAddress(birthDate)
  * def address = randomAddress
  
  * call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
  * def motherNhsNumber = response.id 
  * url baseURL 
 
  @sandbox
  Scenario: create  PDS record at birth - successful
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { expectedStatus: 201 }
    * def nhsNumber = response.id
    * def expectedResponse = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create_record_at_birth_response_template.json')
    * match response == expectedResponse
    * match response.address[0].line[0] == address.line[1]
    * match responseHeaders['notification-id'] == '#present'

  Scenario: Fail to create a record for a new patient, single demographics match found
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 201 }
    * def nhsNumber = response.id
   
    # second create at birth with same demographic details
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')

   #  create at birth with same demographic details with ignore_potential_matches=true - expected algorithm 1 to match on demographics
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200, ignoreDuplicatesValue: true }
    * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')
  
  Scenario: Fail to create a record for a new patient, multiple demographics match found
       ##    1. Send a Create-Patient-at-Birth request with demographic details
             2. Wait until PDS record is created
             3. Get the record back and compare to confirm the PDS record has been created
             4. Send a second Create-Patient-at-Birth request with the almost the same demographic details,
                but with different mother nhs number and motherDoB and ignore_potential_matches set to true
             5. create a third Create-Patient-at-Birth request with the almost the same demographic details,
                but with different mother nhs number and motherDoB
             6. Check that a Multiple Matches Found response is returned

    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 201 }
    * def nhsNumber = response.id
     
    # different mothers NHS and different motherDOB - creating new mother nhs number and overriding global motherNhsNumber variables

    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = "female"
    * def birthDate = utils.randomBirthDateBetween16And40()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
    * configure headers = call read('classpath:auth/auth-headers.js')
    * def patientPayload = read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  
    * call read('classpath:patients/common/createPatient.feature@createPatient') { patientPayload:"#(patientPayload)", expectedStatus: 201 }
    * def motherNhsNumber = response.id 
    * def createRecordAtBirthPayload = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json')   
     # second create at birth with different mother nhs number, mother dob and ignore_potential_matches=true
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
      # second create at birth with different mother nhs number, mother dob - creating new mother nhs number and overriding global motherNhsNumber variables
    * def createBabyResponse = call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 201, ignoreDuplicatesValue: true  }
    * def nhsNumber2 = createBabyResponse.id
 
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = "female"
    * def birthDate = utils.randomBirthDateBetween16And40()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress 
    * configure headers = call read('classpath:auth/auth-headers.js')
  
    * def patientPayload = read('classpath:patients/healthcareWorker/createPatient/post-patient-request.json')
  
    * call read('classpath:patients/common/createPatient.feature@createPatient') { patientPayload:"#(patientPayload)", expectedStatus: 201 }
    * def motherNhsNumber = response.id 
    * def createRecordAtBirthPayload = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json')
 
      # third create at birth with different mother nhs number, mother dob
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 200 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json') 

 @sandbox-only
  Scenario: Fail to create a record for a new patient, single demographics match found
    # we rely on data that's already in the database for our existing record
    * def nhsNumber = "5900004899"
    * def familyName = "McMatch-Single"
    * def babyGivenName = ["Mickey"]
    * def babyGender = "male"
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
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
    * def demographics = ({ family: familyName, birthdate: babyBirthDate, gender: babyGender, "address-postalcode": address.postalCode })
    * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
    * assert patientSearchResults.response.total == 1

    # so when we try to create a new patient using the same demographics, we get the single_match_found error
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')

  @sandbox-only
  Scenario: Fail to create a record for a new patient, multiple demographics matches found
    # we rely on data that's already in the database for our existing record
    * def familyName = "McMatch-Multiple"
    * def babyGivenName = ["Leandro", "Gerry"]
    * def babyGender = "male"
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def address = 
      """
          {
      "period": { "start": "2024-03-19"},
      "use": "home",
      "postalCode": "DN19 7UD",
      "line": ["","1 Jasmine Court","","Doncaster"]
    }
      """
      
    # we get one match in the database for these demographics
    * def demographics = ({ family: familyName, birthdate: babyBirthDate, gender: babyGender, "address-postalcode": address.postalCode })
    * def patientSearchResults = karate.call('classpath:patients/healthcareWorker/searchForAPatient/getPatientByDemographics.feature', demographics)
    * assert patientSearchResults.response.total == 2

    # so when we try to create a new patient using the same demographics, we get the single_match_found error
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')  

  @sandbox  
  Scenario Outline: Negative path: missing value in request body - missing <missingValue>
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def createRecordAtBirthPayload = call read (payload)
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 400 }
  
    * def diagnostics = `Missing value - '${missingValue}'`
    * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')

  Examples:
    | payload                                                                                                                                      | missingValue                |
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-name-use.json          | entry/0/resource/name/0/use | 
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-birthdate.json         |entry/0/resource/birthDate|
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-gender.json            |entry/0/resource/gender|
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-address.json           |entry/0/resource/address|
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-birthweight-value.json |entry/1/resource/valueQuantity/value|
    | classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-mother-nhs-number.json |entry/7/resource/identifier/0/value|    

  @sandbox  
  Scenario Outline: Negative path: invalid value in request body - <property>
    * def validBabyGender = utils.randomGender()
    * def validBabyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = validBabyBirthDate + utils.randomTime()
    * def validBabyBirthOrder = 1
    * def validBabyBirthWeight = utils.randomBirthWeight()
    * def validBabyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]

    * json jsonValue = invalidValue

    * def babyGender = property == "gender" ? jsonValue : validBabyGender
    * def babyBirthDate = property == "birthDate" ? jsonValue : validBabyBirthDate
    * def babyBirthOrder = property == "birthOrder" ? jsonValue : validBabyBirthOrder
    * def babyBirthWeight = property == "birthWeight" ? jsonValue : validBabyBirthWeight
    * def address = property == "address" ? jsonValue : address
    * def babyGivenName = property == "givenName" ? jsonValue : validBabyGivenName
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 400 }

    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  
    Examples:
      | property            | invalidValue                | diagnostics                                                            |
      | givenName           | not an array                | Invalid value - 'not an array' in field 'entry/0/resource/name/0/given'|
      | address             | "another"                   | Invalid value - 'another' in field 'entry/0/resource/address/0'        |
      | gender              | other                       | Invalid value - 'other' in field 'gender'                              |
      | birthDate           | not-a-date                  | Invalid value - 'not-a-date' in field 'birthDate'                      |
      | givenName           | 'O`Brien'                   | Invalid value - 'O`Brien' in field 'entry/0/resource/name/0/given'     |
      | birthOrder          | 100                         | Invalid value - '100' in field 'entry/0/resource/multipleBirthInteger' |
      | birthWeight         | 35552                       | Invalid value - '35552' in field 'entry/1/resource/valueQuantity/value'|
    
  Scenario: Negative path: invalid "line" array defined as part of address
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def validAddress = utils.randomAddress(babyBirthDate)
  
    # our "validAddress" has a valid array for the "line" property. let's change that.
    # we only want one item in the array
    * def invalidLine = validAddress.line[1]
    * copy invalidAddress = validAddress
    * set invalidAddress.line = [invalidLine]
    * def address = invalidAddress
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    
    # you can't create a new patient if the line property doesn't match the spec
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 400 }
    * def diagnostics = "Invalid patient create data provided - 'address lines 1 and 4 or 2 and 4 must be completed as a minimum'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_CREATE.json')

  Scenario: Negative path: Mandatory resource or observation missing from request body
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def createRecordAtBirthPayload = call read ('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-delivery-location-resource.json')
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 400 }
    
    # you can't create a new patient if the mandatory resource/observation is missing
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 400 }
    * def diagnostics = "Too few values submitted - <json too long to display> in field 'entry'"
    * match response == read('classpath:mocks/stubs/errorResponses/TOO_FEW_VALUES_SUBMITTED.json')    

  Scenario: Negative path: Mandatory extension missing from patient resource
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def createRecordAtBirthPayload = call read ('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/MissingValuesPayload/create-pds-record-at-birth-missing-ethnicity-extension.json')
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 400 }
    
    # you can't create a new patient if the mandatory resource/observation is missing
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 400 }
    * match response.issue[0].diagnostics contains "in field 'entry/0/resource/extension'"   

  Scenario: Fail to create a record for a new patient when usual name has end date
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def address = randomAddress
    * def createRecordAtBirthPayload = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json')
    * def nameWithEndDate = 
    """
      {
          "family": "Rosey",
          "given": ["One"],
          "prefix": ["Mr"],
          "suffix": ["MBE"],
          "use": "usual",
          "period": {"start": "2020-01-01", "end": "#(babyBirthDate)"}
      }

    """
    * createRecordAtBirthPayload.entry[0].resource.name[0] = nameWithEndDate
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 400 }
    * def diagnostics = "Invalid patient create data provided - 'An end date can not be provided on usual name'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_CREATE.json')    

  Scenario: create a still birth PDS record at birth - formal death should have consistent still born indicatore equals 2,3 or 4
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def address = randomAddress
    * def createRecordAtBirthPayload = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json')
    * def deathNotificationExtension = 
    """
      {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus",
            "extension": [
              {
                "url": "deathNotificationStatus",
                "valueCodeableConcept": {
                  "coding": [
                    {
                      "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                      "code": "2"
                    }
                  ]
                }
              }
            ]
          }

    """
    * set createRecordAtBirthPayload.entry[0].resource.deceasedDateTime = babyBirthTime
    * set createRecordAtBirthPayload.entry[0].resource.extension = createRecordAtBirthPayload.entry[0].resource.extension.concat(deathNotificationExtension)
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 400 }
    * match response == read('classpath:mocks/stubs/errorResponses/INSERT_BIRTH_DEATH_STATUS_INCONSISTENT.json')  

    Scenario: create a still birth PDS record at birth - Successful
    * def babyGender = utils.randomGender() 
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def address = randomAddress
    * def stillbornCode = "2"  
    # 2=Antepartum, 3=Intrapartum, 4=Postpartum
    * def stillbornDisplay = "Antepartum"
    * def createRecordAtBirthPayload = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create-pds-record-at-birth.json')
    * def deathNotificationExtension = 
    """
      {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus",
            "extension": [
              {
                "url": "deathNotificationStatus",
                "valueCodeableConcept": {
                  "coding": [
                    {
                      "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                      "code": "2"
                    }
                  ]
                }
              }
            ]
          }

    """
    * set createRecordAtBirthPayload.entry[0].resource.deceasedDateTime = babyBirthTime
    * set createRecordAtBirthPayload.entry[0].resource.extension = createRecordAtBirthPayload.entry[0].resource.extension.concat(deathNotificationExtension) 
    * set createRecordAtBirthPayload.entry[2].resource.valueCodeableConcept.coding[0].code = stillbornCode
    * set createRecordAtBirthPayload.entry[2].resource.valueCodeableConcept.coding[0].display = stillbornDisplay
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { createRecordAtBirthPayload: "#(createRecordAtBirthPayload)", expectedStatus: 201 }
    * def nhsNumber = response.id
    * match nhsNumber == '#notnull'
    * match response.gender == babyGender
    * match response.birthDate == babyBirthDate
    * def deathNotification = karate.jsonPath(response, "$.extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus')]")[0]
    * match deathNotification.extension[0].valueCodeableConcept.coding[0].code == stillbornCode

   Scenario: create PDS record at birth and check the response includes the ethnicity extension when the feature is enabled for the endpoint
    * def babyGender = utils.randomGender()
    * def babyBirthDate = utils.randomNewbornDateLast5Days()
    * def babyBirthTime = babyBirthDate + utils.randomTime()
    * def babyBirthOrder = 1
    * def babyBirthWeight = utils.randomBirthWeight()
    * def babyGivenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { expectedStatus: 201 }
    * def nhsNumber = response.id
    * def expectedResponse = read('classpath:patients/healthcareWorker/createNewPdsRecordAtBirth/create_record_at_birth_response_template.json')
    * match response == expectedResponse
    * match responseHeaders['notification-id'] == '#present'
    * def newlyAllocatedNhsNumber = response.id

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * def odsCodeHeader = {'NHSD-End-User-Organisation-ODS': 'A20047'}
    * def mergedHeaders = karate.merge(requestHeaders, odsCodeHeader)
    * configure headers = mergedHeaders
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ expectedStatus: 200, nhsNumber:"#(newlyAllocatedNhsNumber)"}
    
    # ethnicity extension is enabled for asid:ODScode - 200000001215:A20047 
    * def ethnicityExtension = karate.jsonPath(response, "$.extension[?(@.url==  'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-EthnicCategory' )]")[0]
    * match ethnicityExtension != null
    * match ethnicityExtension.extension[0].url == '#present'
    * match ethnicityExtension.extension[0].url ==  'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-EthnicCategory' 
  