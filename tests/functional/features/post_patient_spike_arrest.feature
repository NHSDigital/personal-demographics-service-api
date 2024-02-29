Feature: Post Patient Spike Arrest Policy 
    
    Scenario: The rate limit is tripped when POSTing new Patients (>5tps)
        Given I am a healthcare worker user
        When I post to the Patient endpoint more than 5 times per second
        Then I get a 429 HTTP response code
        And returns a rate limit error message
