Feature: Patient Access (Retrieve)
    Retrieve a PDS record as a patient

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
    * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')

    * configure url = baseURL
    * def p9number = '9912003071'
    * def p5number = '9912003072'
    * def p0number = '9912003073'

  @smoke
  Scenario: P9 Patient can authenticate and retrieve their own details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == p9number
    * match response == Patient

  @ignore
  Scenario Outline: <patientType> users can authenticate but can't retrieve their own details (<patientType> example)
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

    Examples:
      | patientType | nhsNumber   |
      | P0          | 9912003073  |
      | P5          | 9912003072  |
      | P9.Cp       | 5900068196  |

  Scenario: P9 Patient can't retrieve details of another patient
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p5number
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

  Scenario: P9 Patient can't search for a patient (including searching for their own record)
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient'
    * params { family: 'Bobins', gender: 'male', birthDate: "eq2008-06-03" }
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
   
  @ignore 
  Scenario Outline: <patientTypeAndVot> user can authenticate and retrieve their own details
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == nhsNumber
    * match response == Patient

    Examples:
    | patientTypeAndVot | nhsNumber   |
    | P9.Cp.Cd          | 9900000285  |
    | P9.Cm             | 5900071332  |
    | P9.Cp.Ck          | 5900069176  |
