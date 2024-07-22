@sandbox
Feature: Get related person details (Healthcare worker access)

Background:
  # schemas and validators that are required by the schema checks
  * def utils = call read('classpath:helpers/utils.feature')

  * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
  * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
  * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json RelatedPersonSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchResultEntry.json')
  * json RelatedPersonSearchBundle = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchBundle.json')

  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

Scenario: Patient has one related person
  * def nhsNumber = karate.env == 'mock' ? '9000000017' : '9693633679'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == RelatedPersonSearchBundle
  * match response.total == 1

@smoke-only
Scenario: Patient has one related person (INT smoke test)
  * def nhsNumber = '9693633679'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == RelatedPersonSearchBundle
  * match response.total == 1


@sandbox-only
Scenario: Patient has more than one related person
  * def nhsNumber = '9000000009'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == RelatedPersonSearchBundle
  * match response.total == 2

Scenario: Patient doesn't have a related person
  * def nhsNumber = karate.env == 'mock' ? '9000000025' : '9693632109'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response == 
    """
    {
      "resourceType": "Bundle",
      "type": "searchset",
      "timestamp": "#? utils.isValidTimestamp(_)",
      "total": 0
    }
    """
