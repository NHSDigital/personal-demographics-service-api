/*
    Handler for get patient's coverage by NHS Number
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders,timestampBody,setInvalidSearchDataError */

function buildResponseHeaders (request, patientCoverageDetails) {
  return {
    'content-type': 'application/fhir+json',
    etag: `W/"${patientCoverageDetails.meta.versionId}"`,
    'x-request-id': request.header('x-request-id'),
    'x-correlation-id': request.header('x-correlation-id')
  }
}
function buildResponse (request, responseBody) {
  response.headers = buildResponseHeaders(request, responseBody)
  response.body = timestampBody(responseBody)
  response.status = 200
}

if (request.pathMatches('/Coverage') && request.get) {
  response.headers = basicResponseHeaders(request)
  const nhsNumber = request.param('subscriber:identifier')
  const VALID_PARAMS = new Set(['subscriber:identifier'])
  const paramKeys = Object.keys(request.params)
  const validParams = paramKeys.filter(param => VALID_PARAMS.has(param))
  const invalidParams = paramKeys.filter(param => !VALID_PARAMS.has(param))

  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber) && validParams.length === 1) {
    const responseMap = {
      9000000009: 'classpath:mocks/stubs/coverageResponses/patient_with_coverage_9000000009.json',
      9000000033: 'classpath:mocks/stubs/coverageResponses/patient_without_coverage.json'
    }
    const responsePath = responseMap[nhsNumber]
    if (responsePath) {
      const responseData = context.read(responsePath)
      buildResponse(request, responseData)
    }
  } else if (invalidParams.length === 1 || paramKeys.length === 0) {
    const diagnostics = "Invalid search data provided - 'Coverage search request must follow the format /Coverage?subscriber:identifier=NHS_NUMBER'"
    setInvalidSearchDataError(diagnostics)
  }
}
