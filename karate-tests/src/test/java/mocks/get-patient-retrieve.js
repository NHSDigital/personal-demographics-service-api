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
    response.headers = {
        'content-type': 'application/fhir+json',
        'etag': 'W/"1"',
        'x-request-id': request.header('x-request-id'),
        'x-correlation-id': request.header('x-correlation-id')

    };

    const nhsNumber = request.pathParams.nhsNumber;
    let validNHSNumber = validate(nhsNumber)
    const requestID = request.header('x-request-id')
    let errors = false;
    
    if (!requestID) {
        errors = true
        response.body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE_x-request-id.json')
        response.status = 400
    } else if (!isValidUUID(requestID)) {
        errors = true
        invalidValueError(X_REQUEST_ID, requestID)
    } else if (!validNHSNumber) {
        errors = true
        response.body = context.read('classpath:stubs/oldSandbox/errors/INVALID_RESOURCE_ID.json');
        response.status = 400
    }
    if (!errors) {
        if (typeof session.patients[nhsNumber] == 'undefined') {
            response.body = context.read('classpath:stubs/oldSandbox/errors/RESOURCE_NOT_FOUND.json');
            response.status = 404
        } else {
            patient = session.patients[nhsNumber]
            response.body = patient;
            response.status = 200;
        }    
    }
}
