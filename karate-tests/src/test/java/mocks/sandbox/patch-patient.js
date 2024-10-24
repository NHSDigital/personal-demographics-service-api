/* Karate objects */
/* global context, request, response, session */

/* Functions defined in supporting-functions.js */
/* global setInvalidValueError, setUnsupportedServiceError, validateHeaders, validateNHSNumber, validatePatientExists, basicResponseHeaders */

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

function setForbiddenUpdateError (request, diagnostics) {
  const body = context.read('classpath:mocks/stubs/errorResponses/FORBIDDEN_UPDATE.json')
  body.issue[0].diagnostics = diagnostics
  response.headers = basicResponseHeaders(request)
  response.body = body
  response.status = 403
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

/*
    Validate the headers specific to patching a patient
*/
function validatePatchHeaders (request) {
  let valid = true
  if (!request.header('if-match')) {
    setPreconditionFailedError(request, NO_IF_MATCH_HEADER)
    valid = false
  }
  if (valid && !request.header('content-type').startsWith('application/json')) {
    setUnsupportedServiceError()
    response.headers = basicResponseHeaders(request)
    valid = false
  }
  return valid
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
  for (let i = 0; i < request.body.patches.length; i++) {
    const patch = request.body.patches[i]
    if (!validOperations.includes(patch.op)) {
      return setInvalidValueError(`Invalid value - '${patch.op}' in field '0/op'`)
    }
  }
  const updatedPatient = JSON.parse(JSON.stringify(originalPatient))
  let forbiddenUpdate = false
  const updateErrors = []

  for (let i = 0; i < request.body.patches.length; i++) {
    const patch = request.body.patches[i]
    if (patch.op === 'add' && patch.path === '/name/-') {
      if (patch.value.use === 'usual') {
        forbiddenUpdate = 'Forbidden update with error - multiple usual names cannot be added'
      } else {
        patch.value.id = 'new-object-id'
        updatedPatient.name.push(patch.value)
      }
    }
    if (patch.op === 'add' && patch.path === '/name/0/suffix') {
      updatedPatient.name[0].suffix = patch.value
    }
    if (patch.op === 'add' && patch.path === '/name/0/suffix/0') {
      updatedPatient.name[0].suffix.splice(0, 0, patch.value)
    }
    if (patch.op === 'replace' && patch.path === '/name/0/given/0') {
      updatedPatient.name[0].given[0] = patch.value
    }
    if (patch.op === 'replace' && patch.path === '/gender') {
      updatedPatient.gender = patch.value
    }
    if (patch.op === 'replace' && patch.path === '/birthDate') {
      updatedPatient.birthDate = patch.value
    }
    if (patch.op === 'remove' && patch.path === '/name/0/suffix') {
      if (!updatedPatient.name[0].suffix) {
        updateErrors.push("Invalid update with error - Invalid patch - can't remove non-existent object '0'")
      } else {
        delete updatedPatient.name[0].suffix
      }
    }
    if (patch.op === 'remove' && patch.path === '/name/0/suffix/0') {
      if (!updatedPatient.name[0].suffix) {
        updateErrors.push("Invalid update with error - Invalid patch - can't remove non-existent object '0'")
      } else {
        updatedPatient.name[0].suffix.splice(0, 1)
      }
    }

    if (patch.op === 'remove' && patch.path === '/name/1') {
      if (!request.body.patches[0].op === 'test' || !request.body.patches[0].path.startsWith('/name/1/id')) {
        updateErrors.push("Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item")
      } else if (request.body.patches[0].path === '/name/1/id' && request.body.patches[0].value === '123456') {
        updateErrors.push("Invalid update with error - Invalid patch - index '1' is out of bounds")
      } else {
        updatedPatient.name.splice(1, 1)
      }
    }

    if (patch.op === 'remove' && patch.path === '/name/0') {
      if (request.body.patches[0].value.use === 'usual') {
        forbiddenUpdate = 'Forbidden update with error - not permitted to remove usual name'
      }
    }

    if (patch.op === 'remove' && patch.path === '/birthDate') {
      forbiddenUpdate = 'Forbidden update with error - source not permitted to remove \'birthDate\''
    }
    // these specific error scenarios for update errors should be reviewed in SPINEDEM-2695
    if (patch.op === 'replace' && patch.path === '/address/0/line/0' && patch.value === '2 Whitehall Quay') {
      updateErrors.push('Invalid update with error - no id or url found for path with root /address/0')
    } else if (patch.op === 'replace' && patch.path.startsWith('/address/0/') && !Object.prototype.hasOwnProperty.call(originalPatient, 'address')) {
      updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds")
    } else if (patch.op === 'replace' && patch.path === '/address/0/id' && patch.value === '456') {
      updateErrors.push("Invalid update with error - no 'address' resources with object id 456")
    } else if (patch.op === 'replace' && patch.path === '/address/0/line') {
      updateErrors.push("Invalid update with error - Invalid patch - can't replace non-existent object 'line'")
    } else if (patch.op === 'replace' && patch.path === '/address/0/id' && patch.value === '123456') {
      updateErrors.push("Invalid update with error - no 'address' resources with object id '123456'")
    }
  }

  // why is it that for this specific scenario (Invalid patch - attempt to replace non-existent object),
  // we have to pick the last error message, when for all the others we pick the first error message?
  // review this logic in SPINEDEM-2695
  const rogueErrors = [
    "Invalid update with error - no 'address' resources with object id 456",
    "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
  ]

  if (forbiddenUpdate) {
    return setForbiddenUpdateError(request, forbiddenUpdate)
  } else if (updateErrors.length > 0) {
    if (updateErrors.every(item => rogueErrors.includes(item)) && rogueErrors.every(item => updateErrors.includes(item))) {
      return setInvalidUpdateError(request, updateErrors[1])
    } else {
      return setInvalidUpdateError(request, updateErrors[0])
    }
  } else {
    updatedPatient.meta.versionId = (parseInt(originalPatient.meta.versionId) + 1)
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
