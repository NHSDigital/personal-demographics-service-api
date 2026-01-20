    @no-oas
Feature: Create a new PDS record at birth - not permitted for application-restricted users
  
  Background:
    * def accessToken = karate.callSingle('classpath:auth-jwt/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders  
  
  Scenario: Invalid Method error should be raised for creat a new record at birth - application-restricted users
    * def display = "Cannot create resource with application-restricted access token"
    * call read('classpath:patients/common/createNewPdsRecordAtBirth.feature@invalidMethodCode')