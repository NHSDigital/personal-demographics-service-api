Feature: Patient Access (Retrieve Coverage details)
    Retrieve a chargeable snippet for a patient

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json patientCoverageResultEntry  = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageResultEntry.json')
    * json coverageBundle = karate.readAsString('classpath:schemas/searchSchemas/patientCoverageBundle.json')
    
    * configure url = baseURL

  @sandbox
   Scenario: Happy path - Retrieve patient coverage details
    * def p9number = karate.env.includes('sandbox') ? '9000000009' : '9733162868'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(p9number)", expectedStatus: 200 }
    * match response == coverageBundle
    * match response.entry[0].resource.status == 'active'
    * match response.entry[0].resource.subscriber.identifier.value == p9number
    * match response.entry[0].resource.identifier[0].assigner contains { display: '#notnull'}

  @sandbox
  Scenario: Happy path - patient has no coverage details
    * def P9WithNoCoverage = karate.env.includes('sandbox') ? '9000000033' : '9733162876'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: P9WithNoCoverage, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(P9WithNoCoverage)", expectedStatus: 200 }
    * match response.entry[0] == '#notpresent'
    * match response.meta contains {versionId: '#notnull'}
    * match responseHeaders.Etag != null
   
    # 9732019735 is displayed in retained record 9732019638
  Scenario: Retrieve patient current coverage details when superseded NHS number is sent
    * def mergedP9number = '9732019735'
    * def retainedRecord = '9732019638' 
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: mergedP9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(mergedP9number)", expectedStatus: 200 }
    * match response == coverageBundle
    * match response.entry[0].resource.status == 'active'
    * match response.entry[0].resource.subscriber.identifier.value == retainedRecord
   
  Scenario: Retrieve patient coverage details where personal identification number is not available(Beneficiary is a mandatory field in FHIR)
    * def personal_id_p9 = '9733162884'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: personal_id_p9, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(personal_id_p9)", expectedStatus: 200 }
    * match response.entry[0] == '#notpresent'
    * match response.meta contains {versionId: '#notnull'}
    * match responseHeaders.Etag != null

  Scenario: Patient has no coverage details when Ehic details are hidden
    * def P9number = '9733162906'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: P9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * call read('classpath:patients/common/getCoverage.feature@getCoverageDetails'){ nhsNumber:"#(P9number)", expectedStatus: 200 }
    * match response.entry[0] == '#notpresent'