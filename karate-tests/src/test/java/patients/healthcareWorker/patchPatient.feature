@sandbox
Feature: Patch patient - Healthcare worker access mode

  # These tests are only run against the sandbox at the moment - until we have a better 
  # way of managing test data in the integration environment
  
  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    
    * url baseURL
    * def nhsNumber = karate.get('nhsNumber', '9000000009')
    * path 'Patient', nhsNumber
    * method get
    * status 200
    
    * def patientObject = response
    * def etag = karate.response.header('etag')
    * def originalVersion = parseInt(response.meta.versionId)
    
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    
  Scenario: Add new name to patient
    * match response.name == '#[1]'

    * def newName = 
    """
    {
      "use": "usual",
      "period": {"start": "2019-12-31"},
      "prefix": "Dr",
      "given": ["Joe", "Horation", "Maximus"],
      "family": "Bloggs",
      "suffix": "PhD",
    }
    """
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "add", "path": "/name/-", "value": "#(newName)" }]}
    * method patch
    * status 200
    * match response.name == '#[2]'
    * match response.name[1] == newName
    * match parseInt(response.meta.versionId) == originalVersion + 1

  Scenario: Replace given name of a patient
    * def newName = "Anne"

    * def existingName = response.name[0].given[0]
    * match existingName != newName
    
    * path 'Patient', nhsNumber
    * request {"patches":[{"op":"replace","path":"/name/0/given/0","value":"#(newName)"}]}
    * method patch
    * status 200
    * match response.name[0].given[0] == newName
    * match parseInt(response.meta.versionId) == originalVersion + 1

  Scenario: Remove suffix from patient
    * def existingSuffix = response.name[0].suffix
    * match existingSuffix != null

    * path 'Patient', nhsNumber
    # we even add a patch that should be ignored here for some reason
    * request {"patches":[{"op":"test","path":"/name/0/id","value":"123"},{"op":"remove","path":"/name/0/suffix/0"}]}
    * method patch
    * status 200
    * match response.name[0].suffix == '#[0]'
    * match parseInt(response.meta.versionId) == originalVersion + 1

  Scenario: Change the gender of a patient
    * def genderOptions = ['male', 'female', 'unknown']
    * def targetGender = utils.pickDifferentOption(genderOptions, patientObject.gender)
    
    * path 'Patient', nhsNumber
    * request {"patches": [{ "op": "replace", "path": "/gender", "value": "#(targetGender)" }]}
    * method patch
    * status 200
    * match response.gender == targetGender
    * match parseInt(response.meta.versionId) == originalVersion + 1

  