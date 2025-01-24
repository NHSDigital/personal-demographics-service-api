/*
    Handler for get patient's coverage by NHS Number
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders,timestampBody */

function buildResponseHeaders (request) {
  return {
    'content-type': 'application/fhir+json',
    etag: 'W/"1"',
    'x-request-id': request.header('x-request-id'),
    'x-correlation-id': request.header('x-correlation-id')
  }
}
function buildResponse (request, responseBody) {
  response.headers = buildResponseHeaders(request)
  response.body = timestampBody(responseBody)
  response.status = 200
}

if (request.pathMatches('/Coverage') && request.get) {
  response.headers = basicResponseHeaders(request)
  const nhsNumber = request.param('subscriber:identifier')

  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber)) {
    if (nhsNumber === '9733162868') {
      const COVERAGE_9733162868 = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162868.json')
      buildResponse(request, COVERAGE_9733162868)
    } else if (nhsNumber === '9733162876') {
      const NO_COVERAGE_9733162876 = context.read('classpath:mocks/stubs/coverageResponses/patient_without_coverage.json')
      buildResponse(request, NO_COVERAGE_9733162876)
    } else if (nhsNumber === '9733162892') {
      const COVERAGE_9733162892 = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162892.json')
      buildResponse(request, COVERAGE_9733162892)
    }
  }
}
