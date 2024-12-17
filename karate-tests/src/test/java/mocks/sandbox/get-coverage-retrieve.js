/*
    Handler for get patient's coverage by NHS Number
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders,timestampBody, EMPTY_SEARCHSET */

if (request.pathMatches('/Coverage') && request.get) {
  response.headers = basicResponseHeaders(request)
  const nhsNumber = request.param('beneficiary:identifier')
  console.log('NHS number from request', nhsNumber)

  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber)) {
    if (nhsNumber === '9733162868') {
      const COVERAGE_9733162868 = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162868.json')
      response.body = timestampBody(COVERAGE_9733162868)
    } else if (nhsNumber === '9733162876') {
      response.body = EMPTY_SEARCHSET
      response.body.timestamp = new Date().toISOString()
    }
  }
}
