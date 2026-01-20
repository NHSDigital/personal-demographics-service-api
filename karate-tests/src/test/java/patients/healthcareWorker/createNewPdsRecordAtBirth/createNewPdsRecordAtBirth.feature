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
     
    # different mothers NHS and different motherDOB - creating new mother nhs number 

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

    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
      # second create at birth with different mother nhs number, mother dob
    * def createBabyResponse = call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 201, ignoreDuplicatesValue: true  }
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
      # third create at birth with different mother nhs number, mother dob
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { expectedStatus: 200 }
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