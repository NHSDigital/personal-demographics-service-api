@ignore
Feature: Authentication redirect for Healthcare Worker and Patient access
    
Scenario: Run the relevant authentication routine
  * def userID = karate.get('userID', '656005750107')
  # call with scope: 'nhs-login' if you're using NHS Login authentication
  * def scope = karate.get('scope', null)
  * def routine = karate.env == 'mock' ? read('classpath:auth/authentication.feature@mock') : read('classpath:auth/authentication.feature@real')
  * call routine { userID: '#(userID)', scope: '#(scope)' }
