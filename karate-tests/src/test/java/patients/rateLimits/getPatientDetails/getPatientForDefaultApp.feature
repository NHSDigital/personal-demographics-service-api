
Feature: Get a patient - Healthcare worker access mode

Background:
 
  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature', { clientID: karate.get('proxyRateLimitingAppClientID'),clientSecret: karate.get('proxyRateLimitingAppClientSecret')}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * url baseURL

Scenario: Get patient details
  * def nhsNumber = '9727022820'
  * path 'Patient', nhsNumber
  * method get
  * def is429 = responseStatus == 429
  * karate.set('is429', is429)
  * print '>>>>>>>>>>>>>>>>>>>>>>>>>>> Status:', responseStatus
  