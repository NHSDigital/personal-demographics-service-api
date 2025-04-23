@no-oas
Feature: Search for a patient(Healthcare worker access)- Empty address lines

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

Scenario:Search for a patient using parameters
    * path "Patient"
    * params  { family: "Jones", gender: "male", birthdate: "ge1992-01-01", _max-results: "6" }
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.entry[0].resource.id == "5900035697"
    * def addresses = response.entry[0].resource.address
    * match utils.checkNullsHaveExtensions(addresses) == true
