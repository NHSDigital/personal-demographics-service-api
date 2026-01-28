/* karate objects */
/* global context, request, response */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders,validateHeaders */

/* global Java */

/*
 * Generating valid NHS numbers on the fly isn't so easy, so we just have an array of valid numbers
 * to pick from when we need to create a new patient. When the array is exhausted, the mock server
 * should reset itself to its initial state, removing all creates and updates.
 */

function generateObjectId () {
  // generates a random ID for the name and address objects, e.g. 8F1A21BC
  // Using Java's SecureRandom instead of Math.random() to satisfy security requirements
  const SecureRandom = Java.type('java.security.SecureRandom')
  const random = new SecureRandom()

  let hex = ''
  for (let i = 0; i < 4; i++) { // NOSONAR - traditional loop needed for Java random generation
    const randomByte = random.nextInt(256)
    hex += randomByte.toString(16).padStart(2, '0')
  }
  return hex.substring(0, 8).toUpperCase()
}

const NEW_PATIENT_AT_BIRTH = context.read('classpath:mocks/stubs/postPdsRecordAtBirthResponses/new_pds_record_at_birth.json')
const SINGLE_MATCH_AT_BIRTH = context.read('classpath:mocks/stubs/postPatientResponses/SINGLE_MATCH_FOUND.json')
const MULTIPLE_MATCHES_AT_BIRTH = context.read('classpath:mocks/stubs/postPatientResponses/MULTIPLE_MATCHES_FOUND.json')

