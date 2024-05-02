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
function setInvalidValueError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 400
}

function setMissingValueError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 400
}

function setAccessDeniedError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/ACCESS_DENIED.json')
  body.issue[0].diagnostics = diagnostics
  response.body = body
  response.status = 401
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

/*
   * validate the oauth2 bearer token
    */
function isValidBearerToken(token) {
  const tokenParts = token.split(' ')
  if (tokenParts.length !== 2) {
    return false
  } else if (tokenParts[0] !== 'Bearer') {
    return false
  } else if (!isValidUUID(tokenParts[1])) {
    return false
  }
  return true
}

/**
 * Validates the headers of a request.
 *
 * @param {Request} request - The request object.
 * @returns {boolean} - Returns true if the headers are valid, false otherwise.
 */
function validateAuthHeader(request) {
  let valid = true
  let diagnostics = ''
  // Check if the Authorization header is present and correct
  const authorization = request.header('Authorization')
  if (!('authorization' in request.headers)) {
    diagnostics = 'Missing Authorization header'
    valid = false
  } else if (authorization === '') {
    diagnostics = 'Empty Authorization header'
    valid = false
  } else if (!isValidBearerToken(authorization)) {
    diagnostics = 'Invalid Access Token'
    valid = false
  }
  if (!valid) {
    setAccessDeniedError(diagnostics)
  }
  return valid
}

function validateRequestIDHeader(request) {
  // Check if the X-Request-ID header is present and correct
  let valid = true
  const requestID = request.header('x-request-id')
  if (!requestID) {
    const diagnostics = 'Invalid request with error - X-Request-ID header must be supplied to access this resource'
    setMissingValueError(diagnostics)
    valid = false
  } else if (!isValidUUID(requestID)) {
    const diagnostics = `Invalid value - '${requestID}' in header 'X-Request-ID'`
    setInvalidValueError(diagnostics)
    valid = false
  }
  return valid
}

// eslint-disable-next-line no-unused-vars
function validateHeaders (request) {
  if (!validateRequestIDHeader(request)) {
    return false
  } else if (!validateAuthHeader(request)) {
    return false
  }
  return true
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
