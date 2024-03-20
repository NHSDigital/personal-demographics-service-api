@ignore
Feature: Utils

A collection of utility functions for generating, validating and manipulating data

Scenario:
  # data generators
  * def randomUUID = function(){ return java.util.UUID.randomUUID() + '' }
  * def randomInt = function() { return Math.floor(Math.random() * 999) + 1 }
  * def randomString = 
  """
  function(length) {
    let result = '';
    const characters = 'abcdefghijklmnopqrstuvwxyz';
    const charactersLength = characters.length;

    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }

    return result;
  }
  """
  * def randomBirthDate = 
  """
  function() {
    var min = new Date(Date.parse('1930-01-01')).getTime();
    var max = new Date(Date.parse('2023-09-01')).getTime();
    var randomValue = Math.random() * (max - min) + min;

    var randomDate = new Date(randomValue)
    return randomDate.toISOString().split('T')[0]
  }
  """

  # data validators
  * def isTodaysDate = 
  """
  function(inputDate) {
    var input = (new Date(Date.parse(inputDate)).toDateString());
    var today = (new Date()).toDateString();
    return input == today;
  }
  """

  * def isValidTimestamp = function(timestamp) { return !isNaN(Date.parse(timestamp)) }
  * def isValidDateString = 
  """
  function (dateString) {
    var regex=new RegExp("([0-9]{4}[-](0[1-9]|1[0-2])[-]([0-2]{1}[0-9]{1}|3[0-1]{1})|([0-2]{1}[0-9]{1}|3[0-1]{1})[-](0[1-9]|1[0-2])[-][0-9]{4})");
    return regex.test(dateString);
  }
  """

  * def isValidPostalCode = 
  """
  function(postalCode) {
    postalCode = postalCode.replaceAll(" ", "")
    var regex = new RegExp("^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))[0-9][A-Za-z]{2})$")
    return regex.test(postalCode)
  }
  """

  * def isValidNHSNumber = read('classpath:helpers/nhs-number-validator.js')
  * def isValidPatientURL = 
  """
  function(url) {
    var baseURL = "https://veit07.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/"
    var nhsNumber = url.split('/')[url.split('/').length -1]
    var validNHSNumber = karate.call('classpath:helpers/nhs-number-validator.js', nhsNumber)
    return validNHSNumber
  }
  """
  
  # other utility functions
  * def sleep = function(seconds){ java.lang.Thread.sleep(seconds * 1000) }
  
  # pick an item at random from an array, ignoring one of the items
  * def pickDifferentOption = 
  """
  function(optionsArray, itemToIgnore) {
    const index = optionsArray.indexOf(itemToIgnore);
    optionsArray.splice(index, 1)
    return optionsArray[Math.floor(Math.random() * optionsArray.length)]
  }
  """
  
    
    