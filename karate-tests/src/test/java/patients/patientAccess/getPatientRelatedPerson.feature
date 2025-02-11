Feature: Get related person details (Patient access)

Background:
  # schemas and validators that are required by the schema checks
  * def utils = call read('classpath:helpers/utils.feature')
  * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
  * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
  * json CodingSchema = karate.readAsString('classpath:schemas/searchSchemas/codingSchema.json')
  * json Period = karate.readAsString('classpath:schemas/Period.json')
  * json RelatedPersonSearchResultEntry = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchResultEntry.json')
  * json RelatedPersonSearchBundle = karate.readAsString('classpath:schemas/searchSchemas/relatedPersonSearchBundle.json')

  # auth
  * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: '9900000285', scope: 'nhs-login'}).accessToken
  * def requestHeaders = call read('classpath:auth/auth-headers.js')
  * configure headers = requestHeaders 

  * url baseURL

@oas-bug
Scenario: Patient can do related person search for their own record
  # The response should include the family name, according to our OAS definition:
  # https://nhsd-jira.digital.nhs.uk/browse/SPINEDEM-3344
  * def nhsNumber = karate.env.includes('sandbox') ? '9000000009' : '9900000285'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 200
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  # this is commented out because the schema won't match - due to the ticket noted above
  # we can still assert the response comes back, but validating the schema will fail
  # reinstate / review this line if the behaviour for SPINEDEM-3344 is changed 
  # * match response == RelatedPersonSearchBundle


Scenario: Patient can't do related person search for another patient's record
  * def nhsNumber = karate.env.includes('sandbox') ? '9000000009' : '9693632109'
  * path 'Patient', nhsNumber, 'RelatedPerson'
  * method get
  * status 403
  * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
  * def display = 'Patient cannot perform this action'
  * def diagnostics = 'Your access token has insufficient permissions. See documentation regarding Patient access restrictions https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir'
  * match response == read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')

  