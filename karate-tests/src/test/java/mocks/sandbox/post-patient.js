/* karate objects */
/* global context, request, response */

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

context.nhsNumberIndex = context.nhsNumberIndex || 0

function generateObjectId () {
  // generates a random ID for the name and address objects, e.g. 8F1A21BC
  return Math.random().toString(16).substr(2, 8).toUpperCase()
}

function getTodaysDate () {
  // returns today's date in the format YYYY-MM-DD
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth() + 1
  const day = today.getDate()
  return `${year}-${month < 10 ? '0' : ''}${month}-${day < 10 ? '0' : ''}${day}`
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
  const family = request.body.name['name.familyName']
  const postalCode = request.body.address['address.postalCode']
  if (family === 'McMatch-Single' && postalCode === 'BAP4WG') {
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
  let valid = true
  if (!request.body.nhsNumberAllocation) {
    const body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
    body.issue[0].diagnostics = "Missing value - 'nhsNumberAllocation'"
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
      patient.id = VALID_NHS_NUMBERS[context.nhsNumberIndex]
      patient.identifier[0].value = VALID_NHS_NUMBERS[context.nhsNumberIndex]
      context.nhsNumberIndex += 1

      // set the name properties
      patient.name[0].family = request.body.name['name.familyName']
      patient.name[0].given = [request.body.name['name.givenName.name1']]
      patient.name[0].id = generateObjectId()
      patient.name[0].period.start = getTodaysDate()
      patient.name[0].prefix = [request.body.name['name.prefix']]

      // set the address properties
      patient.address[0].id = generateObjectId()
      patient.address[0].line = [request.body.address['address.addr.line1']]
      patient.address[0].period.start = getTodaysDate()
      patient.address[0].postalCode = request.body.address['address.postalCode']
      response.body = patient
      response.status = 201
    }
  }
}
