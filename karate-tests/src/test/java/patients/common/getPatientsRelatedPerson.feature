@ignore
Feature: Get related person details

  Background:

    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
    * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
    * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json RelatedPersonSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchResultEntry.json')
    * json RelatedPersonSearchBundle = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchBundle.json')
    * url baseURL

  @patientWithOneRelatedPerson  
  Scenario: Patient has one related person
    * def nhsNumber = '9693633679'
    * path 'Patient', nhsNumber, 'RelatedPerson'
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response == RelatedPersonSearchBundle
    * match response.total == 1

  @patientWithNoRelatedPerson    
  Scenario: Patient doesn't have a related person
    * def nhsNumber = '9693632109'
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