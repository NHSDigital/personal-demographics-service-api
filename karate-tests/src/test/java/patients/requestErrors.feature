Feature: Handle request errors

Background:
  # schemas and validators that are required by the schema checks
  * def utils = call read('classpath:helpers/utils.feature')

  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

Scenario: Make request to endpoint that is not supported
  * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9693632109'
  * path 'HelloWorld'
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.issue[0].diagnostics == "Unsupported path - '/HelloWorld'"

Scenario: Make request to invalid endpoint that is similar to valid endpoint
  * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9693632109'
  * path 'Patient!'
  * method get
  * status 400
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.issue[0].diagnostics == "Unsupported path - '/Patient!'"
