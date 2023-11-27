Feature: Patient Access (Retrieve)
	Retrieve a PDS record as a patient

	Scenario: Patient can retrieve self
		Given I am a P9 user
		
		When I retrieve my details

		Then I get a 200 HTTP response code

	Scenario: Patient cannot retrieve another patient
		Given I am a P9 user
		
		When I retrieve a patient

		Then I get a 403 HTTP response code

	Scenario: Patient retrieve uses incorrect path
		Given I am a P9 user
		
		When I retrieve my details using an incorrect path

		Then I get a 403 HTTP response code