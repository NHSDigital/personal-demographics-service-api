/* karate objects */
/* global context, request, response */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders */

const PATIENT_WITH_COVERAGE = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9733162892.json')

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

function initializePatientCoverageData (request) {
  const patient = JSON.parse(JSON.stringify(PATIENT_WITH_COVERAGE))

  // set coverage details for the patient

  patient.entry[0].resource.beneficiary.identifier.value = request.body.beneficiary.identifier.value
  patient.entry[0].resource.identifier[0].assigner.display = request.body.identifier[0].assigner.display
  patient.entry[0].resource.identifier[0].assigner.identifier.value = request.body.identifier[0].assigner.identifier.value
  patient.entry[0].resource.identifier[0].value = request.body.identifier[0].value
  patient.entry[0].resource.payor[0].identifier.value = request.body.payor[0].identifier.value
  patient.entry[0].resource.period.end = request.body.period.end
  patient.entry[0].resource.subscriberId = request.body.subscriberId
  return patient
}

function handlePatientCoverageRequest (request) {
  response.headers = basicResponseHeaders(request)
  response.contentType = 'application/json'
  if (postPatientRequestIsValid(request)) {
    const patient = initializePatientCoverageData(request)
    response.body = patient
    response.status = 201
  }
}

// Check if the incoming request is a POST to the /Coverage endpoint and handle accordingly
if (request.pathMatches('/Coverage') && request.post) {
  handlePatientCoverageRequest(request)
}
