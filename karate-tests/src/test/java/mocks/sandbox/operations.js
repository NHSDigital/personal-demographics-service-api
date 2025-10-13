function updateAddressDetails (value, originalPatient, updateErrors) {
  if (!Object.hasOwn(originalPatient, 'address')) {
    updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds")
  } else if (value === '123456') {
    updateErrors.push("Invalid update with error - no 'address' resources with object id '123456'")
  } else if (value === '2 Whitehall Quay') {
    originalPatient.address[0].line[0] = value
  } else if (value === 'LS1 4BU') {
    originalPatient.address[0].postalCode = value
  } else if (Array.isArray(value)) {
    updateErrors.push("Invalid update with error - Invalid patch - can't replace non-existent object 'line'")
  } else if (typeof value === 'object') {
    originalPatient.address[0] = value
  }
}

function handleNameRemovalError (request, updateErrors, patient) {
  const firstPatch = request.body.patches?.[0]

  if (!firstPatch) {
    updateErrors.push('Invalid update with error - missing patch operation')
    return
  }

  if (firstPatch.op !== 'test' || !firstPatch.path.startsWith('/name/1/id')) {
    updateErrors.push("Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item")
  } else if (firstPatch.path === '/name/1/id' && firstPatch.value === '123456') {
    updateErrors.push("Invalid update with error - Invalid patch - index '1' is out of bounds")
  } else {
    patient.name.splice(1, 1)
  }
}

function removeNameSuffix (patient) {
  delete patient.name[0].suffix
}

function removeSuffixIfExists (patient, updateErrors, suffixIndex) {
  if (!patient.name[0].suffix) {
    updateErrors.push("Invalid update with error - Invalid patch - can't remove non-existent object '0'")
  } else {
    patient.name[0].suffix.splice(suffixIndex, 1)
  }
}

function updateGivenName (patient, givenName) {
  patient.name[0].given[0] = givenName
}

function updateGender (patient, gender) {
  patient.gender = gender
}

function updateBirthDate (patient, birthDate) {
  patient.birthDate = birthDate
}

function addNameSuffixAtStart (patient, name) {
  patient.name[0].suffix.unshift(name)
}

function addNameSuffix (patient, suffix) {
  patient.name[0].suffix = suffix
}

let forbiddenUpdate = null
function addNewName (value, patient) {
  if (value.use === 'usual') {
    forbiddenUpdate = 'Forbidden update with error - multiple usual names cannot be added'
  } else {
    value.id = 'new-object-id'
    patient.name.push(value)
  }
}

function removeUsualName (patient) {
  if (patient.name[0].use === 'usual') {
    forbiddenUpdate = 'Forbidden update with error - not permitted to remove usual name'
  }
}

function removeBirthDate () {
  forbiddenUpdate = 'Forbidden update with error - source not permitted to remove \'birthDate\''
}

function removeGender () {
  forbiddenUpdate = 'Forbidden update with error - source not permitted to remove \'gender\''
}

function addDeceasedDate (patient, value) {
  patient.deceasedDateTime = value
}

function addExtension (patient, value) {
  patient.extension = [value]
}

function updateDeceasedDate (patient, value) {
  patient.deceasedDateTime = value
}

function updateExtension (patient, index, value) {
  patient.extension[index] = value
}

function updateSingleItemInExtension (patient, index, childIndex, value) {
  patient.extension[index].extension[childIndex] = value
}

function removeExtensionIfExists (patient, updateErrors, index) {
  if (!patient.extension[index]) {
    updateErrors.push("Invalid update with error - Invalid patch - can't remove non-existent object '0'")
  } else {
    delete patient.extension[index]
  }
}

function removeSingleItemFromExtension (patient, index, childIndex) {
  patient.extension[index].extension.splice(childIndex, 1)
}
