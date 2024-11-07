/* Karate objects */
/* global context, request, response, session */

/* Functions defined in supporting-functions.js */
/* global setInvalidValueError, setUnsupportedServiceError, validateHeaders, validateNHSNumber, validatePatientExists, basicResponseHeaders */

/* Functions defined in operations.js */
/* global updateAddressDetails, handleNameRemovalError, removeSuffixIfExists, removeNameSuffix, updateGivenName, updateGender, updateBirthDate,
 addNameSuffixAtStart, addNameSuffix, addNewName, removeUsualName, removeBirthDate, forbiddenUpdate */

function buildResponseHeaders (request, patient) {
  return {
    'content-type': 'application/fhir+json',
    etag: `W/"${patient.meta.versionId}"`,
    'x-request-id': request.header('x-request-id'),
    'x-correlation-id': request.header('x-correlation-id')
  }
}

/*
    Diagnostics strings for error messages
*/
const NO_IF_MATCH_HEADER = 'Invalid request with error - If-Match header must be supplied to update this resource'
const NO_PATCHES_PROVIDED = 'Invalid update with error - No patches found'

/*
    Functions to handle error responses
*/
function setResourceVersionMismatchError (request) {
  const body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_VERSION_MISMATCH.json')
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 409
}

function setInvalidUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 400
}

function setPreconditionFailedError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 412
}

function setForbiddenUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 403
}

/*
    Validate the headers specific to patching a patient
*/
function validatePatchHeaders (request) {
  const ifMatchHeader = request.header('if-match')
  const contentType = request.header('content-type')
  if (!ifMatchHeader) {
    setPreconditionFailedError(request, NO_IF_MATCH_HEADER)
    return false
  }
  if (!contentType || !contentType.startsWith('application/json')) {
    setUnsupportedServiceError()
    response.headers = basicResponseHeaders(request)
    return false
  }
  return true
}

/*
    The main logic for patching a patient
*/
function patchPatient (originalPatient, request) {
  if (!request.body.patches) {
    return setInvalidUpdateError(request, NO_PATCHES_PROVIDED)
  }
  if (request.header('if-match') !== `W/"${originalPatient.meta.versionId}"`) {
    return setResourceVersionMismatchError(request)
  }

  const validOperations = ['add', 'replace', 'remove', 'test']
  // Validate patch operations
  for (const patch of request.body.patches) {
    if (!validOperations.includes(patch.op)) {
      return setInvalidValueError(`Invalid value - '${patch.op}' in field '0/op'`)
    }
  }

  const updatedPatient = JSON.parse(JSON.stringify(originalPatient))
  const updateErrors = []

  for (const patch of request.body.patches) {
    const { op, path, value } = patch

    switch (op) {
      case 'add': {
        const addPaths = {
          '/name/-': () => addNewName(value, updatedPatient),
          '/name/0/suffix': () => addNameSuffix(updatedPatient, value),
          '/name/0/suffix/0': () => addNameSuffixAtStart(updatedPatient, value)
        }
        if (addPaths[path]) {
          addPaths[path]()
        }
        break
      }

      case 'replace': {
        const updateAddressLine = () => { updateAddressDetails(value, originalPatient, updateErrors) }
        const updateAddressId = () => { updateAddressDetails(value, originalPatient, updateErrors) }

        const replacePaths = {
          '/name/0/given/0': updateGivenName(updatedPatient, value),
          '/gender': updateGender(updatedPatient, value),
          '/birthDate': updateBirthDate(updatedPatient, value),
          '/address/0/line/0': updateAddressLine,
          '/address/0/line': updateAddressLine,
          '/address/0/id': updateAddressId
        }
        if (replacePaths[path]) {
          replacePaths[path]()
        } else if (path.startsWith('/address/0/') && !Object.prototype.hasOwnProperty.call(originalPatient, 'address')) {
          updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds")
        }
        break
      }

      case 'remove':{
        const removePaths = {
          '/name/0/suffix': () => removeNameSuffix(updatedPatient),
          '/name/0/suffix/0': () => removeSuffixIfExists(updatedPatient, updateErrors, 0),
          '/name/1': () => handleNameRemovalError(request, updateErrors, updatedPatient),
          '/name/0': () => removeUsualName(updatedPatient),
          '/birthDate': () => removeBirthDate()
        }
        if (removePaths[path]) {
          removePaths[path]()
        }
        break
      }
    }
  }

  // why is it that for this specific scenario (Invalid patch - attempt to replace non-existent object),
  // we have to pick the last error message, when for all the others we pick the first error message?
  // review this logic in SPINEDEM-2695
  const rogueErrors = [
    "Invalid update with error - no 'address' resources with object id 456",
    "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
  ]

  // Handle final update errors

  if (forbiddenUpdate) {
    return setForbiddenUpdateError(request, forbiddenUpdate)
  } else if (updateErrors.length > 0) {
    if (updateErrors.every(item => rogueErrors.includes(item)) && rogueErrors.every(item => updateErrors.includes(item))) {
      return setInvalidUpdateError(request, updateErrors[1])
    } else {
      return setInvalidUpdateError(request, updateErrors[0])
    }
  } else {
    // Update patient meta versionId and return
    updatedPatient.meta.versionId = (parseInt(originalPatient.meta.versionId) + 1).toString()
    return updatedPatient
  }
}

/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {
  const valid = validateNHSNumber(request) && validatePatchHeaders(request) && validateHeaders(request) && validatePatientExists(request)

  if (valid) {
    const nhsNumber = request.pathParams.nhsNumber
    const originalPatient = session.patients[nhsNumber]
    const updatedPatient = patchPatient(originalPatient, request)
    if (updatedPatient) {
      session.patients[nhsNumber] = updatedPatient
      response.headers = buildResponseHeaders(request, updatedPatient)
      response.body = updatedPatient
      response.status = 200
    }
  }
}
