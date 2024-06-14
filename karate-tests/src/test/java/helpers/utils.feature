@ignore
Feature: Utils

A collection of utility functions for generating, validating and manipulating data

Scenario:
  # data generators
  * def randomUUID = function(){ return java.util.UUID.randomUUID() + '' }
  * def randomInt = function() { return Math.floor(Math.random() * 99) + 1 }
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
      const min = new Date(Date.parse('1930-01-01')).getTime()
      const max = new Date(Date.parse('2023-09-01')).getTime()
      const randomValue = Math.random() * (max - min) + min
      const randomDate = new Date(randomValue)
      return randomDate.toISOString().split('T')[0]
    }
    """

  * def randomDate = 
    """
    function(earliest) {
      const min = new Date(Date.parse(earliest)).getTime()
      const max = new Date(Date.parse('2023-09-01')).getTime()
      const randomValue = Math.random() * (max - min) + min
      const randomDate = new Date(randomValue)
      return randomDate.toISOString().split('T')[0]
    }
    """

  * def randomAddress =
  """
  function(earliestStartDate) {
    const addresses = karate.read('classpath:helpers/addresses.json')
    const randomAddress = addresses[Math.floor(Math.random() * addresses.length)]
    const min = new Date(Date.parse(earliestStartDate)).getTime()
    const max = new Date(Date.parse('2023-09-01')).getTime()
    const addressStartDate = new Date(Math.random() * (max - min) + min).toISOString().split('T')[0]
    const street = `${Math.floor(Math.random() * 99) + 1} ${randomAddress.street}`
    const addressObject = {
        period: {"start": addressStartDate},
        use: "home",
        postalCode: randomAddress.postalCode,
        line: [street, randomAddress.city]
      }
    return addressObject
  }
  """

  * def randomGender = 
  """
  function() {
    const genders = ['male', 'female', 'other', 'unknown']
    return genders[Math.floor(Math.random() * genders.length)];
  }
  """

  * def randomPrefix = 
  """
  function() {
    const prefixes = ['Mr', 'Mrs', 'Miss', 'Ms', 'Dr', 'Prof', 'Rev', 'Sir', 'Lady', 'Lord']
    return prefixes[Math.floor(Math.random() * prefixes.length)];
  }
  """
  
  # data validators
  * def isTodaysDate = 
    """
    function(inputDate) {
      const input = (new Date(Date.parse(inputDate)).toDateString())
      const today = (new Date()).toDateString()
      return input == today
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
      const regex=new RegExp("([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])T\\d{2}:\\d{2}:\\d{2}\\+\\d{2}:\\d{2})$|^([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])T\\d{2}:\\d{2}:\\d{2})$|^([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])T\\d{2}:\\d{2}:\\d{2}\\+\\d{2}:\\d{2})$|^([12]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01]))")
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
      let pattern = "((([A-Z][0-9]{1,2})|(([A-Z][A-HJ-Y][0-9]{1,2})|"
      pattern += "(([AZ][0-9][A-Z])|([A-Z][A-HJ-Y][0-9]?[A-Z]))))[0-9][A-Z]{2})"
      const regex = new RegExp(pattern)
      return regex.test(postalCode)
    }
    """

  * def isValidNHSNumber = read('classpath:helpers/nhs-number-validator.js')
  * def isValidPatientURL = 
    """
    function(url) {
      const baseURL = karate.get('internalServerURL') + "/Patient/"
      if (!url.startsWith(baseURL)) return false
      const nhsNumber = url.split('/')[url.split('/').length -1]
      const validNHSNumber = karate.call('classpath:helpers/nhs-number-validator.js', nhsNumber)
      return validNHSNumber
    }
    """

  * def validateResponseHeaders = 
    """
    function(requestHeaders) {
      /*
        validate the values of the x-correlation-id and x-correlation-id response headers match those
        of the request (if they were provided)
      */
      let validRequestID = false
      let validCorrelationID = false

      const requestID = requestHeaders['x-request-id']
      const correlationID = requestHeaders['x-correlation-id']
      
      if (!requestID) { 
        validRequestID = karate.response.header('x-request-id') == null        
      } else if (requestID === '""') {
        validRequestID = karate.response.header('x-request-id') == null        
      } else {
        validRequestID = requestID == karate.response.header('x-request-id')  
      }
      return validRequestID
    }
    """
  
  # other utility functions
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