@ignore
Feature: Utils

A collection of utility functions...

Scenario:
    * def randomUUID = function(){ return java.util.UUID.randomUUID() + '' }
    * def randomInt = function() { return Math.random() * (10000 - 1) + 1 }

    * def isTodaysDate = 
    """
    function(inputDate) {
      var input = (new Date(Date.parse(inputDate)).toDateString());
      var today = (new Date()).toDateString();
      return input == today;
    }
    """
    
    * def getRandomBirthDate = 
    """
    function() {
      var min = new Date(Date.parse('1930-01-01')).getTime();
      var max = new Date(Date.parse('2020-12-31')).getTime();
      var randomValue = Math.random() * (max - min) + min;

      var randomDate = new Date(randomValue)
      return randomDate.toISOString().split('T')[0]
    }
    """

    * def sleep = function(pause){ java.lang.Thread.sleep(pause) }
    
    # pick an item at random from an array
    * def pickRandom = function(optionsArray) { Math.floor(Math.random() * optionsArray.length) }

    # validators
    * def isValidTimestamp = function(timestamp) { return !isNaN(Date.parse(timestamp)) }
    * def isValidNHSNumber = read('classpath:helpers/nhs-number-validator.js')