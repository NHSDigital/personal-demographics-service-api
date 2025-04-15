Feature: Get a patient(patient access)- Empty address lines

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    # auth
    * url baseURL
    * def p9number = '9733162930'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret'),userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders   
Scenario: Get a patient details
    * path 'Patient', p9number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true
