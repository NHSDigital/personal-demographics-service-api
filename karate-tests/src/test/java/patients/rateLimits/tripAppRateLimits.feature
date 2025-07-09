Feature:Trip App rate limit on int environment

@rateLimit
Scenario:Trigger rate limit with repeated requests
    * def maxAttempts = karate.get('rateLimitOnApp') + 1
    * print maxAttempts
    * def delay = 500  
    * def found429 = false

    * def tripRateLimit =
    """
    function() {
      for (var i = 0; i < maxAttempts; i++) {
        var response = karate.call('classpath:helpers/getPatientForRateLimitingApp.feature')
        if (response.responseStatus == 429) {
          return { status: 429 }
        }
        java.lang.Thread.sleep(delay)
      }
      return { status: response.responseStatus}
    }
    """

    * def result = tripRateLimit()
    * match result.status == 429
