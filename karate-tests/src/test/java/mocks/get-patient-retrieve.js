/*
    Stubs
*/
session.stubs = session.stubs || {
    examplePatientSmith: context.read('classpath:mocks/stubs/patientResponses/Patient.json'),
    examplePatientSmyth: context.read('classpath:mocks/stubs/patientResponses/Patient-Jayne-Smyth.json'),
    examplePatientSmythe: context.read('classpath:mocks/stubs/patientResponses/Sensitive_Patient.json'),
    examplePatientMinimal: context.read('classpath:mocks/stubs/patientResponses/Minimal_Patient.json'),
    exampleSearchPatientSmith: context.read('classpath:mocks/stubs/patientResponses/PatientSearch.json').entry[0].resource,
    exampleSearchPatientSmyth: context.read('classpath:mocks/stubs/patientResponses/PatientSearch-Jayne-Smyth.json').entry[0].resource,
    exampleSearchPatientSmythe: context.read('classpath:mocks/stubs/patientResponses/Sensitive_PatientSearch.json').entry[0].resource,
    exampleSearchPatientMinimal: context.read('classpath:mocks/stubs/patientResponses/Minimal_PatientSearch.json').entry[0].resource,
    exampleSearchPatientCompoundName: context.read('classpath:mocks/stubs/patientResponses/PatientCompoundName.json')
}

/*
    Patient objects used in pytest tests
*/
session.patients = session.patients || {
    '9000000009': context.read('classpath:stubs/patient/sandbox-patient.json'),
    '9000000025': context.read('classpath:stubs/oldSandbox/sensitive-patient.json'),
    '9693632109': context.read('classpath:stubs/patient/patient_9693632109.json')
}

/*
    Handler for get patient by NHS Number
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.get) {
    let valid = validateHeaders(request) && validateNHSNumber(request) ;

    if (valid) {
        const nhsNumber = request.pathParams.nhsNumber;
        if (typeof session.patients[nhsNumber] == 'undefined') {
            response.body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json');
            response.headers = basicResponseHeaders(request)
            response.status = 404
        } else {
            patient = session.patients[nhsNumber]
            let responseHeaders = basicResponseHeaders(request)
            responseHeaders['etag'] = `W/"${patient.meta.versionId}"`
            response.body = patient;
            response.headers = responseHeaders;
            response.status = 200;
        }    
    }
}
