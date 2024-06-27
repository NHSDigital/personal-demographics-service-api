Feature: Patient updates their details

Scenario: Patient can update their record
    Given I am a P9 user
    And scope added to product
    And I have my record to update
    And I wish to update my telephone number

    When I update my PDS record

    Then I get a 200 HTTP response code
    And the response body contains the record's new version number

  Scenario: Patient cannot update another patient
    Given I am a P9 user
    And scope added to product
    And I have another patient's NHS number

    When I update another patient's PDS record

    Then I get a 403 HTTP response code
    And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body
 
  Scenario: Patient update uses incorrect path
    Given I am a P9 user
    And scope added to product

    When I update another patient's PDS record using an incorrect path

    Then I get a 403 HTTP response code
    And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body

