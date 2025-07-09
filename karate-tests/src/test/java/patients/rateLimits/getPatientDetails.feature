Feature: Get a patient - Healthcare worker access mode
 # By default, the test application uses the proxy rate limits. These rate limits vary across the internal-dev, int, and ref environments.
 # As a precondition, the appropriate proxy must be assigned to the test application based on the specific testing requirements.
 
Background:
 
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature', { clientID: karate.get(requestingApp + 'ClientID'), clientSecret: karate.get(requestingApp + 'ClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

@rateLimit
Scenario: Get patient details
  * def nhsNumber = '9727022820'
  * path 'Patient', nhsNumber
  * method get
  * def is429 = result.responseStatus == 429
  * karate.set('is429', is429)
  * if (is429) karate.set('timestamp429', java.time.ZonedDateTime.now(java.time.ZoneOffset.UTC).toString())