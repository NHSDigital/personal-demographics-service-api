Feature: Patient access levels

  See this page: https://digital.nhs.uk/services/nhs-login/nhs-login-for-partners-and-developers/nhs-login-integration-toolkit/how-nhs-login-works

  Background:
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
  
    * configure url = baseURL
    * def p9number = '9912003071'

    # so, why don't we have these patients in the database?
    * def p5number = '9912003072'
    * def p0number = '9912003073'
  
    * url baseURL

  Scenario: P0 patient cannot log in
    # Low level verification (P0)
    # The user has verified ownership of an email address and mobile phone number. They have not proven who they are or provided any other personal details.
    * def accessToken = karate.callSingle('classpath:patients/healthcareWorker/auth-redirect.feature', {userID: p0number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:patients/healthcareWorker/healthcare-worker-headers.js')
    * configure headers = requestHeaders 
    * path 'Patient', p0number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)

  Scenario: Get a P5 patient
    # Medium level verification (P5)
    # The user has provided some additional information, which has been checked to correspond to a record on the NHS Personal Demographics Service (PDS).
    #
    # This information may include:
    # - date of birth
    # - NHS number
    # - name
    # - postcode
    #
    # Medium level verification can allow users to do things like contact their GP or receive notifications. It does not provide access to health records or personal information.
    * path 'Patient', p5number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)

  Scenario: Get a P9 patient
    # High level verification (P9)
    # The user must prove who they are in order to gain access to health records or personal information. To be verified to the highest level, a user must have completed an online or offline identity verification process, where physical comparison between photo ID and the user has been made.
    #
    # To do this, a user has 4 options:
    # The first three options are known as 'Prove your Identity online' (PYI) and using your GP surgery online services is known 'Patient On Line' (POL).
    #
    # - Fast-track ID check (IDVM)
    # - Photo ID and a face scan
    # - Photo ID and a video
    # - GP surgery online services registration details
    * path 'Patient', p9number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
