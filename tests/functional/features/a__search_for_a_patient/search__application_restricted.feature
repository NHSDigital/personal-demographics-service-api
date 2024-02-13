Feature: Search for a patient - Application-restricted access mode

  Background:
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token
    Given path "/Patient"

  Scenario: Basic search with phone & email positive	
    Given params
      {
        "family": "Smith", 
        "gender": "female", 
        "birthdate": "eq2010-10-22", 
        "email": "jane.smith@example.com", 
        "phone": "01632960587"
      }
    When GET request
    Then status 200
    And response body
      {
        "resourceType": "Bundle",
        "timestamp": "#date-time",
        "total": "#integer",
        "type": "searchset"
      }  
  
  #
      
  # Scenario: Search on given name, family name, postcode and date of birth
    

  # Scenario: Search using wildcards

  # Scenario: Fuzzy search, multiple matches

  # Scenario: Non-fuzzy search, close matching

  # Scenario: Non-exact match

  # Scenario: Include history