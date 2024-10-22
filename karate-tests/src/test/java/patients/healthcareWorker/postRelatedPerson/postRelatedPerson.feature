Feature: Post patient related person - Healthcare worker access mode

Background:
    * def utils = call read('classpath:helpers/utils.feature')    
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * url baseURL

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * def nhsNumber = '5900069176'

Scenario: Post forbidden - not allowed for healthcareWorker
    * configure headers = call read('classpath:auth/auth-headers.js') 

    * def display = "Cannot create resource with user-restricted access token"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')

    * path 'Patient', nhsNumber, 'RelatedPersons'
    * request {}
    * method post
    * status 403
    * match response == expectedResponse