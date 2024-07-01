@sandbox
Feature: Search errors

Background:
  * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
  * configure headers = call read('classpath:auth/auth-headers.js')
  * url baseURL


Scenario: All invalid params
  * path 'Patient'  
  * params {manufacturer: "Ford", model: "focus", year: "2003" }
  * method get
  * status 400
  # The order of properties in the diagnostics message is not guaranteed, so we have assert the string in a roundabout way for this test
  * def diagnostics = response.issue[0].diagnostics
  * assert diagnostics.startsWith("Invalid request with error - Additional properties are not allowed ")
  * assert diagnostics.includes("model")
  * assert diagnostics.includes("manufacturer")
  * assert diagnostics.includes("year")
  * assert diagnostics.endsWith("were unexpected)")
  * match response == read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')

Scenario: One invalid param
  * path 'Patient'
  * params { family: "Smith", birthdate: "eq2010-10-22", year: "2003" }
  * method get
  * status 400
  * def diagnostics = "Invalid request with error - Additional properties are not allowed ('year' was unexpected)"
  * match response == read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')

Scenario: Valid/invalid search criteria
  * path 'Patient'
  * params { family: "Sm*", gender: "female", invalidParam: "123", birthdate: "eq2010-10-22", email: "j.smith@example.com", phone: "0163" }
  * method get
  * status 400
  * def diagnostics = "Invalid request with error - Additional properties are not allowed ('invalidParam' was unexpected)"
  * match response == read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')

Scenario: Unsuccessful search on email/phone only
  * path 'Patient'
  * params { email: "j.smith@example.com", phone: "0163" }
  * method get
  * status 400
  * def diagnostics = "Missing value - 'birth_date/birth_date_range_start/birth_date_range_end'"
  * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')

Scenario: Invalid date format (birthdate)
  * path 'Patient'  
  * params { family: "Smith", given: "jane", gender: "female", birthdate: "20101022" } 
  * method get
  * status 400
  * def diagnostics = "Invalid value - '20101022' in field 'birthdate'"
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')

Scenario: Invalid date format (death-date)
  * path 'Patient'  
  * params { family: "Smith", given: "jane", gender: "female", death-date: "20101022" } 
  * method get
  * status 400
  * def diagnostics = "Invalid value - '20101022' in field 'death-date'"
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')

Scenario: Too few search params - No params
  * path 'Patient'    
  * params {}
  * method get
  * status 400
  * match response == read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json')


Scenario: Too few search params - Missing params other than birthdate
  * path 'Patient'    
  * params { birthdate: "eq2010-10-22" }
  * method get
  * status 400
  * def diagnostics = "Invalid search data provided - 'No searches were performed as the search criteria did not meet the minimum requirements'"
  * match response == read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')

Scenario: Too few search params - but system only flags birthdate!
  * path 'Patient'    
  * params { gender: 'female' }
  * method get
  * status 400
  * def diagnostics = "Missing value - 'birth_date/birth_date_range_start/birth_date_range_end'"
  * match response == read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')