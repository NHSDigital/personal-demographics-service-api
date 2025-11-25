@no-oas
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
   * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(p9number)", expectedStatus: 200 }
   * def addresses = response.address
   * match utils.checkNullsHaveExtensions(addresses) == true
