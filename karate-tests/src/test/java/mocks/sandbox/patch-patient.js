/* Karate objects */
/* global context, request, response, session */

/* Functions defined in supporting-functions.js */
/* global setInvalidValueError, setUnsupportedServiceError, validateHeaders, validateNHSNumber, validatePatientExists, basicResponseHeaders */

/* Functions defined in operations.js */
/* global updateAddressDetails, handleNameRemovalError, removeSuffixIfExists, removeNameSuffix, updateGivenName, updateGender, updateBirthDate,
 addNameSuffixAtStart, addNameSuffix, addNewName, removeUsualName, removeBirthDate, forbiddenUpdate, addDeceasedDate, addExtension
 updateDeceasedDate, updateExtension, updateSingleItemInExtension, removeExtensionIfExists, removeSingleItemFromExtension */

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
  if (request.body.patches.length === 0) {
    return setInvalidUpdateError(request, NO_PATCHES_PROVIDED)
  }
  const updateErrors = []

  if (request.body.patches.some(patch => patch.path.startsWith('/address'))) {
    if (!request.body.patches.some(patch => patch.path === '/address/0')) {
      if (!request.body.patches.some(patch => patch.path === '/address/0/id')) {
        updateErrors.push('Invalid update with error - no id or url found for path with root /address/0')
      }
    }
  }

  const validOperations = ['add', 'replace', 'remove', 'test']
  // Validate patch operations
  for (const patch of request.body.patches) {
    if (!validOperations.includes(patch.op)) {
      return setInvalidValueError(`Invalid value - '${patch.op}' in field '0/op'`)
    }
  }

  const updatedPatient = JSON.parse(JSON.stringify(originalPatient))

  for (const patch of request.body.patches) {
    const { op, path, value } = patch

    switch (op) {
      case 'add': {
        const addPaths = {
          '/name/-': () => addNewName(value, updatedPatient),
          '/name/0/suffix': () => addNameSuffix(updatedPatient, value),
          '/name/0/suffix/0': () => addNameSuffixAtStart(updatedPatient, value),
          '/deceasedDateTime': () => addDeceasedDate(updatedPatient, value),
          '/extension/-': () => addExtension(updatedPatient, value)
        }
        if (addPaths[path]) {
          addPaths[path]()
        }
        break
      }

      case 'replace': {
        const replacePaths = {
          '/name/0/given/0': () => updateGivenName(updatedPatient, value),
          '/gender': () => updateGender(updatedPatient, value),
          '/birthDate': () => updateBirthDate(updatedPatient, value),
          '/address/0': () => updateAddressDetails(value, updatedPatient, updateErrors),
          '/address/0/line/0': () => updateAddressDetails(value, updatedPatient, updateErrors),
          '/address/0/line': () => updateAddressDetails(value, updatedPatient, updateErrors),
          '/address/0/id': () => updateAddressDetails(value, updatedPatient, updateErrors),
          '/address/0/postalCode': () => updateAddressDetails(value, updatedPatient, updateErrors),
          '/deceasedDateTime': () => updateDeceasedDate(updatedPatient, value),
          '/extension/3': () => updateExtension(updatedPatient, 3, value),
          '/extension/4': () => updateExtension(updatedPatient, 4, value),
          '/extension/5': () => updateExtension(updatedPatient, 5, value),
          '/extension/4/extension/0': () => updateSingleItemInExtension(updatedPatient, 4, 0, value),
          '/extension/5/extension/1': () => updateSingleItemInExtension(updatedPatient, 5, 1, value)
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
          '/name/5': () => handleNameRemovalError(request, updateErrors, updatedPatient),
          '/name/0': () => removeUsualName(updatedPatient),
          '/birthDate': () => removeBirthDate(),
          '/extension/4': () => removeExtensionIfExists(updatedPatient, updateErrors, 4),
          '/extension/5/extension/2': () => removeSingleItemFromExtension(updatedPatient, 5, 2)
        }
        if (removePaths[path]) {
          removePaths[path]()
        }
        break
      }
    }
  }

  if (forbiddenUpdate) {
    return setForbiddenUpdateError(request, forbiddenUpdate)
  } else if (updateErrors.length > 0) {
    return setInvalidUpdateError(request, updateErrors[0])
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
      response.headers = buildResponseHeaders(request, updatedPatient)
      response.body = updatedPatient
      response.status = 200
    }
  }
}
