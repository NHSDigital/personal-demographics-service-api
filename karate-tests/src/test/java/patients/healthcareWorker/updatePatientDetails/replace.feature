@sandbox
Feature: Patch patient - Replace data

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * url baseURL

  Scenario: Replace attribute of an object
    # To replace the attribute of an object, you need to provide the id of the object you want to replace
    # in a preceding operation. (This is simlar to, but different from removing an object - we call 
    # "replace" instead of "test")
    * def nhsNumber = karate.env == 'mock' ? '9000000009' : '5900056597'
    * configure headers = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js') 
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)
    * def givenName = response.name[0].given[0]

    * def options = ["Anne", "Mary", "Jane"]
    * def newGivenName = utils.pickDifferentOption(options, givenName)

    * configure headers = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request 
      """
      {"patches":[
        {"op":"replace","path":"/name/0/id","value":"#(response.name[0].id)"}
        {"op":"replace","path":"/name/0/given/0","value":"#(newGivenName)"}
      ]}
      """
    * method patch
    * status 200
    * match response.name[0].given[0] == newGivenName
    * match parseInt(response.meta.versionId) == originalVersion + 1

  Scenario Outline: Replace the <property> property
    # Unlike replacing a property that is an object, there's no need to make a 
    # preceding test operation
    * configure headers = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js') 
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)

    * def currentValue = response[property]
    * def targetValue = utils.pickDifferentOption(options, currentValue)

    * configure headers = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "replace", "path": "#('/' + property)", "value": "#(targetValue)" }]}
    * method patch
    * status 200
    * def newValue = response[property]
    * match newValue == targetValue
    * match parseInt(response.meta.versionId) == originalVersion + 1

    Examples:
      | nhsNumber     | property      | options!                             |  
      | 5900059243    | gender        | ['male', 'female', 'unknown']        |
      | 5900043320    | birthDate     | ["1985-10-26", "1955-11-05"]         |