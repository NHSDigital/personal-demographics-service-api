@sandbox
Feature: Patch patient - add errors

Covers error scenarios that can arise when trying to add data to a patient resource.

Background:
    * def utils = call read('classpath:helpers/utils.feature')    
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * url baseURL

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * def nhsNumber = '5900059332'
    * path 'Patient', nhsNumber
    * method get
    * status 200 

Scenario: Forbidden update example - multiple usual names cannot be added
    * match response.name == '#[1]'

    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')

    * def diagnostics = "Forbidden update with error - multiple usual names cannot be added"
    * def expectedResponse = read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')

    * def newName = 
    """
    {
      "use": "usual",
      "period": {"start": "2019-12-31"},
      "prefix": ["Dr"],
      "given": ["Joe", "Horation", "Maximus"],
      "family": "Bloggs",
      "suffix": ["PhD"],
    }
    """
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
    * method patch
    * status 403
    * match response == expectedResponse