    @no-oas
Feature: Get related person details - privileged-application-restricted access mode

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 

    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
    * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
    * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json RelatedPersonSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchResultEntry.json')
    * json RelatedPersonSearchBundle = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchBundle.json')
    * url baseURL

  Scenario: Patient has one related person - privileged-application-restricted access mode
    * call read('classpath:patients/common/getPatientsRelatedPerson.feature@patientWithOneRelatedPerson') 

  Scenario: Patient doesn't have a related person- privileged-application-restricted access mode
    * call read('classpath:patients/common/getPatientsRelatedPerson.feature@patientWithNoRelatedPerson')
  Scenario: Related people are not returned for a restricted/sensitive patient and an empty bundle is returned
    * def nhsNumber = '9733162507'
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
    @ignore
    # The related sensitive patient record is currently displaying address and telecom details
    # which should not be visible. An incident has been raised to address this issue. The ignore tag will be removed once the fix has been applied   
  Scenario: Patient has sensitive related person - response should not include address or telecom details with privileged access
    * def nhsNumber = '9733162426'
    * path 'Patient', nhsNumber, 'RelatedPerson'
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response == RelatedPersonSearchBundle
    * match response.entry[0].resource.address == '#notpresent'
    * match response.entry[0].resource.telecom == '#notpresent'   