Feature: Patient Access (Retrieve)
    Retrieve a chargeable snippet for a patient

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json coverageCountryExtension = karate.readAsString('classpath:schemas/extensions/CoverageCountry.json')
    * json coverageResultSet = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageResultsEntry.json')
  
    * configure url = baseURL
    * def p9number = '9733162868'
   Scenario: Happy path - Retrieve patient coverage details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = p9number
    * method get
    * status 200
    * match response == read('classpath:schemas/searchSchemas/patientCoverageBundle.json')

# Scenario: Happy path - patient has no coverage details
#     * def P9WithNoCoverage = '9733162873'
#     * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: P9WithNoCoverage, scope: 'nhs-login'}).accessToken
#     * def requestHeaders = call read('classpath:auth/auth-headers.js')
#     * configure headers = requestHeaders
#     * path 'Coverage'
#     * param beneficiary:identifier = P9WithNoCoverage
#     * method get
#     * status 404
