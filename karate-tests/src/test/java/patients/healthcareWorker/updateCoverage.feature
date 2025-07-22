
Feature: Update Coverage-not permitted for healthcare worker

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL
    # Adding re-try when "sync-wrap failed to connect to spine"
    * configure retry = { count: 2, interval: 6000 }
    * retry until responseStatus != 503

  Scenario: Fail to update a Coverage resource
    * def nhsNumber = '9733163031'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * header If-Match = karate.response.header('etag')
    * header Content-Type = "application/json"
    * def periodEndDate = utils.randomDateWithInYears(2)
    * path "Coverage"
    * request read('classpath:patients/patientAccess/updateCoverageRequests/update-patient-coverage-request.json')
    * method post
    * status 403
    * def display = "Cannot POST resource with user-restricted access token"
    * def diagnostics = "Your app has insufficient permissions to use this operation. Please contact support."
    * def expectedResponse = read(`classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json`)
    * match response == expectedResponse