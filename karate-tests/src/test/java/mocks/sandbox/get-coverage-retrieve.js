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
  const nhsNumber = request.param('beneficiary:identifier')

  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber)) {
    if (nhsNumber === '9000000009') {
      const COVERAGE_9000000009 = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9000000009.json')
      buildResponse(request, COVERAGE_9000000009)
    } else if (nhsNumber === '9000000033') {
      const NO_COVERAGE_9000000033 = context.read('classpath:mocks/stubs/coverageResponses/patient_without_coverage.json')
      buildResponse(request, NO_COVERAGE_9000000033)
    }
  }
}
