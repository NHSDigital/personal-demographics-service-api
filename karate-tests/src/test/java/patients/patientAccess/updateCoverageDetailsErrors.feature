
@no-oas
Feature: Patient Access (Update Coverage details) - error scenarios

  Background:
    * def utils = call read('classpath:helpers/utils.feature') 
    * configure url = baseURL
  
   Scenario Outline: Patient can't retrieve coverage details when <patientType> 
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = 'W/"4"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

    Examples:
      | patientType     | nhsNumber   |
      | P9.Cp           | 5900068196  |
      | P5              | 9912003072  |
      | P9.Cp           | 5900068196  |
  
  Scenario Outline: Auth errors: update patient coverage details
    * def nhsNumber = '9733162868'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * requestHeaders.authorization = headerValue
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = 'W/"4"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 401
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def display = 'Access Denied - Unauthorised'
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse
      
      Examples:
           | headerValue                | diagnostics                    | 
           |                            | Missing Authorization header   |      
           | Bearer                     | Missing access token           |
           | Bearer abcdef123456789     | Invalid Access Token           |  
  
  @sandbox
  Scenario Outline: x-request-id errors: update patient coverage details
    * def nhsNumber = '9733162868'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * requestHeaders['x-request-id'] = headerValue
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = 'W/"4"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 400
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/${errorResponse}.json`)
    * match response == expectedResponse
    
    Examples:
        | headerValue                | diagnostics                                                                                 | errorResponse   |     
        |                            | Invalid request with error - X-Request-ID header must be supplied to access this resource   | MISSING_VALUE   |
        | 1234                       | Invalid value - '1234' in header 'X-Request-ID'                                             | INVALID_VALUE   |         

  @ignore       
  Scenario: Login nhs number doesn't match nhs number in the body
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = 'W/"4"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * def nhsNumber = '9732019913'
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 400
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
   
  @sandbox
  Scenario: Incorrect resource version to update coverage 
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * def incorrectResourceVersion = originalVersion + 1
    * header If-Match = 'W/"' + incorrectResourceVersion + '"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 409
    * match response == read('classpath:mocks/stubs/errorResponses/RESOURCE_VERSION_MISMATCH.json') 
  
  @sandbox   
  Scenario: Missing If-Match header to update coverage 
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 412
    * def diagnostics = "Invalid request with error - If-Match header must be supplied to update this resource"
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')
    * match response == expectedBody  

  @sandbox
  Scenario: Missing personal id number in the request body
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request-missing-subscriber.json')
    * method post
    * status 400
    * def diagnostics = `Missing value - 'subscriberId'`
    * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')   

  @sandbox  
  Scenario: Missing Identification number of the institution in the request body
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request-missing-cardnumber.json')
    * method post
    * status 400
    * def diagnostics = `Missing value - 'identifier/0/value'`
    * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')    

  @sandbox
  Scenario: Invalid period in the request body
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = '2026-13-15'
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 400
    * def diagnostics = `Invalid value - '2026-13-15' in field 'period/end'`
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  
  Scenario: Send empty field in the request body
    * def nhsNumber = '9733162892'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-reques-empty-value-institution-id.json')
    * method post
    * status 400
    * def diagnostics = `Invalid value - '' in field 'payor/0/identifier/value'`
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')  

  Scenario:  Patient that don't have corresponding patient objects
    * def p9WithoutPatientObject = '9462978182'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9WithoutPatientObject, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = 'W/"4"'
    * def periodEndDate = utils.randomDateWithInYears(4)
    * def nhsNumber = p9WithoutPatientObject
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 404
    * match response == read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')   

  Scenario: Send an update for superseded NHS number(authenticate and send update with superseded NHS number)
    * def mergedP9number = '9732019735'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: mergedP9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = mergedP9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    * def nhsNumber = mergedP9number
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 403
    * def diagnostics = `Forbidden update with error - Update Failed - NHS No. supplied has been superseded in a merge`
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')

  @ignore 
  Scenario: Send an update for retained NHS number by authenticating with superseded NHS number
    * def mergedP9number = '9732019735'
    * def retainedRecord = '9732019638'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: mergedP9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = mergedP9number
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * header Content-Type = "application/json"
    * header If-Match = originalEtag
    # sending updates with retained record
    * def nhsNumber = retainedRecord
    * def periodEndDate = utils.randomDateWithInYears(4)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 403
    * def diagnostics = `Forbidden update with error - Update Failed - NHS No. supplied has been superseded in a merge`
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')  