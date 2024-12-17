Feature: Get Coverage

  Background:
    * def utils = karate.callSingle('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:patients/appRestricted/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/appRestricted/app-restricted-headers.js')

    * url baseURL

  Scenario: Fail to retrieve a Coverage resource
    * configure headers = requestHeaders 
    * path "Coverage"
    * param "beneficiary:identifier" = "9999999999"
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.issue[0].details.coding[0].display == "Cannot GET resource with application-restricted access token"
    * match response.issue[0].details.coding[0].code == "ACCESS_DENIED"
    * match response.issue[0].diagnostics == "Your app has insufficient permissions to use this operation. Please contact support."