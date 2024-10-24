/*
    Stubbed responses used by the different mocks
*/

/* eslint-disable no-unused-vars */
/* global context, session */

const SEARCH_PATIENT_9000000009 = context.read('classpath:mocks/stubs/searchResponses/search_patient_9000000009.json')
const SEARCH_PATIENT_9000000017 = context.read('classpath:mocks/stubs/searchResponses/search_patient_9000000017.json')
const RESTRICTED_PATIENT_SEARCH = context.read('classpath:mocks/stubs/searchResponses/search_patient_9000000025.json')
const EMPTY_SEARCHSET = { resourceType: 'Bundle', type: 'searchset', total: 0 }

const SIMPLE_SEARCH = {
  resourceType: 'Bundle', type: 'searchset', total: 1, entry: [{ fullUrl: 'https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009', search: { score: 1 }, resource: SEARCH_PATIENT_9000000009 }]
}
const WILDCARD_SEARCH = {
  resourceType: 'Bundle',
  type: 'searchset',
  total: 2,
  entry: [
    { fullUrl: 'https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009', search: { score: 0.8343 }, resource: SEARCH_PATIENT_9000000009 },
    { fullUrl: 'https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000017', search: { score: 0.8343 }, resource: SEARCH_PATIENT_9000000017 }
  ]
}
const FUZZY_SEARCH_PATIENT_17 = {
  resourceType: 'Bundle', type: 'searchset', total: 1, entry: [{ fullUrl: 'https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000017', search: { score: 0.8976 }, resource: SEARCH_PATIENT_9000000017 }]
}

/*
    Our patients "database"
*/
session.patients = session.patients || {
  5900043320: context.read('classpath:mocks/stubs/patientResponses/patient_5900043320.json'),
  5900046192: context.read('classpath:mocks/stubs/patientResponses/patient_5900046192.json'),
  5900056449: context.read('classpath:mocks/stubs/patientResponses/patient_5900056449.json'),
  5900056597: context.read('classpath:mocks/stubs/patientResponses/patient_5900056597.json'),
  5900057208: context.read('classpath:mocks/stubs/patientResponses/patient_5900057208.json'),
  5900059073: context.read('classpath:mocks/stubs/patientResponses/patient_5900059073.json'),
  5900059243: context.read('classpath:mocks/stubs/patientResponses/patient_5900059243.json'),
  5900059332: context.read('classpath:mocks/stubs/patientResponses/patient_5900059332.json'),
  9000000009: context.read('classpath:mocks/stubs/patientResponses/patient_9000000009.json'),
  9000000025: context.read('classpath:mocks/stubs/patientResponses/patient_9000000025.json'),
  9000000033: context.read('classpath:mocks/stubs/patientResponses/patient_9000000033.json'),
  9693632109: context.read('classpath:mocks/stubs/patientResponses/patient_9693632109.json'),
  9733162043: context.read('classpath:mocks/stubs/patientResponses/patient_9733162043.json')
}
