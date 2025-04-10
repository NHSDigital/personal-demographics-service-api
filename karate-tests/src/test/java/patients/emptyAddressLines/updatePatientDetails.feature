Feature: Update Patient's address with empty address lines
Background:
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL
Scenario: Healthcare worker can't add temporary address with empty address lines
    #Change NHS number
    * def nhsNumberForAddress = '9733162868'
    * path 'Patient', nhsNumberForAddress
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
    * path 'Patient', p9numberForAddress
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
   # Check validation to address in the response shows 5 lines
