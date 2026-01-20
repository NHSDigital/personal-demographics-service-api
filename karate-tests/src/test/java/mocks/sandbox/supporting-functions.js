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
  body.issue[0].details.coding[0].display = 'Access Denied - Unauthorised'
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

// eslint-disable-next-line no-unused-vars
function setUnsupportedServiceError () {
  response.body = context.read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json')
  response.status = 400
}

// eslint-disable-next-line no-unused-vars
function setAdditionalPropertiesError (diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/ADDITIONAL_PROPERTIES.json')
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
 * There is always the option to not use a valid UUID, if you want to simplify
 * things and make your access token reflect the type of user you're authenticating
 * as...
 *
 * @param {string} uuid - The string to be checked.
 * @returns {boolean} - Returns true if the string is a valid UUID, otherwise false.
 */
function isValidUUID (uuid) {
  const regex = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/
  return regex.test(uuid)
}

function isValidAuthToken (token) {
  const regex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]+(_[a-zA-Z0-9]+)?$/
  return regex.test(token)
}

/*
 * validate the oauth2 bearer token
 */
function isValidBearerToken (token, validateTokenPart = false) {
  const tokenParts = token.split(' ')
  if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
    return false
  }
  if (validateTokenPart && !isValidAuthToken(tokenParts[1])) {
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
function validateAuthHeader (request) {
  // Check if the Authorization header is present and correct
  const authorization = request.header('Authorization')
  if (!authorization) {
    // authorization is not mandatory on sandbox
    return true
  } else if (!isValidBearerToken(authorization)) {
    setAccessDeniedError('Missing access token')
    return false
  } else if (!isValidBearerToken(authorization, true)) {
    setAccessDeniedError('Invalid Access Token')
    return false
  }
  return true
}

function validateRequestIDHeader (request) {
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
  return validateRequestIDHeader(request) && validateAuthHeader(request)
}

/**
 * Validates the NHS number from the request.
 *
 * @param {Object} request - The request object.
 * @param {Object} nhsNumber - The nhsNumber param.
 * @returns {boolean} - Returns true if the NHS number is valid, otherwise false.
 */
// eslint-disable-next-line no-unused-vars
function validateNHSNumber (request, nhsNumber) {
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
  if (session.patients[nhsNumber] === undefined) {
    response.body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')
    response.headers = basicResponseHeaders(request)
    response.status = 404
    valid = false
  }
  return valid
}

/*
  Add a timestamp to the body of the response
*/
// eslint-disable-next-line no-unused-vars
function timestampBody (body) {
  // timestamp format is '2019-12-25T12:00:00+00:00'
  body.timestamp = new Date().toISOString()
  return body
}

/*
    Diagnostics strings for error messages
*/
// eslint-disable-next-line no-unused-vars
const NO_IF_MATCH_HEADER = 'Invalid request with error - If-Match header must be supplied to update this resource'
// eslint-disable-next-line no-unused-vars
const NO_PATCHES_PROVIDED = 'Invalid update with error - No patches found'

/*
    Functions to handle error responses
*/
// eslint-disable-next-line no-unused-vars
function setResourceVersionMismatchError (request) {
  const body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_VERSION_MISMATCH.json')
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 409
}
// eslint-disable-next-line no-unused-vars
function setInvalidUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 400
}
// eslint-disable-next-line no-unused-vars
function setPreconditionFailedError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 412
}
// eslint-disable-next-line no-unused-vars
function setForbiddenUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 403
}
