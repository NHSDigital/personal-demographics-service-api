/* Karate objects */
/* global request, response, session */

/* Functions defined in supporting-functions.js */
/* global setInvalidValueError, setUnsupportedServiceError, validateHeaders, validateNHSNumber, validatePatientExists, basicResponseHeaders, NO_IF_MATCH_HEADER,
NO_PATCHES_PROVIDED, setResourceVersionMismatchError, setInvalidUpdateError, setPreconditionFailedError, setForbiddenUpdateError */

/* Functions defined in operations.js */
/* global updateAddressDetails, handleNameRemovalError, removeSuffixIfExists, removeNameSuffix, updateGivenName, updateGender, updateBirthDate,
 addNameSuffixAtStart, addNameSuffix, addNewName, removeUsualName, removeBirthDate, forbiddenUpdate, addDeceasedDate, addExtension
 updateDeceasedDate, updateExtension, updateSingleItemInExtension, removeExtensionIfExists, removeSingleItemFromExtension, removeGender */

function buildResponseHeaders (request, patient) {
  return {
    'content-type': 'application/fhir+json',
    etag: `W/"${patient.meta.versionId}"`,
    'x-request-id': request.header('x-request-id'),
    'x-correlation-id': request.header('x-correlation-id')
  }
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
  if (!contentType?.startsWith('application/json')) {
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
  const patches = request.body.patches
  if (!patches || patches.length === 0) {
    return setInvalidUpdateError(request, NO_PATCHES_PROVIDED)
  }

  if (request.header('if-match') !== `W/"${originalPatient.meta.versionId}"`) {
    return setResourceVersionMismatchError(request)
  }

  const updateErrors = []
  validateAddressPatches(patches, updateErrors)

  if (!validatePatchOperations(patches)) {
    return setInvalidValueError(`Invalid value - '${patches[0].op}' in field '0/op'`)
  }

  const updatedPatient = structuredClone(originalPatient)

  for (const patch of patches) {
    applyPatch(patch, updatedPatient, originalPatient, updateErrors, request)
  }

  if (forbiddenUpdate) {
    return setForbiddenUpdateError(request, forbiddenUpdate)
  }

  if (updateErrors.length > 0) {
    return setInvalidUpdateError(request, updateErrors[0])
  }

  updatedPatient.meta.versionId = (
    Number.parseInt(originalPatient.meta.versionId) + 1
  ).toString()

  return updatedPatient
}

function validateAddressPatches (patches, updateErrors) {
  const hasAddressPatch = patches.some(p => p.path.startsWith('/address'))
  const hasRootAddress = patches.some(p => p.path === '/address/0')
  const hasId = patches.some(p => p.path === '/address/0/id')

  if (hasAddressPatch && !hasRootAddress && !hasId) {
    updateErrors.push('Invalid update with error - no id or url found for path with root /address/0')
  }
}

function validatePatchOperations (patches) {
  const validOperations = new Set(['add', 'replace', 'remove', 'test'])
  return patches.every(patch => validOperations.has(patch.op))
}

function applyPatch (patch, updatedPatient, originalPatient, updateErrors, request) {
  const { op, path, value } = patch

  const opHandlers = {
    add: {
      '/name/-': () => addNewName(value, updatedPatient),
      '/name/0/suffix': () => addNameSuffix(updatedPatient, value),
      '/name/0/suffix/0': () => addNameSuffixAtStart(updatedPatient, value),
      '/deceasedDateTime': () => addDeceasedDate(updatedPatient, value),
      '/extension/-': () => addExtension(updatedPatient, value)
    },
    replace: {
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
    },
    remove: {
      '/name/0/suffix': () => removeNameSuffix(updatedPatient),
      '/name/0/suffix/0': () => removeSuffixIfExists(updatedPatient, updateErrors, 0),
      '/name/1': () => handleNameRemovalError(request, updateErrors, updatedPatient),
      '/name/5': () => handleNameRemovalError(request, updateErrors, updatedPatient),
      '/name/0': () => removeUsualName(updatedPatient),
      '/birthDate': () => removeBirthDate(),
      '/gender': () => removeGender(),
      '/extension/4': () => removeExtensionIfExists(updatedPatient, updateErrors, 4),
      '/extension/1': () => removeExtensionIfExists(updatedPatient, updateErrors, 1),
      '/extension/5/extension/2': () => removeSingleItemFromExtension(updatedPatient, 5, 2)
    }
  }

  const handler = opHandlers[op]?.[path]
  if (handler) {
    handler()
  } else if (op === 'replace' && path.startsWith('/address/0/') &&
             !Object.hasOwn(originalPatient, 'address')) {
    updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds")
  }
}
/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {
  const nhsNumber = request.pathParams.nhsNumber
  const valid = validateNHSNumber(request, nhsNumber) && validatePatchHeaders(request) && validateHeaders(request) && validatePatientExists(request)

  if (valid) {
    const originalPatient = session.patients[nhsNumber]
    const updatedPatient = patchPatient(originalPatient, request)
    if (updatedPatient) {
      response.headers = buildResponseHeaders(request, updatedPatient)
      response.body = updatedPatient
      response.status = 200
    }
  }
}
