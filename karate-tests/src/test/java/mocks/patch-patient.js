function buildResponseHeaders(request, patient) {
    return {
        'content-type': 'application/fhir+json',
        'etag': `W/"${patient.meta.versionId}"`,
        'x-request-id': request.header('x-request-id'),
        'x-correlation-id': request.header('x-correlation-id')
    };
}


function patchPatient(originalPatient, requestBody) {
    let newPatient = JSON.parse(JSON.stringify(originalPatient));
    for(let i = 0; i < requestBody.patches.length; i++) {
        let patch = requestBody.patches[i];
        if (patch.op == 'add' && patch.path === '/name/-') {
            newPatient.name.push(patch.value);
        }
        if (patch.op == 'replace' && patch.path === '/name/0/given/0') {
            newPatient.name[0].given[0] = patch.value;
        }
        if (patch.op == 'replace' && patch.path === '/gender') {
            newPatient.gender = patch.value;
        }
        if (patch.op == 'remove' && patch.path === '/name/0/suffix/0') {
            newPatient.name[0].suffix.splice(0, 1);
        }
    }
    newPatient.meta.versionId = (parseInt(newPatient.meta.versionId) + 1);
    return newPatient;
}

/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {

    const nhsNumber = request.pathParams.nhsNumber;
    let validNHSNumber = validate(nhsNumber)
    const requestID = request.header('x-request-id')
    
    if (!requestID) {
        response.body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE_x-request-id.json')
        response.status = 400
    } else if (!isValidUUID(requestID)) {
        let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE_x-request-id.json')
        body['issue'][0]['diagnostics'] = `Invalid value - '${request.header('x-request-id')}' in header 'X-Request-ID'`
        response.body = body
        response.status = 400
    } else if (!validNHSNumber) {
        response.body = context.read('classpath:stubs/oldSandbox/errors/INVALID_RESOURCE_ID.json');
        response.status = 400
    } else {
        if (typeof session.patients[nhsNumber] == 'undefined') {
            response.body = context.read('classpath:stubs/oldSandbox/errors/RESOURCE_NOT_FOUND.json');
            response.status = 404
        } else {
            originalPatient = session.patients[nhsNumber]
            newPatient = patchPatient(originalPatient, request.body);
            session.patients[nhsNumber] = newPatient;
            response.headers = buildResponseHeaders(request, newPatient);
            response.body = newPatient;
            response.status = 200;
        }    
    }
}
