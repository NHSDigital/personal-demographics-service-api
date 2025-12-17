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