function requestMatchesErrorScenario (request) {
  // the mocks are programmed to demonstrate error scenarios where we already have matching patients
  // and we don't create a patient. There is no complex logic here where we try to mimic the matching
  // logic of the real system, just a simple check that will demonstrate the behaviour when specific
  // data is sent in the request.

  // Find the baby patient (the one without an NHS number identifier)
  const patientEntry = request.body?.entry?.find(entry =>
    entry.resource?.resourceType === 'Patient' &&
    !entry.resource?.identifier?.some(id => id.system === 'https://fhir.nhs.uk/Id/nhs-number')
  )
  const patient = patientEntry?.resource

  if (!patient) return false

  const family = patient.name[0].family
  const postalCode = patient.address[0].postalCode

  const matchConditions = [
    {
      condition: family === 'McMatch-Single' && postalCode === 'BAP 4WG',
      responseBody: () => {
        const body = JSON.parse(JSON.stringify(SINGLE_MATCH_AT_BIRTH)) // NOSONAR - structuredClone not available in Karate
        body.issue[0].diagnostics = 'Unable to create new patient. NHS number 5900004899 found for supplied demographic data.'
        return body
      }
    },
    {
      condition: family === 'McMatch-Multiple' && postalCode === 'DN19 7UD',
      responseBody: () => MULTIPLE_MATCHES_AT_BIRTH
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

  // Find the baby patient resource (the one without an NHS number identifier)
  const patientEntry = request.body?.entry?.find(entry =>
    entry.resource?.resourceType === 'Patient' &&
    !entry.resource?.identifier?.some(id => id.system === 'https://fhir.nhs.uk/Id/nhs-number')
  )
  const patient = patientEntry?.resource

  if (!patient) {
    const body = context.read(diagnosticsMap.missing)
    body.issue[0].diagnostics = 'Missing baby Patient resource in entry array'
    response.body = body
    response.status = 400
    return false
  }

  const validations = [
    {
      condition: !patient.name?.[0]?.use,
      diagnostics: 'Missing value - \'entry/0/resource/name/0/use\'',
      type: 'missing'
    },
    {
      condition: !patient.address,
      diagnostics: 'Missing value - \'entry/0/resource/address\'',
      type: 'missing'
    },
    {
      condition: !patient.gender,
      diagnostics: 'Missing value - \'entry/0/resource/gender\'',
      type: 'missing'
    },
    {
      condition: !patient.birthDate,
      diagnostics: 'Missing value - \'entry/0/resource/birthDate\'',
      type: 'missing'
    },
    {
      condition: !request.body?.entry?.[1]?.resource?.valueQuantity?.value,
      diagnostics: 'Missing value - \'entry/1/resource/valueQuantity/value\'',
      type: 'missing'
    },
    {
      condition: typeof patient.address?.[0] !== 'object' || Array.isArray(patient.address?.[0]),
      diagnostics: `Invalid value - '${patient.address?.[0]}' in field 'entry/0/resource/address/0'`,
      type: 'invalid'
    },
    {
      condition: !patient.address?.[0].period,
      diagnostics: 'Missing value - \'address/0/period\'',
      type: 'missing'
    },
    {
      condition: !Array.isArray(patient.name?.[0]?.given) || ['O`Brien'].includes(patient.name?.[0]?.given),
      diagnostics: `Invalid value - '${patient.name?.[0]?.given}' in field 'entry/0/resource/name/0/given'`,
      type: 'invalid'
    },
    {
      condition: typeof patient.address?.[0] !== 'object' || Array.isArray(patient.address?.[0]),
      diagnostics: `Invalid value - '${patient.address?.[0]}' in field 'entry/0/resource/address/0'`,
      type: 'invalid'
    },
    {
      condition: !['male', 'female', 'unknown'].includes(patient.gender),
      diagnostics: 'Invalid value - \'other\' in field \'gender\'',
      type: 'invalid'
    },
    {
      condition: !patient.birthDate?.match(/^\d{4}-\d{2}-\d{2}$/),
      diagnostics: 'Invalid value - \'not-a-date\' in field \'birthDate\'',
      type: 'invalid'
    },
    {
      condition: !request.body?.entry?.[7]?.resource?.identifier?.[0]?.value,
      diagnostics: 'Missing value - \'entry/7/resource/identifier/0/value\'',
      type: 'missing'
    },
    {
      condition: !request.body?.entry?.[1]?.resource?.valueQuantity?.value,
      diagnostics: 'Missing value - \'entry/1/resource/valueQuantity/value\'',
      type: 'missing'
    },
    {
      condition: !(request.body?.entry?.[1]?.resource?.valueQuantity?.value >= 1000 && request.body?.entry?.[1]?.resource?.valueQuantity?.value <= 9999),
      diagnostics: `Invalid value - '${request.body?.entry?.[1]?.resource?.valueQuantity?.value}' in field 'entry/1/resource/valueQuantity/value'`,
      type: 'invalid'
    },
    {
      condition: !(patient.multipleBirthInteger >= 1 && patient.multipleBirthInteger <= 9),
      diagnostics: `Invalid value - '${patient.multipleBirthInteger}' in field 'entry/0/resource/multipleBirthInteger'`,
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
  // Find the baby patient resource (the one without an NHS number identifier)
  const patientEntry = request.body?.entry?.find(entry =>
    entry.resource?.resourceType === 'Patient' &&
    !entry.resource?.identifier?.some(id => id.system === 'https://fhir.nhs.uk/Id/nhs-number')
  )
  const requestPatient = patientEntry?.resource

  const patient = JSON.parse(JSON.stringify(NEW_PATIENT_AT_BIRTH)) // NOSONAR - structuredClone not available in Karate

  // set a new NHS number for the patient

  patient.id = '5900010775'
  patient.identifier[0].value = '5900010775'

  // name and address objects need an ID
  patient.name[0] = requestPatient.name[0]
  patient.name[0].id = generateObjectId()

  // in the address object, the line property is an array that can contain blank strings. For the response,
  // the blank strings are removed.
  const line = requestPatient.address[0].line.filter((line) => line !== '')
  patient.address[0] = requestPatient.address[0]
  patient.address[0].line = line
  patient.address[0].id = generateObjectId()

  // set the other properties
  patient.gender = requestPatient.gender
  patient.birthDate = requestPatient.birthDate

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
if (request.pathMatches('/Patient/$process-birth-details') && request.post) {
  handlePatientCreationRequest(request)
}
