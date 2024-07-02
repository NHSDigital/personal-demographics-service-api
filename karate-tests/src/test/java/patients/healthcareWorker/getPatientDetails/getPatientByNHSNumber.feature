@sandbox
Feature: Get a patient - Healthcare worker access mode

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
  * json Patient = karate.readAsString('classpath:schemas/Patient.json')

  # auth
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

@unrestricted @smoke
Scenario: Get an "unrestricted" patient
  * def nhsNumber = karate.env == 'mock' ? '9000000009' : '9693632109'
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.id == nhsNumber
  * match response == Patient
  * match response.meta.security[0] ==
    """
    {
      "code": "U",
      "display": "unrestricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """

@sensitive
Scenario: Get a "restricted" (sensitive) patient
  * def nhsNumber = karate.env == 'mock' ? '9000000025' : '9727022820'
  * path 'Patient', nhsNumber
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * match response.id == nhsNumber
  * match response == Patient
  * match response.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """
