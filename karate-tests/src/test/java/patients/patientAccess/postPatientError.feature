Feature: Create patient (allocate NHS number)

Background:
  # authenticate as a P9 user (a patient)
  * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature', {userId: '9472063845'}).accessToken
  * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
  * configure headers = requestHeaders
  * url baseURL

Scenario: A patient cannot allocate an NHS number
  * path "Patient"
  * request { bananas: "in pyjamas" }
  * configure retry = { count: 5, interval: 10000 }
  * retry until responseStatus != 429 && responseStatus != 503
  * method post
  * status 403
  * def diagnostics = "Your app has insufficient permissions to use this method. Please contact support."
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')