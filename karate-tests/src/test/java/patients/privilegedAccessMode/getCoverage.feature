Feature: Get Coverage-not permitted for privileged-application-restricted users

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')

    * url baseURL

  Scenario: Fail to retrieve a Coverage resource
    * configure headers = requestHeaders 
    * path "Coverage"
    * param "subscriber:identifier" = "9999999999"
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = "Cannot GET resource with privileged-application-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse