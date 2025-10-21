    @no-oas
Feature: Create patient - not permitted for application-restricted users
    A spike arrest policy is in a place for this endpoint, and the spike arrest policy 
    takes priority over the authentication rules. Even though we can't create a patient
    in this scenario, we have to accommodate the spike arrest policy, hence the retry...

  Background:
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders  
    * url baseURL
    * def utils = call read('classpath:helpers/utils.feature')
 
  Scenario: Invalid Method error should be raised with application-restricted users
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def prefix = ["#(utils.randomPrefix())"]
    * def gender = utils.randomGender()
    * def birthDate = utils.randomBirthDate()
    * def randomAddress = utils.randomAddress(birthDate)
    * def address = randomAddress
    * call read('classpath:patients/common/createPatient.feature@createPatient') { expectedStatus: 403 }
    * def display = "Cannot create resource with application-restricted access token"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    * match response == expectedResponse