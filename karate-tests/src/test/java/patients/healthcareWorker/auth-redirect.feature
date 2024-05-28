@ignore
Feature: Authentication redirect for Healthcare Worker
    
Scenario: Run the relevant authentication routine
  * def userID = karate.get('userID', '656005750107')
  * def feature = 'classpath:patients/healthcareWorker/authentication.feature'
  * def routine = karate.env == 'mock' ? read('classpath:patients/healthcareWorker/authentication.feature@mock') : read('classpath:patients/healthcareWorker/authentication.feature@real')
  * call routine { userID: '#(userID)' }
