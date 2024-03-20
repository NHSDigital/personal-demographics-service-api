Feature: Patch patient - Healthcare worker access mode

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
    * def nhsNumber = karate.get('nhsNumber', '9912002725')
    * path 'Patient', nhsNumber
    * method get
    * status 200
    
    * def patientObject = response
    * def etag = karate.response.header('etag')
    * def originalVersion = parseInt(response.meta.versionId)

  @gender
  Scenario: Change the gender of a patient
    * def genderOptions = ['male', 'female', 'unknown']
    * def targetGender = utils.pickDifferentOption(genderOptions, patientObject.gender)
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    * path 'Patient', nhsNumber
    * request
      """
      {
        "patches": [
          { "op": "replace", "path": "/gender", "value": "#(targetGender)" }
        ]
      }
      """
    * method patch
    * status 200
    * match response.gender == targetGender
    * match parseInt(response.meta.versionId) == originalVersion + 1