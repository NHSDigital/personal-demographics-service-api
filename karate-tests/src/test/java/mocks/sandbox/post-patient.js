/* karate objects */
/* global context, request, response */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders,validateHeaders */

/*
 * Generating valid NHS numbers on the fly isn't so easy, so we just have an array of valid numbers
 * to pick from when we need to create a new patient. When the array is exhausted, the mock server
 * should reset itself to its initial state, removing all creates and updates.
 */

function generateObjectId () {
  // generates a random ID for the name and address objects, e.g. 8F1A21BC
  return Math.random().toString(16).slice(2, 8).toUpperCase()
}

const NEW_PATIENT = context.read('classpath:mocks/stubs/postPatientResponses/new_patient.json')
const SINGLE_MATCH = context.read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')
const MULTIPLE_MATCHES = context.read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')

function requestMatchesErrorScenario (request) {
  // the mocks are programmed to demonstrate error scenarios where we already have matching patients
  // and we don't create a patient. There is no complex logic here where we try to mimic the matching
  // logic of the real system, just a simple check that will demonstrate the behaviour when specific
  // data is sent in the request.

  const family = request.body.name[0].family
  const postalCode = request.body.address[0].postalCode

  const matchConditions = [
    {
      condition: family === 'McMatch-Single' && postalCode === 'BAP 4WG',
      responseBody: () => {
        const body = structuredClone(SINGLE_MATCH)
        body.issue[0].diagnostics = 'Unable to create new patient. NHS number 5900054586 found for supplied demographic data.'
        return body
      }
    },
    {
      condition: family === 'McMatch-Multiple' && postalCode === 'DN19 7UD',
      responseBody: () => MULTIPLE_MATCHES
    }
  ]
  for (const { condition, responseBody } of matchConditions) {
    if (condition) {
      response.body = responseBody()
      return true
    }
  }
  return false
}

function postPatientRequestIsValid (request) {
  const diagnosticsMap = {
    missing: 'classpath:mocks/stubs/errorResponses/MISSING_VALUE.json',
    invalid: 'classpath:mocks/stubs/errorResponses/INVALID_VALUE.json'
  }
  const validations = [
    {
      condition: !request.body?.name,
      diagnostics: 'Missing value - \'name\'',
      type: 'missing'
    },
    {
      condition: !request.body?.address,
      diagnostics: 'Missing value - \'address\'',
      type: 'missing'
    },
    {
      condition: !request.body?.gender,
      diagnostics: 'Missing value - \'gender\'',
      type: 'missing'
    },
    {
      condition: !request.body?.birthDate,
      diagnostics: 'Missing value - \'birthDate\'',
      type: 'missing'
    },
    {
      condition: Array.isArray(request.body?.address?.[0]),
      diagnostics: `Invalid value - '${JSON.stringify(request.body?.address?.[0] || {})
  .replaceAll('"', "'")
  .replaceAll("','", "', '")}' in field 'address/0'`,
      type: 'invalid'
    },
    {
      condition: !request.body?.address?.[0].period,
      diagnostics: 'Missing value - \'address/0/period\'',
      type: 'missing'
    },
    {
      condition: !Array.isArray(request.body?.name?.[0]?.given) || ['O`Brien'].includes(request.body?.name?.[0]?.given),
      diagnostics: `Invalid value - '${request.body?.name?.[0]?.given}' in field 'name/0/given'`,
      type: 'invalid'
    },
    {
      condition: typeof request.body?.address?.[0] !== 'object' || Array.isArray(request.body?.address?.[0]),
      diagnostics: `Invalid value - '${request.body?.address?.[0]}' in field 'address/0'`,
      type: 'invalid'
    },
    {
      condition: !['male', 'female', 'unknown'].includes(request.body?.gender),
      diagnostics: 'Invalid value - \'other\' in field \'gender\'',
      type: 'invalid'
    },
    {
      condition: !request.body?.birthDate?.match(/^\d{4}-\d{2}-\d{2}$/),
      diagnostics: 'Invalid value - \'not-a-date\' in field \'birthDate\'',
      type: 'invalid'
    }
  ]

  for (const { condition, diagnostics, type } of validations) {
    if (condition) {
      const body = context.read(diagnosticsMap[type])
      body.issue[0].diagnostics = diagnostics
      response.body = body
      response.status = 400
      return false
    }
  }

  return true
}

function initializePatientData (request) {
  const patient = structuredClone(NEW_PATIENT)

  // set a new NHS number for the patient

  patient.id = '5182663366'
  patient.identifier[0].value = '5182663366'

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

  return patient
}

function handlePatientCreationRequest (request) {
  response.headers = basicResponseHeaders(request)
  response.contentType = 'application/fhir+json'
  const isRequestHeadersValid = validateHeaders(request)
  if (isRequestHeadersValid) {
    if (postPatientRequestIsValid(request)) {
      if (!requestMatchesErrorScenario(request)) {
        const patient = initializePatientData(request)
        response.body = patient
        response.status = 201
      }
    }
  }
}

// Check if the incoming request is a POST to the /Patient endpoint and handle accordingly
if (request.pathMatches('/Patient') && request.post) {
  handlePatientCreationRequest(request)
}
