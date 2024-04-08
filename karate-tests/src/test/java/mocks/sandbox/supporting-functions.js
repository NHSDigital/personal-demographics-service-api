/* Karate objects */
/* global context, response, session */

/**
 * Generates basic response headers based on the provided request.
 *
 * @param {Object} request - The request object.
 * @returns {Object} - The response headers object.
 */
function basicResponseHeaders (request) {
  return {
    'content-type': 'application/fhir+json',
    'x-request-id': request.headers['x-request-id'],
    'x-correlation-id': request.headers['x-correlation-id']
  }
};

/*********************************************************************************************************************
 *   Error responses
 *********************************************************************************************************************/

/**
 * Sets an invalid value error response for a given field and value.
 * @param {string} field - The header field name.
 * @param {string} value - The invalid value.
 * @param {object} request - The request object.
 */
function setInvalidValueError (field, value, request) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  body.issue[0].diagnostics = `Invalid value - '${value}' in header '${field}'`
  response.body = body
  response.headers = basicResponseHeaders(request)
  response.status = 400
}

function setMissingValueError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 400
}

/**
 * Sets an invalid search data error response.
 *
 * @param {string} diagnostics - The diagnostics message for the error.
 */
// eslint-disable-next-line no-unused-vars
function setInvalidSearchDataError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 400
}

/**
 * Sets an INVALID_UPDATE error response for the given request and diagnostics.
 *
 * @param {Object} request - The request object.
 * @param {Array} diagnostics - The diagnostics to be set in the error response.
 */
// eslint-disable-next-line no-unused-vars
function setInvalidUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 400
}

/*********************************************************************************************************************
 *   Validation functions
 *********************************************************************************************************************/

// reading this file gives us the `validate` function for validating NHS numbers
context.read('classpath:helpers/nhs-number-validator.js')
/* global validate */

/**
 * Checks if a given string is a valid UUID.
 *
 * @param {string} uuid - The string to be checked.
 * @returns {boolean} - Returns true if the string is a valid UUID, otherwise false.
 */
function isValidUUID (uuid) {
  const regex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}/
  return regex.test(uuid)
}

/**
 * Validates the headers of a request.
 *
 * @param {Request} request - The request object.
 * @returns {boolean} - Returns true if the headers are valid, false otherwise.
 */
// eslint-disable-next-line no-unused-vars
function validateHeaders (request) {
  const X_REQUEST_ID = 'X-Request-ID'

  let valid = true

  const requestID = request.header('x-request-id')
  if (!requestID) {
    const diagnostics = 'Invalid request with error - X-Request-ID header must be supplied to access this resource'
    setMissingValueError(diagnostics)
    valid = false
  } else if (!isValidUUID(requestID)) {
    setInvalidValueError(X_REQUEST_ID, requestID, request)
    valid = false
  }
  return valid
}

/**
 * Validates the NHS number from the request.
 *
 * @param {Object} request - The request object.
 * @returns {boolean} - Returns true if the NHS number is valid, otherwise false.
 */
// eslint-disable-next-line no-unused-vars
function validateNHSNumber (request) {
  const nhsNumber = request.pathParams.nhsNumber
  let valid = true
  const validNHSNumber = validate(nhsNumber)
  if (!validNHSNumber) {
    valid = false
    response.headers = basicResponseHeaders(request)
    response.body = context.read('classpath:mocks/stubs/errorResponses/INVALID_RESOURCE_ID.json')
    response.status = 400
  }
  return valid
}

/**
 * Validates if a patient exists based on the provided NHS number.
 *
 * @param {Object} request - The request object containing the path parameters.
 * @returns {boolean} - Returns true if the patient exists, false otherwise.
 */
// eslint-disable-next-line no-unused-vars
function validatePatientExists (request) {
  const nhsNumber = request.pathParams.nhsNumber
  let valid = true
  if (typeof session.patients[nhsNumber] === 'undefined') {
    response.body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')
    response.headers = basicResponseHeaders(request)
    response.status = 404
    valid = false
  }
  return valid
}
