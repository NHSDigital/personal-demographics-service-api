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
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')

    * configure url = baseURL
    * def p9number = '9912003071'
    * def p5number = '9912003072'
    * def p0number = '9912003073'

  Scenario: P9 Patient can authenticate and retrieve their own details
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p9number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == p9number
    * match response == Patient

  Scenario Outline: P0 and P5 users can authenticate but can't retrieve their own details (<patientType> example)
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

  Scenario: P9 Patient can't retrieve details of another patient
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p5number, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders
    * path 'Patient', p5number
    * method get
    * status 403
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * def display = 'Patient cannot perform this action'
    * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
    * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

    # Scenario: Patient attempts to search for a patient
    #     Given I am a P9 user
    #     And scope added to product
    
    #     When I search for a patient's PDS record

    #     Then I get a 403 HTTP response code
    #     And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
    #     And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body

    # Scenario: Patient cannot retrieve their record with an expired token
    #     Given I am a P9 user
    #     And scope added to product
    #     And I have an expired access token

    #     When I retrieve my details

    #     Then I get a 401 HTTP response code
    #     And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
    #     And Access Token expired is at issue[0].diagnostics in the response body

    # Scenario: Patient can retrieve their record with a refreshed token
    #     Given I am a P9 user
    #     And scope added to product
    #     And I have a refreshed access token

    #     When I retrieve my details

    #     Then I get a 200 HTTP response code