/*
    Handler for get patient's coverage by NHS Number
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders,timestampBody */

if (request.pathMatches('/Coverage') && request.get) {
  response.headers = basicResponseHeaders(request)
  const identifier = request.param('beneficiary:identifier')
  console.log('identifier##################', identifier)

  if (validateHeaders(request) && validateNHSNumber(request, identifier)) {
    if (identifier === '9733162868') {
      const COVERAGE_9733162868 = context.read('classpath:mocks/stubs/coverageResponses/patient_coverage_9733162868.json')
      response.body = timestampBody(COVERAGE_9733162868)
    }
  }
}
