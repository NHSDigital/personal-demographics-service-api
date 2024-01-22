Feature: Allocate an NHS Number
	Attempt to allocate an NHS Number

	Scenario: A patient cannot allocate an NHS number
		Given I am a P9 user
		And scope added to product
		
		When I request an NHS number

		Then I get a 403 HTTP response code
	
	Scenario: An application-restricted app cannot allocate an NHS number
		Given I am a application-restricted user
		
		When I request an NHS number

		Then I get a 403 HTTP response code

	Scenario: A healthcare worker can allocate an NHS number
		Given I am a P9 user
		And scope added to product
		
		When I request an NHS number

		Then I get a 400 HTTP response code