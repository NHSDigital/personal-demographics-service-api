@wip
Feature: Patient lifecycle

Background:
    * def auth = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature')
    * def accessToken = auth.response.access_token
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

Scenario: post, get, patch a patient
    * def post = call read('classpath:patients/healthcareWorker/postPatient.feature')
    * def nhsNumber = post.response.id
    * def get = call read('classpath:patients/healthcareWorker/getPatient.feature@get') {nhsNumber: '#(nhsNumber)'}
    * def patch = call read('classpath:patients/healthcareWorker/patchPatient.feature@gender') {nhsNumber: '#(nhsNumber)'}