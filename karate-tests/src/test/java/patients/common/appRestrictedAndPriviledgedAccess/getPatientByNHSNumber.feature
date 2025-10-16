@inore
Feature:Get a patient By NHS number

  Background:
    # schemas and validators that are required by the schema checks
    * def utils = call read('classpath:helpers/utils.feature')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
    * json OtherContactSystem = karate.readAsString('classpath:schemas/extensions/OtherContactSystem.json')
    * json ContactRelationship = karate.readAsString('classpath:schemas/codeable/ContactRelationship.json')
    * json Contact = karate.readAsString('classpath:schemas/Contact.json')
    * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json ManagingOrganizationReference = karate.readAsString('classpath:schemas/ManagingOrganizationReference.json')
    * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')

    * url baseURL

  @getPatient
  Scenario: Get a patients details
    * configure headers = requestHeaders  
    * def nhsNumber = '9733162825'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.id == nhsNumber 

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