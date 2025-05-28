@no-oas 
Feature: Search for a patient(Healthcare worker access)- confidential reasons for removal

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * url baseURL

Scenario:Search for a patient using parameters response should not include reason for removal details
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('confidentialRemovalReasonsClientID'), clientSecret:karate.get('confidentialRemovalReasonsClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * path "Patient"
    * params  { family: "KELLET", gender: "female", birthdate: "1972-06-01" }
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.entry[0].resource.id == "9733163023"
    * match response.entry[0].resource.extension == '#notpresent'

Scenario:Search for a patient using parameters response should not include reason for removal details for default test app
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * path "Patient"
    * params  { family: "COLE", gender: "female", birthdate: "1964-08-28" }
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.entry[0].resource.id == "9733163074"
    * match response.entry[0].resource.extension[0].url == "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus" 
    * match response.entry[0].resource.extension[1] == '#notpresent'    