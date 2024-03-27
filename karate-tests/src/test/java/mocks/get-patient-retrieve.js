/*
    Our patients "database" for the get by NHS Number requests :-)
*/
session.patients = session.patients || {
    '9000000009': context.read('classpath:mocks/stubs/patientResponses/patient_9000000009.json'),
    '9000000025': context.read('classpath:mocks/stubs/patientResponses/patient_9000000025.json'),
    '9000000033': context.read('classpath:mocks/stubs/patientResponses/patient_9000000033.json'),
    '9693632109': context.read('classpath:mocks/stubs/patientResponses/patient_9693632109.json')
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
