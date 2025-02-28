Feature: Post Patient Spike Arrest Policy

Scenario: The rate limit is tripped when POSTing new Patients (>3tps)
    Given I am a healthcare worker user
    When I post to the Patient endpoint more than 3 times per second
    Then I get a mix of 400 and 429 HTTP response codes
    And the 429 response bodies alert me that there have been too many Create Patient requests
