/*
    Handler for get patient by NHS Number
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.get) {  
    let valid = validateHeaders(request) && validateNHSNumber(request) && validatePatientExists(request)
    if (valid) {
        patient = session.patients[request.pathParams.nhsNumber]
        let responseHeaders = basicResponseHeaders(request)
        responseHeaders['etag'] = `W/"${patient.meta.versionId}"`
        response.body = patient
        response.headers = responseHeaders
        response.status = 200
    }
}
