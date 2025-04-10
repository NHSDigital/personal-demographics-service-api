@no-oas @ignore
Feature:Create a patient - Healthcare worker access mode

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

Scenario:  Post patient and check response shows all 
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
  #check address line includes 5 lines with null values