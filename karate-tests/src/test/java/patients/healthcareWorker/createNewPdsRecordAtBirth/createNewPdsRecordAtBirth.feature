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

  @ignore
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
    * configure headers = requestHeaders 
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')

   #  expected algorithm 1 match on demographics
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth') { expectedStatus: 200 , ignoreDuplicatesValue:true }
    * match response == read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')
    
 @ignore
  Scenario: Fail to create a record for a new patient, multiple demographics match found
       ## 1. Send a Create-Patient-at-Birth request with demographic details
             2. Wait until PDS record is created
             3. Get the record back and compare to confirm the PDS record has been created
             4. Send a second Create-Patient-at-Birth request with the almost the same demographic details,
                but with birthWeight and motherDoB changed so only algorithm 1 returns a match, and with
                ignore-potential-matches set to False
             5. Check only algorithm 1 returned a match

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
    * configure headers = requestHeaders 
    # different mothers NHS and different motherDOB, creating new mother nhs number 

    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = "female"
    * def birthDate = utils.randomBirthDateBetween16And40()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
  
    * call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
    * def motherNhsNumber = response.id 
    * configure headers = requestHeaders 
      # second create at birth with different mother nhs number and mother dob
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { expectedStatus: 201 }
    * def nhsNumber2 = response.id

    * configure headers = requestHeaders 
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = "female"
    * def birthDate = utils.randomBirthDateBetween16And40()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
  
    * call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 201 }
    * def motherNhsNumber = response.id 

    * configure headers = requestHeaders
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@createRecordAtBirth ') { expectedStatus: 201 }
    * match response == read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json') 
