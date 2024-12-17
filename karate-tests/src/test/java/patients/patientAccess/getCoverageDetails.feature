Feature: Patient Access (Retrieve)
    Retrieve a chargeable snippet for a patient

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json patientCoverageResultEntry  = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageResultEntry.json')
    * json coverageBundle = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageBundle.json')
    
    * configure url = baseURL
  
@sandbox
   Scenario: Happy path - Retrieve patient coverage details
    * def p9number = '9733162868'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = p9number
    * method get
    * status 200
    * match response == coverageBundle
    * match response.entry[0].status == 'active'
    * match response.entry[0].beneficiary.identifier.value == p9number
    # * match response.entry[0].beneficiary.value == p9number

@sandbox
 Scenario: Happy path - patient has no coverage details
    * def P9WithNoCoverage = '9733162876'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: P9WithNoCoverage, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = P9WithNoCoverage
    * method get
    * status 200
    * match response.entry[0] == '#notpresent'

  # 9733162922 is displayed in retained record 9733162930
# Scenario: Retrieve patient current coverage details when superseded NHS number is sent
#     * def mergedP9number = '9733162922'
#     * def retainedRecord = '9733162930' 
#     * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: mergedP9number, scope: 'nhs-login'}).accessToken
#     * def requestHeaders = call read('classpath:auth/auth-headers.js')
#     * configure headers = requestHeaders
#     * path 'Coverage'
#     * param beneficiary:identifier = mergedP9number
#     * method get
#     * status 200
#     * match response == coverageBundle
#     * match response.entry[0].status == 'active'
#     * match response.entry[0].beneficiary.value !== mergedP9number 
#     * match response.entry[0].beneficiary.value == retainedRecord  

# Scenario: Retrieve patient coverage details where personalIdentification number is not available
#     * def personal_id_p9 = '9733162884'
#     * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: personal_id_p9, scope: 'nhs-login'}).accessToken
#     * def requestHeaders = call read('classpath:auth/auth-headers.js')
#     * configure headers = requestHeaders
#     * path 'Coverage'
#     * param beneficiary:identifier = personal_id_p9
#     * method get
#     * status 200
#     * match response == coverageBundle
#     * match response.entry[0].status == 'active'
#     * match response.entry[0].subscriberId == '#notpresent'


