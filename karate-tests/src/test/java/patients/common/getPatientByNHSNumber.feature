@ignore
Feature:Get a patient By NHS number

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * url baseURL

  @invalidResource  
  Scenario: Retrieve a patient with an invalid NHS number format should return 'invalid resource'
    * def nhsNumber = '9000000000'
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALID_RESOURCE_ID.json')
    * path 'Patient', nhsNumber
    * method get
    * status 400
    * match response == expectedBody

  @resourceNotFound
  Scenario: Retrieve a patient with non-existent records should return 'RESOURCE_NOT_FOUND'
    * def nhsNumber = '9727194737'
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')
    * path 'Patient', nhsNumber
    * method get
    * status 404
    * match response == expectedBody

  @invalidatedResource 
  Scenario: Retrieve a patient with invalidated records should return 'INVALIDATED_RESOURCE'
    * def nhsNumber = '9990003343'
    * def expectedBody = read('classpath:mocks/stubs/errorResponses/INVALIDATED_RESOURCE.json')
    * path 'Patient', nhsNumber
    * method get
    * status 404
    * match response == expectedBody