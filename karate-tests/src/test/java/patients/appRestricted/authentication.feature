@ignore
Feature: Authentication for application-restricted access - signed JWT authentication
   For application-restricted access, we used a signed JWT token to make a request for 
   our bearer token.

Background:
    * def javaUtils = Java.type('helpers.Utils')
    * def utils = call read('classpath:helpers/utils.feature')
    * def randomUUID = function(){ return java.util.UUID.randomUUID() + '' }
    * url oauth2MockURL

@mock
Scenario: Mock authentication
    # We don't authenticate. We set a value that isn't a UUID, that the mock accepts
    * def accessToken = "g1112R_ccQ1Ebbb4gtHBP1aaaNM"

@real
Scenario: Authentication for application-restricted access - signed JWT authentication
    # note that the apiKey will be different if we're using our own apps...
    * def tokenParams = 
        """
        {
            signingKey: "#(signingKey)",
            apiKey: "#(apiKey)",
            keyID: "#(keyID)",
            authURL: "#(oauth2MockURL + '/token')"
        }
        """
    * def jwt = javaUtils.generateJWT(tokenParams)
    * path 'token'
    * form field grant_type = "client_credentials"
    * form field client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    * form field client_assertion = jwt
    * method post
    * status 200
    * match response ==
        """
        {
            "access_token": "#string",
            "expires_in": "#regex[0-9]+",
            "token_type": "Bearer",
            "issued_at": "#string"
        }
        """
    * def accessToken = response.access_token