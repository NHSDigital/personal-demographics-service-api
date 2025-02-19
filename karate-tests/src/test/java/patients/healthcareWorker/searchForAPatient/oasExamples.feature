@sandbox-only
Feature: Search for a patient - OAS file examples

    The public OAS file (https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir) lists a number
    of search examples and expected responses. This feature file makes sure the sandbox behaves in the same way that the
    documentation describes.

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    # auth
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
  
  Scenario: Basic search with phone & email positive
    * path 'Patient'
    * params { family: "Smith", gender: "female", birthdate: "eq2010-10-22", email: "jane.smith@example.com", phone: "01632960587" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Basic search with phone & email negative
    * path 'Patient'
    * params { family: "Smith", gender: "female", birthdate: "eq2010-10-22", email: "deb.trotter@example.com", phone: "0121111111" }
    * method get
    * status 200
    * match response == { resourceType: 'Bundle', type: 'searchset', total: 0, timestamp: '#? utils.isValidTimestamp(_)' }

  Scenario: Wildcard search without phone/email
    * path 'Patient'
    * params { family: "Sm*", gender: "female", birthdate: "eq2010-10-22" }
    * method get
    * status 200
    * match response.total == 2

  Scenario: Wildcard search with email and phone
    * path 'Patient'
    * params { family: "Sm*", gender: "female", birthdate: "eq2010-10-22", email: "jane.smith@example.com", phone: "01632960587" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Search with limited results
    * path 'Patient'
    * params { family: "Sm*", gender: "female", birthdate: "eq2010-10-22", email: "jane.smith@example.com", phone: "01632960587", _max-results: "1" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Search with date range
    * path 'Patient'
    * params { family: "Smith", gender: "female", birthdate: ["ge2010-10-21","le2010-10-23"], email: "jane.smith@example.com", phone: "01632960587" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Fuzzy search with phone and email
    * path 'Patient'
    * params { family: "Smith", given: "Jane", gender: "female", birthdate: "eq2010-10-22", email: "jane.smith@example.com", phone: "01632960587", _fuzzy-match: "true" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Fuzzy search without phone or email
    * path 'Patient'
    * params { family: "Smith", given: "Jane", gender: "female", birthdate: "eq2010-10-22", _fuzzy-match: "true" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Restricted patient search
    * path 'Patient'
    * params { family: "Smythe", given: "Janet", gender: "female", birthdate: "eq2005-06-16", email: "janet.smythe@example.com", phone: "01632960587" }
    * method get
    * status 200
    * match response.total == 1

  Scenario: Compound name search
    * path 'Patient'
    * params { family: "Smith", given: ["John Paul", "James"], gender: "male", birthdate: "eq2010-10-22", email: "johnp.smith@example.com", phone: "01632960587" }
    * method get
    * status 200
    * match response.total == 1
  
  Scenario: Search on family name and DoB - No results
    * path 'Patient'
    * params { family: "Spiderman", birthdate: "1962-07-31" }
    * method get
    * status 200
    * match response == { resourceType: 'Bundle', type: 'searchset', total: 0, timestamp: '#? utils.isValidTimestamp(_)' }