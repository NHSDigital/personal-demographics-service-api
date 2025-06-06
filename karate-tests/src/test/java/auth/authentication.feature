@ignore
Feature: Authentication for Healthcare Worker
    
  Reusable feature for authentication. When calling this feature,
  you can optionally pass in a userID value to authenticate as a specific
  test user. Otherwise, we default to shirley.bryne@nhs.net (656005750107)

  For reference some valid cis2 mock usernames are:
    - 656005750104 	surekha.kommareddy@nhs.net (requires a role to be specified using the NHSD-Session-URID header)
    - 656005750105 	darren.mcdrew@nhs.net
    - 656005750106 	riley.jones@nhs.net
    - 656005750107 	shirley.bryne@nhs.net

Background:
    * def userID = karate.get('userID', '656005750107')
    * def scope = karate.get('scope', null)
    * def javaUtils = Java.type('helpers.Utils')
    * def utils = call read('classpath:helpers/utils.feature')
    * def clientID = karate.get('clientID')
    * def clientSecret = karate.get('clientSecret')

@mock
Scenario: Mock authentication
    # We don't authenticate on sandbox. We set a example value that follows bearer token format
    * def accessToken = "g1112R_ccQ1Ebbb4gtHBP1aaaNM"
    # gitleaks:allow

@real
Scenario: Call the real oauth2 authentication mock service
    
    # 1. Call the "authorize" endpoint
    # for the sake of supporting the NHS login flow (where scope='nhs-login'),
    # we need to avoid following the redirects, since the redirect URL isn't fully valid
    # and Karate won't follow it automatically.
    * configure followRedirects = false

    * url oauth2MockURL
    * path 'authorize'
    * param response_type = 'code'
    * param client_id = clientID
    * param state = utils.randomUUID()
    * param redirect_uri = 'https://example.org/callback'
    * param scope = scope
    * method get
    * status 302
    
    * def redirectURL = responseHeaders['Location'][0]
    * url redirectURL.replace(' ', '%20')
    * method get
    * status 200
    
    # 2. This gives us a login form - get the URL this form calls when submitted
    * def action = javaUtils.getLoginFormAction(response)

    # 3. Submit the form. We don't follow redirects or we end up with a 404.
    # We go step by step until we get the resource we need.
    * configure followRedirects = false
    * url action 
    * form field username = userID
    * form field login = 'Sign In'
    * method post
    
    # This redirects us to the identity-service
    * status 302
    
    # Then we get redirected to what we set as our callback URL
    * url responseHeaders['Location'][0]
    * method get
    * status 302
    * def secondRedirectLocation = responseHeaders['Location'][0]
    
    # Then we get the code
    * def parseCode = 
        """
        function(locationURL) {
          var regexp = /.*code=(.*)&/g;
          var matches = regexp.exec(locationURL);
          return matches[1];
        }
        """
    * def authorizationCode = call parseCode secondRedirectLocation
    
    # We use this code to call the 'token' endpoint and get our access token
    * url oauth2MockURL
    * path 'token'
    * form field grant_type = 'authorization_code'
    * form field code = authorizationCode
    * form field redirect_uri = 'https://example.org/callback'
    * form field client_id = clientID
    * form field client_secret = clientSecret
    * method post
    * status 200

    * def accessToken = response.access_token
  