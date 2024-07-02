Feature: Get related person details (Patient access)

Background:
  # schemas and validators that are required by the schema checks
  * def utils = call read('classpath:helpers/utils.feature')

  * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
  * json RelatedPersonSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchResultEntry.json')
  * json RelatedPersonSearchBundle = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchBundle.json')

  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature', {userID: '9472063845', scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

Scenario: Patient can do related person search for their own record
  * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9472063845'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == RelatedPersonSearchBundle
