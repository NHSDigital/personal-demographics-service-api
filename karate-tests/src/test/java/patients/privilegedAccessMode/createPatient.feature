@no-oas
Feature: Create patient - not permitted for privileged-application-restricted users
    A spike arrest policy is in a place for this endpoint, and the spike arrest policy 
    takes priority over the authentication rules. Even though we can't create a patient
    in this scenario, we have to accommodate the spike arrest policy, hence the retry...

  Background:
    * def accessToken = karate.call('classpath:auth-jwt/auth-redirect.feature', {signingKey: karate.get('privilegedAccessSigningKey'), apiKey: karate.get('privilegedAccessApiKey')}).accessToken
    * def requestHeaders = call read('classpath:auth-jwt/app-restricted-headers.js')
    * configure headers = requestHeaders  
    * url baseURL

  Scenario: Invalid Method error should be raised for nhs number allocation with privileged access
    * def display = "Cannot create resource with privileged-application-restricted access token"
    * call read('classpath:patients/common/createPatient.feature@invalidMethodCode')