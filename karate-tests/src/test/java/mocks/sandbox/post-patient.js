/* karate objects */
/* global context, request, response, session */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders */

/*
 * Generating valid NHS numbers on the fly isn't so easy, so we just have an array of valid numbers
 * to pick from when we need to create a new patient. When the array is exhausted, the mock server
 * should reset itself to its initial state, removing all creates and updates.
 */
const VALID_NHS_NUMBERS = [
  '5182663366', '5306479413', '5865618296', '5596570559', '5061511085',
  '5954974977', '5157195761', '5897052085', '5359513144', '5446520122',
  '5103506718', '5468649624', '5002272274', '5941993854', '5574773538',
  '5899264950', '5604719625', '5117676297', '5705279671', '5890418181'
]

session.nhsNumberIndex = session.nhsNumberIndex || 0

function generateObjectId () {
  // generates a random ID for the name and address objects, e.g. 8F1A21BC
  return Math.random().toString(16).substr(2, 8).toUpperCase()
}

const NEW_PATIENT = context.read('classpath:mocks/stubs/postPatientResponses/new_patient.json')
const SINGLE_MATCH = context.read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')
const MULTIPLE_MATCHES = context.read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')

function requestMatchesErrorScenario (request) {
  // the mocks are programmed to demonstrate error scenarios where we already have matching patients
  // and we don't create a patient. There is no complex logic here where we try to mimic the matching
  // logic of the real system, just a simple check that will demonstrate the behaviour when specific
  // data is sent in the request.
  let match = false
  const family = request.body.name[0].family
  const postalCode = request.body.address[0].postalCode
  if (family === 'McMatch-Single' && postalCode === 'BAP 4WG') {
    const body = JSON.parse(JSON.stringify(SINGLE_MATCH))
    body.issue[0].diagnostics = 'Unable to create new patient. NHS number 5900054586 found for supplied demographic data.'
    response.body = body
    match = true
  } else if (family === 'McMatch-Multiple' && postalCode === 'DN19 7UD') {
    response.body = MULTIPLE_MATCHES
    match = true
  }
  return match
}

function postPatientRequestIsValid (request) {
  // check the request body has the expected structure
  let missingValue = false
  let invalidValue = false
  let valid = true
  let diagnostics = ''
  if (!request.body.name) {
    diagnostics = "Missing value - 'name'"
    missingValue = true
  } else if (!request.body.address) {
    diagnostics = "Missing value - 'address'"
    missingValue = true
  } else if (!request.body.gender) {
    diagnostics = "Missing value - 'gender'"
    missingValue = true
  } else if (!request.body.birthDate) {
    diagnostics = "Missing value - 'birthDate'"
    missingValue = true
  } else if (!Array.isArray(request.body.name[0].given)) {
    diagnostics = "Invalid value - 'not an array' in field 'name/0/given'"
    invalidValue = true
  } else if (typeof request.body.address[0] !== 'object') {
    diagnostics = `Invalid value - '${request.body.address[0]}' in field 'address/0'`
    invalidValue = true
  } else if (!['male', 'female', 'other', 'unknown'].includes(request.body.gender)) {
    diagnostics = "Invalid value - 'notAValidOption' in field 'gender'"
    invalidValue = true
  } else if (!request.body.birthDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
    diagnostics = "Invalid value - 'not-a-date' in field 'birthDate'"
    invalidValue = true
  }

  if (missingValue) {
    const body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
    body.issue[0].diagnostics = diagnostics
    response.body = body
    response.status = 400
    valid = false
  } else if (invalidValue) {
    const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json')
    body.issue[0].diagnostics = diagnostics
    response.body = body
    response.status = 400
    valid = false
  }
  return valid
}

function userHasPermission (request) {
  // check the user making the request has permission to create a patient
  let valid = true
  if (request.header('Authorization') === 'Bearer APP_RESTRICTED') {
    const body = context.read('classpath:mocks/stubs/errorResponses/INVALID_METHOD.json')
    body.issue[0].details.coding[0].display = 'Cannot create resource with application-restricted access token'
    response.body = body
    response.status = 403
    valid = false
  }
  return valid
}

if (request.pathMatches('/Patient') && request.post) {
  response.headers = basicResponseHeaders(request)
  response.contentType = 'application/fhir+json'
  if (userHasPermission(request) && postPatientRequestIsValid(request)) {
    if (!requestMatchesErrorScenario(request)) {
      // clone the NEW_PATIENT object, then set properties based on the contents of the request body
      const patient = JSON.parse(JSON.stringify(NEW_PATIENT))

      // set a new NHS number for the patient
      patient.id = VALID_NHS_NUMBERS[session.nhsNumberIndex]
      patient.identifier[0].value = VALID_NHS_NUMBERS[session.nhsNumberIndex]
      session.nhsNumberIndex += 1

      // name and address objects need an ID
      patient.name[0] = request.body.name[0]
      patient.name[0].id = generateObjectId()

      // in the address object, the line property is an array that can contain blank strings. For the response,
      // the blank strings are removed.
      const line = request.body.address[0].line.filter((line) => line !== '')
      patient.address[0] = request.body.address[0]
      patient.address[0].line = line
      patient.address[0].id = generateObjectId()

      // set the other properties
      patient.gender = request.body.gender
      patient.birthDate = request.body.birthDate

      response.body = patient
      response.status = 201
    }
  }
}
