// eslint-disable-next-line no-unused-vars
function updateAddressDetails (value, originalPatient, updateErrors) {
  if (value === '2 Whitehall Quay') {
    updateErrors.push('Invalid update with error - no id or url found for path with root /address/0')
  } else if (!Object.prototype.hasOwnProperty.call(originalPatient, 'address')) {
    updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds")
  } else if (value === '456') {
    updateErrors.push("Invalid update with error - no 'address' resources with object id 456")
  } else if (value === '123456') {
    updateErrors.push("Invalid update with error - no 'address' resources with object id '123456'")
  } else {
    updateErrors.push("Invalid update with error - Invalid patch - can't replace non-existent object 'line'")
  }
}

// eslint-disable-next-line no-unused-vars
function handleNameRemovalError (request, updateErrors, patient) {
  if (!request.body.patches[0]?.op === 'test' || !request.body.patches[0].path.startsWith('/name/1/id')) {
    updateErrors.push("Invalid update with error - removal '/name/1' is not immediately preceded by equivalent test - instead it is the first item")
  } else if (request.body.patches[0].path === '/name/1/id' && request.body.patches[0].value === '123456') {
    updateErrors.push("Invalid update with error - Invalid patch - index '1' is out of bounds")
  } else {
    patient.name.splice(1, 1)
  }
}

// eslint-disable-next-line no-unused-vars
function removeNameSuffix (patient) {
  delete patient.name[0].suffix
}

// eslint-disable-next-line no-unused-vars
function removeSuffixIfExists (patient, updateErrors, suffixIndex) {
  if (!patient.name[0].suffix) {
    updateErrors.push("Invalid update with error - Invalid patch - can't remove non-existent object '0'")
  } else {
    patient.name[0].suffix.splice(suffixIndex, 1)
  }
}

// eslint-disable-next-line no-unused-vars
function updateGivenName (patient, givenName) {
  patient.name[0].given[0] = givenName
}

// eslint-disable-next-line no-unused-vars
function updateGender (patient, gender) {
  patient.gender = gender
}

// eslint-disable-next-line no-unused-vars
function updateBirthDate (patient, birthDate) {
  patient.birthDate = birthDate
}

// eslint-disable-next-line no-unused-vars
function addNameSuffixAtStart (patient, name) {
  patient.name[0].suffix.unshift(name)
}

// eslint-disable-next-line no-unused-vars
function addNameSuffix (patient, suffix) {
  patient.name[0].suffix = suffix
}

// eslint-disable-next-line no-unused-vars
function addNewName (patient, name) {
  name.id = 'new-object-id'
  patient.name.push(name)
}

// eslint-disable-next-line no-unused-vars
function addUsualName (value) {
  if (value.use === 'usual') {
    return 'Forbidden update with error - multiple usual names cannot be added'
  }
}
