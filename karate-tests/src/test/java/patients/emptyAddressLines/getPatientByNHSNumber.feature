Feature: Get a patient(patient access)- Empty address lines

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
    * def p9number = '9733162930'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: p9number, scope: 'nhs-login',clientID: karate.get('emptyAddressLinesClientID'), clientSecret:karate.get('emptyAddressLinesClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 

    * url baseURL
Scenario: Get a patient details
    * path 'Patient', p9number
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response.id == nhsNumber
    * match response == Patient
    * def addresses = response.address
    * match checkNullsHaveExtensions(addresses) == true
    #add validation for custom attribute header