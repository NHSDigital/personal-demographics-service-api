@no-oas
Feature: Patient cannot allocate an NHS number

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')      
    * url baseURL

Scenario: A patient cannot allocate an NHS number
    * def p9number = '9912003071'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def givenName = ["#(faker.givenName())", "#(faker.givenName())"]
    * def familyName = "ToRemove"
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
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Cannot create resource with patient-access access token'
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
