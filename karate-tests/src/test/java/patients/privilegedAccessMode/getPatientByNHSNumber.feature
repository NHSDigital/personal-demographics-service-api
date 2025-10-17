    @no-oas
Feature: Get a patient - privileged-application-restricted access mode

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
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders 
    * url baseURL

  Scenario: Get a "restricted" (sensitive) patient response should include address, telecoms, registered GP and nominated pharmacy details for privileged access
    * def nhsNumber = '9727022820'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == nhsNumber
    * match response == Patient
    * match response.address != null
    * match response.generalPractitioner != null
    * match response.telecom != null
    * match responseHeaders['Nhse-Pds-Privileged-Access'] == '#notpresent'
    * match response.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """
 
  Scenario: Get a "very restricted" patient response should not include address, telecoms, registered GP and nominated pharmacy details for privileged access
    * def nhsNumber = '9727024610'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == nhsNumber

  
    * match response.name == '#notpresent'
    * match response.birthDate == '#notpresent'
    * match response.address == '#notpresent'
    * match response.generalPractitioner == '#notpresent'
    * match response.telecom == '#notpresent'
    * match responseHeaders['Nhse-Pds-Privileged-Access'] == '#notpresent'
    * match response.meta.security[0] == 
    """
    {
      "code": "V",
      "display": "very restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """   

  Scenario: Get a non sensitive patient details with privileged access
    * configure headers = requestHeaders  
    * def nhsNumber = '9733162825'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.id == nhsNumber
    * match response == Patient

    @no-oas
  Scenario: Get a patient details- RemovalReasonExitCode should be Armed Forces (notified by Armed Forces) AFN with privileged access
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * def nhsNumber = '9733162507'  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "AFN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Armed Forces (notified by Armed Forces)" 
    * match response.meta.security[0] == 
    """
    {
      "code": "R",
      "display": "restricted",
      "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality"
    }
    """ 
  
  Scenario: Retrieve a patient with an invalid NHS number format should return 'invalid resource' with privileged access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@invalidResource')

  Scenario: Retrieve a patient with non-existent records should return 'RESOURCE_NOT_FOUND' with privileged access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@resourceNotFound')

  Scenario: Retrieve a patient with invalidated records should return 'INVALIDATED_RESOURCE' with privileged access
    * call read('classpath:patients/common/getPatientByNHSNumber.feature@invalidatedResource')