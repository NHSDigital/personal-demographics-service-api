Feature: Patient Access (Retrieve)
    Retrieve a chargeable snippet error scenarios

Background:
    * def utils = call read('classpath:helpers/utils.feature')

    * configure url = baseURL
    * def p9number = '9733162884'

Scenario Outline: Patient can't retrieve coverage details when <patientType> 
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = nhsNumber
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

    Examples:
      | patientType     | nhsNumber   |
      | P9.Cp           | 5900068196  |

Scenario Outline: Auth errors: patient coverage details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * requestHeaders.authorization = headerValue
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = p9number
    * method get
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

Scenario Outline: x-request-id errors: patient coverage details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * requestHeaders['x-request-id'] = headerValue
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = p9number
    * method get
    * status 400
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders) 
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/${errorResponse}.json`)
    * match response == expectedResponse
    
    Examples:
       | headerValue                | diagnostics                                                                                 | errorResponse   |     
       |                            | Invalid request with error - X-Request-ID header must be supplied to access this resource   | MISSING_VALUE   |
       | 1234                       | Invalid value - '1234' in header 'X-Request-ID'                                             | INVALID_VALUE   |
                
Scenario: Identifier doesn't match nhs number of user
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * param beneficiary:identifier = "9999999990"
    * method get
    * status 403
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

Scenario: No search params provided
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * method get
    * status 400
    * def diagnostics = "Invalid search data provided - 'Coverage search request must follow the format /Coverage?beneficiary:identifier=NHS_NUMBER'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')

Scenario: Additional invalid param
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Coverage'
    * params { beneficiary:identifier = "9999999990", year: "2003" }
    * method get
    * status 400
    * def diagnostics = "Invalid search data provided - 'Coverage search request must follow the format /Coverage?beneficiary:identifier=NHS_NUMBER'"
    * match response == read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')
    