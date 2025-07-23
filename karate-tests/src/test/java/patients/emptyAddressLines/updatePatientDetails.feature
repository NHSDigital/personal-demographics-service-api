@no-oas
Feature: Updating Patient's details(Healthcare worker access) - empty address lines
Background:
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
    * def utils = call read('classpath:helpers/utils.feature')
    * def faker = Java.type('helpers.FakerWrapper')
    
Scenario: Updating temporary address response should show empty address lines
    * def nhsNumber = '9733162256'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalEtag = karate.response.header('etag')
    * def originalVersion = response.meta.versionId 
    * def randomAddress = utils.randomTempAddress()
    * def address = randomAddress
    * def tempAddressDetails = utils.removeNullsFromAddress(response.address.find(x => x.use == "temp"))
    * if (tempAddressDetails == null) {karate.fail('No value found for temporary address, stopping the test.')}
    * def tempAddressIndex = response.address.findIndex(x => x.use == "temp")
    * def path =  "/address/" + tempAddressIndex
    * def testOpValue = tempAddressDetails
  
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * path 'Patient', nhsNumber
    * request read('classpath:patients/requestDetails/add/addressUpdate.json')
    # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
    * configure retry = { count: 2, interval: 5000 }
    * retry until responseStatus != 503 && responseStatus != 502  
    * method patch
    * status 200 
    * match parseInt(response.meta.versionId) == parseInt(originalVersion)+ 1
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true

 
Scenario: Updating contact details response should show empty address lines
    * def nhsNumber = '9733162264'
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalEtag = karate.response.header('etag')
    * def originalTelecom = response.telecom

     # "replace" will update the telecom object we identify
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * def mobileIndex = utils.getIndexOfFirstMobile(originalTelecom)
    * def newTelecom = { "id": "#(originalTelecom[mobileIndex].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }
    * request { "patches": [{ "op": "replace", "path": "#('/telecom/' + mobileIndex)", "value": "#(newTelecom)" }]}
    # Added retry logic to handle "sync-wrap failed to connect to Spine" errors
    * configure retry = { count: 2, interval: 5000 }
    * retry until responseStatus != 503 && responseStatus != 502  
    * path 'Patient', nhsNumber
    * method patch
    * status 200
    * assert originalTelecom.length == response.telecom.length
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true
