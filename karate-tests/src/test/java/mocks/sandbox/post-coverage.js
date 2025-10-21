/* karate objects */
/* global context, request, response */

/* functions defined in supporting-functions.js */
/* global basicResponseHeaders, setResourceVersionMismatchError, setPreconditionFailedError, setUnsupportedServiceError, NO_IF_MATCH_HEADER,
 validateHeaders */

/*
    Validate the headers specific to patching a patient
*/
function validatePostCoverageHeaders (request) {
  const ifMatchHeader = request.header('if-match')
  const contentType = request.header('content-type')
  if (!ifMatchHeader) {
    setPreconditionFailedError(request, NO_IF_MATCH_HEADER)
    return false
  }
  if (!contentType) {
    setUnsupportedServiceError()
    response.headers = basicResponseHeaders(request)
    return false
  }
  return true
}

function buildPostCoverageResponseHeaders (request, patient) {
  return {
    'content-type': 'application/fhir+json',
    etag: `W/"${patient.meta.versionId}"`,
    'x-request-id': request.header('x-request-id')
  }
}

const PATIENT_WITH_COVERAGE = context.read('classpath:mocks/stubs/coverageResponses/patient_with_coverage_9000000009.json')

function postCoverageRequestIsValid (request) {
  const diagnosticsMap = {
    missing: 'classpath:mocks/stubs/errorResponses/MISSING_VALUE.json',
    invalid: 'classpath:mocks/stubs/errorResponses/INVALID_VALUE.json'
  }
  const validations = [
    {
      condition: !request.body?.identifier[0].value,
      diagnostics: 'Missing value - \'identifier/0/value\'',
      type: 'missing'
    },
    {
      condition: !request.body?.status,
      diagnostics: 'Missing value - \'status\'',
      type: 'missing'
    },
    {
      condition: !request.body?.subscriber.identifier.value,
      diagnostics: 'Missing value - \'subscriber/identifier/value\'',
      type: 'missing'
    },
    {
      condition: !request.body?.beneficiary.identifier.value,
      diagnostics: 'Missing value - \'beneficiary/identifier/value\'',
      type: 'missing'
    },
    {
      condition: !request.body?.period,
      diagnostics: 'Missing value - \'period\'',
      type: 'missing'
    },
    {
      condition: !request.body?.period?.end?.match(/^\d{4}-(0[1-9]|1[0-2])-\d{2}$/),
      diagnostics: 'Invalid value - \'not-a-date\' in field \'period\'',
      type: 'invalid'
    },
    {
      condition: request.body?.identifier?.[0]?.value &&
      (!/^[a-zA-Z0-9\-,/:'. ]+$/.test(request.body?.identifier[0].value.trim()) ||
      request.body.identifier[0].value.trim().length > 25),
      diagnostics: `Invalid value - '${request.body?.identifier[0].value}' in field 'identifier/value'`,
      type: 'invalid'
    },
    {
      condition: request.body?.beneficiary.identifier.value &&
      (!/^[a-zA-Z0-9\-,/:'. ]+$/.test(request.body?.beneficiary.identifier.value.trim()) ||
      request.body?.beneficiary.identifier.value.trim().length > 25),
      diagnostics: `Invalid value - '${request.body?.beneficiary.identifier.value}' in field 'beneficiary/identifier/value'`,
      type: 'invalid'
    },
    {
      condition: request.body?.payor[0].identifier?.value &&
      (!/^[a-zA-Z0-9\-,/:'. ]+$/.test(request.body?.payor[0].identifier?.value.trim()) ||
      request.body?.payor[0].identifier?.value.trim().length > 30),
      diagnostics: `Invalid value - '${request.body?.payor[0].identifier}' in field 'Institution id'`,
      type: 'invalid'
    },
    {
      condition: request.body?.status !== 'active',
      diagnostics: `Invalid value - '${request.body?.status}' in field 'status'`,
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

function initializePatientCoverageData (request, patient) {
  // set coverage details for the patient

  patient.entry[0].resource.beneficiary.identifier.value = request.body.beneficiary.identifier.value
  patient.entry[0].resource.identifier[0].assigner.identifier.value = request.body.identifier[0].assigner.identifier.value
  patient.entry[0].resource.identifier[0].value = request.body.identifier[0].value
  patient.entry[0].resource.payor[0].identifier.value = request.body.payor[0].identifier.value
  patient.entry[0].resource.period.end = request.body.period.end
  patient.entry[0].resource.subscriber.identifier.value = request.body.subscriber.identifier.value
  patient.meta.versionId = (Number.parseInt(patient.meta.versionId) + 1).toString()
  return patient
}

function handlePatientCoverageRequest (request) {
  response.headers = basicResponseHeaders(request)
  response.contentType = 'application/json'
  const isRequestHeadersValid = validatePostCoverageHeaders(request) && validateHeaders(request)
  if (isRequestHeadersValid) {
    if (postCoverageRequestIsValid(request)) {
      const originalPatient = structuredClone(PATIENT_WITH_COVERAGE)
      if (request.header('if-match') !== `W/"${originalPatient.meta.versionId}"`) {
        return setResourceVersionMismatchError(request)
      }
      const patientCoverage = initializePatientCoverageData(request, originalPatient)
      response.headers = buildPostCoverageResponseHeaders(request, patientCoverage)
      response.body = patientCoverage
      response.status = 201
    }
  }
}

// Check if the incoming request is a POST to the /Coverage endpoint and handle accordingly
if (request.pathMatches('/Coverage') && request.post) {
  handlePatientCoverageRequest(request)
}
