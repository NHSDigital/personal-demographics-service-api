/*
    Handler for get patient by NHS Number
*/

/* Karate objects */
/* global request, response, session */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, validatePatientExists, basicResponseHeaders */

if (request.pathMatches('/Patient/{nhsNumber}') && request.get) {
  response.headers = basicResponseHeaders(request)
  if (validateHeaders(request) && validateNHSNumber(request) && validatePatientExists(request)) {
    const patient = session.patients[request.pathParams.nhsNumber]
    const responseHeaders = basicResponseHeaders(request)
    responseHeaders.etag = `W/"${patient.meta.versionId}"`
    response.body = patient
    response.headers = responseHeaders
    response.status = 200
  }
}
