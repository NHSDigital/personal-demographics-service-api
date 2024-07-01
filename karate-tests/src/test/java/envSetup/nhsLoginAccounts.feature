Feature: NHS Login accounts

    This confluence page lists NHS Login test users that we should be able to use in tests:

    https://nhsd-confluence.digital.nhs.uk/display/APM/Testing+with+mock+auth#Testingwithmockauth-NHSLogintestusers
    
    This feature simply demonstrates how these users are currently configured in the system under test

  Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json Period = karate.readAsString('classpath:schemas/Period.json')
    * json Address = karate.readAsString('classpath:schemas/Address.json')
    * json HumanName = karate.readAsString('classpath:schemas/HumanName.json')
    * json OtherContactSystem = karate.readAsString('classpath:schemas/extensions/OtherContactSystem.json')
    * json ContactRelationship = karate.readAsString('classpath:schemas/codeable/ContactRelationship.json')
    * json Contact = karate.readAsString('classpath:schemas/Contact.json')
    * json ContactPoint = karate.readAsString('classpath:schemas/ContactPoint.json')
    * json GeneralPractitionerReference = karate.readAsString('classpath:schemas/GeneralPractitionerReference.json')
    * json ManagingOrganizationReference = karate.readAsString('classpath:schemas/ManagingOrganizationReference.json')
    * json Patient = karate.readAsString('classpath:schemas/Patient.json')
  
    * configure url = baseURL

  Scenario Outline: P9 patients that can authenticate using nhs-login (<nhsNumber> <family> <given>)
    # all of the p9 patients listed in the doc can authenticate using nhs-login
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * assert accessToken != null

    Examples:
      | nhsNumber     | family    | given     |
      | 9912003071    | USER      | TEST      | 
      | 9472063845    | Egan      | Dennis    |
      | 9900000285    | WILDE     | Martin    | 
      | 9472063810    | Gorman    | Nathan    | 
      | 9472063802    | Hannay    | Jeff      | 
      | 9462978182    | GREENE    | Andrea    | 
      | 9462767386    | Wrench    | SHERI     | 
      | 9462767270    | LOGAN     | KIERAN    | 
      | 9446041481    | DENIS     | Forest    | 
      | 5900110915    | NICHOLSEN | GARFIELD  |

  Scenario Outline: P9 patients that have corresponding patient objects (<given> <family> example)
    # but only two of them have a corresponding patient object
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * assert utils.validateResponseHeaders(requestHeaders, responseHeaders)
    * match response == Patient

    Examples:
      | nhsNumber     | family    | given     |
      | 9912003071    | USER      | TEST      | 
      | 9472063845    | Egan      | Dennis    |

  Scenario Outline: P9 patients that don't have corresponding patient objects (<nhsNumber> <family> <given>)
    # the rest of them don't have corresponding patient objects...
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {userID: nhsNumber, scope: 'nhs-login'}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * path 'Patient', nhsNumber
    * method get
    * status 404

    Examples:
      | nhsNumber     | family    | given     |
      | 9900000285    | WILDE     | Martin    | 
      | 9472063810    | Gorman    | Nathan    | 
      | 9472063802    | Hannay    | Jeff      | 
      | 9462978182    | GREENE    | Andrea    | 
      | 9462767386    | Wrench    | SHERI     | 
      | 9462767270    | LOGAN     | KIERAN    | 
      | 9446041481    | DENIS     | Forest    | 
      | 5900110915    | NICHOLSEN | GARFIELD  |
