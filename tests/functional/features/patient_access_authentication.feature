Feature: Patient Access - authentication
	Our P5 and P0 patients cannot authenticate
	Scenario: Patient with P5 authorisation level cannot authenticate
		Given I am a P5 user with the NHS number linked to an account
		
		When I sign in using NHS login

		Then I get a 401 HTTP response code
		And unauthorized_client is at error in the response body
		And you have tried to request authorization but your application is not configured to use this authorization grant type is at error_description in the response body
	
	Scenario: Patient with P0 authorisation level cannot authenticate
		Given I am a P0 user with the NHS number linked to an account
		
		When I sign in using NHS login

		Then I get a 401 HTTP response code
		And unauthorized_client is at error in the response body
		And you have tried to request authorization but your application is not configured to use this authorization grant type is at error_description in the response body
