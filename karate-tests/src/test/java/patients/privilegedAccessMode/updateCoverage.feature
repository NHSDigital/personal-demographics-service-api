@no-oas
Feature:  Update Coverage details - not permitted for privileged-application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
 
    * url baseURL
  Scenario: Fail to update a Coverage resource    
    * def nhsNumber = '9733162825'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalEtag = karate.response.header('etag')
    * def periodEndDate = utils.randomBirthDate()
    * header Content-Type = "application/json"
    * header If-Match = originalEtag 
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
    * retry until responseStatus != 503 && responseStatus != 502  
    * method post
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = "Cannot POST resource with privileged-application-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse