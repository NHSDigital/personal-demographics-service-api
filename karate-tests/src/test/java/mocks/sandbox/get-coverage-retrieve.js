/*
    Handler for get patient's coverage by NHS Number
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders,timestampBody */

if (request.pathMatches('/Coverage') && request.get) {
  response.headers = basicResponseHeaders(request)
  const nhsNumber = request.param('beneficiary:identifier')

  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber)) {
    if (nhsNumber === '9733162868') {
      const COVERAGE_9733162868 = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162868.json')
      response.body = timestampBody(COVERAGE_9733162868)
    } else if (nhsNumber === '9733162876') {
      const NO_COVERAGE_9733162868 = context.read('classpath:mocks/stubs/coverageResponses/patient_without_coverage.json')
      response.body = timestampBody(NO_COVERAGE_9733162868)
    }
  }
}
