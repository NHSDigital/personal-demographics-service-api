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
  * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
  * json Patient = karate.readAsString('classpath:schemas/Patient.json')

  # auth
  * def aal2_user_ID = '656005750109'
  * def intNhsNumber = '9693632109'
  * def sandboxNhsNumber = '9000000009'

  * url baseURL

@unrestricted @smoke
Scenario: Get an "unrestricted" patient
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * def nhsNumber = karate.env.includes('sandbox') ? sandboxNhsNumber : intNhsNumber
  * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
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
  * def addresses = response.address
  * match utils.checkNullsHaveExtensions(addresses) == false

@sensitive
Scenario: Get a "restricted" (sensitive) patient
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * def nhsNumber = karate.env.includes('sandbox') ? '9000000025' : '9727022820'
  * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
  * match response.id == nhsNumber
  * match response == Patient
  * match response.address == '#notpresent'
  * match response.generalPractitioner == '#notpresent'
  * match response.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """
   
Scenario: Get an "invalid" patient
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 
  * call read('classpath:patients/common/getPatientByNHSNumber.feature@invalidResource')

Scenario: Allow Healthcare Worker Access with AAL2
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: aal2_user_ID}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def nhsNumber = karate.env.includes('sandbox') ? sandboxNhsNumber : intNhsNumber
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@getPatientByNhsNumber'){ nhsNumber:"#(nhsNumber)", expectedStatus: 200 }
    * match response.id == nhsNumber
    * match response == Patient
