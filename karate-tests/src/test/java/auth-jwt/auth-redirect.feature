@ignore
Feature: Authentication redirect for Application Restricted access
    
Scenario: Run the relevant authentication routine
  * def userID = karate.get('userID', '656005750107')
  * def feature = 'classpath:auth-jwt/authentication.feature'
  * def routine = karate.env.includes('sandbox') ? read('classpath:auth-jwt/authentication.feature@mock') : read('classpath:auth-jwt/authentication.feature@real')
  * call routine { userID: '#(userID)' }
