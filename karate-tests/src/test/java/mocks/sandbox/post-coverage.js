/* karate objects */
/* global context, request, response */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders */

/*
 * Generating valid NHS numbers on the fly isn't so easy, so we just have an array of valid numbers
 * to pick from when we need to create a new patient. When the array is exhausted, the mock server
 * should reset itself to its initial state, removing all creates and updates.
 */

const PATIENT_WITH_COVERAGE = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162868.json')

function postPatientRequestIsValid (request) {
  const diagnosticsMap = {
    missing: 'classpath:mocks/stubs/errorResponses/MISSING_VALUE.json',
    invalid: 'classpath:mocks/stubs/errorResponses/INVALID_VALUE.json'
  }
  const validations = [
    {
      condition: !request.body?.identifier,
      diagnostics: 'Missing value - \'identifier\'',
      type: 'missing'
    },
    {
      condition: !request.body?.status,
      diagnostics: 'Missing value - \'status\'',
      type: 'missing'
    },
    {
      condition: !request.body?.beneficiary,
      diagnostics: 'Missing value - \'beneficiary\'',
      type: 'missing'
    },
    {
      condition: !request.body?.subscriberId,
      diagnostics: 'Missing value - \'subscriberId\'',
      type: 'missing'
    },
    {
      condition: !request.body?.period,
      diagnostics: 'Missing value - \'period\'',
      type: 'missing'
    },
    {
      condition: !request.body?.period?.end?.match(/^\d{4}-\d{2}-\d{2}$/),
      diagnostics: 'Invalid value - \'not-a-date\' in field \'period\'',
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
  const patient = JSON.parse(JSON.stringify(PATIENT_WITH_COVERAGE))

  // set a new NHS number for the patient

  patient.entry[0].resource.beneficiary.identifier.value = request.body.beneficiary.identifier.value
  patient.entry[0].resource.identifier.assigner.display = request.body.beneficiary.identifier[0].value

  // set all other values

  return patient
}

function handlePatientCoverageRequest (request) {
  response.headers = basicResponseHeaders(request)
  response.contentType = 'application/fhir+json'
  if (postPatientRequestIsValid(request)) {
    const patient = initializePatientData(request)
    response.body = patient
    response.status = 201
  }
}

// Check if the incoming request is a POST to the /Patient endpoint and handle accordingly
if (request.pathMatches('/Coverage') && request.post) {
  handlePatientCoverageRequest(request)
}
