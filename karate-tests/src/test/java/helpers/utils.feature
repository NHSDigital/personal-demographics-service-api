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
      let result = ''
      const characters = 'abcdefghijklmnopqrstuvwxyz'
      const charactersLength = characters.length

      for (let i = 0; i < length; i++) {
          result += characters.charAt(Math.floor(Math.random() * charactersLength))
      }

      return result;
    }
    """
  * def randomBirthDate = 
    """
    function() {
      var min = new Date(Date.parse('1930-01-01')).getTime()
      var max = new Date(Date.parse('2023-09-01')).getTime()
      var randomValue = Math.random() * (max - min) + min;

      var randomDate = new Date(randomValue)
      return randomDate.toISOString().split('T')[0]
    }
    """

  # data validators
  * def isTodaysDate = 
    """
    function(inputDate) {
      var input = (new Date(Date.parse(inputDate)).toDateString())
      var today = (new Date()).toDateString()
      return input == today;
    }
    """

  * def isValidTimestamp = function(timestamp) { return !isNaN(Date.parse(timestamp)) }
  
  * def isValidDateString = 
    """
    function (dateString) {
      /* 
        validates the date string based on how we format dates in FIHR, 
        e.g. 2010-10-25 is valid
      */
      var regex=new RegExp("([0-9]{4}[-](0[1-9]|1[0-2])[-]([0-2]{1}[0-9]{1}|3[0-1]{1})|([0-2]{1}[0-9]{1}|3[0-1]{1})[-](0[1-9]|1[0-2])[-][0-9]{4})")
      return regex.test(dateString)
    }
    """

  * def isValidPostalCode = 
    """
    function(postalCode) {
      /*
        this regex should check if a string represents a valid UK postal code, more or less...
        (it's not so straightforward to get a working regex for this)
      */
      postalCode = postalCode.replaceAll(" ", "")
      var pattern = "((([A-Z][0-9]{1,2})|(([A-Z][A-HJ-Y][0-9]{1,2})|"
      pattern += "(([AZ][0-9][A-Z])|([A-Z][A-HJ-Y][0-9]?[A-Z]))))[0-9][A-Z]{2})"
      var regex = new RegExp(pattern)
      return regex.test(postalCode)
    }
    """

  * def isValidNHSNumber = read('classpath:helpers/nhs-number-validator.js')
  * def isValidPatientURL = 
    """
    function(url) {
      var baseURL = karate.get('internalServerURL') + "Patient/"
      var nhsNumber = url.split('/')[url.split('/').length -1]
      var validNHSNumber = karate.call('classpath:helpers/nhs-number-validator.js', nhsNumber)
      return validNHSNumber
    }
    """
  
  # other utility functions
  * def sleep = function(seconds){ java.lang.Thread.sleep(seconds * 1000) }
  
  * def pickDifferentOption = 
    """
    function(optionsArray, itemToIgnore) {
      /*
        pick an item at random from an array, ignoring one of the items, e.g. 
          optionsArray = ['apples', 'bananas', 'pears']
          itemToIgnore = 'bananas'
          returns either 'apples' or 'pears', but not 'bananas'
      */
      const index = optionsArray.indexOf(itemToIgnore)
      optionsArray.splice(index, 1)
      return optionsArray[Math.floor(Math.random() * optionsArray.length)]
    }
    """
  
    
    