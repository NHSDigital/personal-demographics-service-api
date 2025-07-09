Feature:Trip App rate limit on int environment

@rateLimit
Scenario:Trigger rate limit with repeated requests
    * def maxAttempts = 10
    # milliseconds — 10 requests in 1 second
    * def delay = 100  
    * print 'Sending', maxAttempts, 'requests with', delay, 'ms delay'

    * def tripRateLimit =
    """
    function() {
      for (var i = 0; i < maxAttempts; i++) {
        var response = karate.call('classpath:patients/rateLimits/getPatientDetails/getPatientForRateLimitingApp.feature')
        if (response.responseStatus == 429) {
          return { status: 429,message: 'Rate limit triggered at attempt ' + (i + 1) }
        }
        java.lang.Thread.sleep(delay)
      }
      return { status: response.responseStatus, message: '429 not triggered within ' + maxAttempts + ' attempts'}
    }
    """

    * def result = tripRateLimit()
    * print result.message
