Feature: Updating Patient's details - empty address lines
Background:
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL
Scenario: Updating temporary address response should show empty address lines
    #Change NHS number
    * def nhsNumber = '9733162868'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def utils = call read('classpath:helpers/utils.feature')
    * def randomAddress = utils.randomTempAddress()
    * def tempAddress = randomAddress
    # add temp address

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * path 'Patient', nhsNumber
    * def requestBody = 
    """
      {
        "patches":
        [
            {
                "op": "add",
                "path": "/address/-",
                "value": "#(tempAddress)"
            }
        ]
    }
    """
    * request requestBody
    * method patch
    * status 200 
    * def idAfterTempAddress = response.meta.versionId
   # Check validation to address in the response shows 5 lines

   # Test fails if the patient's temp address details are not present in the record
  
   * if (tempAddressDetails == null) {karate.fail('No value found for temporary address, stopping the test.')}
   * def addressIndex = response.address.findIndex(x => x.use == "temp")
   * def tempAddressPath =  "/address/" + addressIndex
   
    # remove temp address details

   * configure headers = call read('classpath:auth/auth-headers.js') 
   * header Content-Type = "application/json-patch+json"
   * header If-Match = karate.response.header('etag')
   * path 'Patient',p9numberForAddress
   * request 
   """
     {
       "patches": [
         {
           "op": "test",
           "path": "#(tempAddressPath)",
           "value": "#(tempAddressDetails)"     
         },
         {
          "op": "remove",
           "path": "#(tempAddressPath)" 
         }
       ]
     }
     """ 
   * method patch
   * status 200
   * match parseInt(response.meta.versionId) == parseInt(idAfterTempAddress)+ 1
  # Check validation to address in the response shows 5 lines

Scenario: Updating contact details response should show empty address lines
    * def nhsNumber = '9733162868'
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def originalEtag = karate.response.header('etag')
    * def originalTelecom = response.telecom

     # "replace" will update the telecom object we identify
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = originalEtag
    * def mobileIndex = utils.getIndexOfFirstMobile(originalTelecom)
    * def newTelecom = { "id": "#(originalTelecom[mobileIndex].id)", "period": { "start": "#(utils.todaysDate())" }, "system": "phone", "use": "mobile", "value": "#(faker.phoneNumber())" }
    * request { "patches": [{ "op": "replace", "path": "#('/telecom/' + mobileIndex)", "value": "#(newTelecom)" }]}
    * path 'Patient', nhsNumber
    * method patch
    * status 200
    * assert originalTelecom.length == response.telecom.length
    # Check validation to address in the response shows 5 lines
