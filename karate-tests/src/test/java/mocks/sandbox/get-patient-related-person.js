/*
    Handler for get related person
*/

/* Karate objects */
/* global request, response, context */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, validateNHSNumber, basicResponseHeaders, timestampBody */

/* Constants defined in stubs.js */
/* global EMPTY_SEARCHSET */

if (request.pathMatches('/Patient/{nhsNumber}/RelatedPerson') && request.get) {
  const nhsNumber = request.pathParams.nhsNumber
  if (validateHeaders(request) && validateNHSNumber(request, nhsNumber)) {
    response.headers = basicResponseHeaders(request)
    const nhsNumber = request.pathParams.nhsNumber

    if (nhsNumber === '9000000009') {
      const body = context.read('classpath:mocks/stubs/relatedPersonResponses/related_person_9000000009.json')
      response.body = timestampBody(body)
    } else if (nhsNumber === '9111231130') {
      const body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')
      response.body = timestampBody(body)
      response.status = 404
    } else if (nhsNumber === '9000000017') {
      const body = context.read('classpath:mocks/stubs/relatedPersonResponses/related_person_9000000017.json')
      response.body = timestampBody(body)
      response.status = 200
    } else {
      response.body = EMPTY_SEARCHSET
      response.body.timestamp = new Date().toISOString()
    }
  }
}
