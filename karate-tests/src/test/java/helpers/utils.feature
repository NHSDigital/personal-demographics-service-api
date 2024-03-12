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
    * def sleep = function(pause){ java.lang.Thread.sleep(pause) }
    * def pickRandom = function(optionsArray) { Math.floor(Math.random() * optionsArray.length) }
    # validators
    * def isValidTimestamp = function(timestamp) { return !isNaN(Date.parse(timestamp)) }
    * def isValidNHSNumber = read('classpath:helpers/nhs-number-validator.js')