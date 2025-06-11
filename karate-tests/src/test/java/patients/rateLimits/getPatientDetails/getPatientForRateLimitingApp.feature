
Feature: Get a patient - Healthcare worker access mode
 # The RateLimiting test application uses the ratelimiting custom attribute, which overrides the default proxy rate limits.
 # As a precondition, the ratelimiting custom attribute must be configured appropriately, and the correct proxy must be assigned to the RateLimiting test application based on the specific testing requirements.
Background:
 
  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature', { clientID: karate.get('rateLimitingAppClientID'),clientSecret: karate.get('rateLimitingAppClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

Scenario: Get patient details
  * def nhsNumber = '9693632109'
  * path 'Patient', nhsNumber
  * method get
  * def is429 = responseStatus == 429
  * karate.set('is429', is429)
  * if (is429) karate.set('timestamp429', java.time.ZonedDateTime.now(java.time.ZoneOffset.UTC).toString())