/*
    Handler for get related person
*/
if (request.pathMatches('/Patient/{nhsNumber}/RelatedPerson') && request.get) {
    let valid = validateHeaders(request) && validateNHSNumber(request)

    if (valid) {
        response.headers = basicResponseHeaders(request)
        const nhsNumber = request.pathParams.nhsNumber
    
        if (nhsNumber == "9000000009") {
            response.body = context.read('classpath:mocks/stubs/relatedPersonResponses/related_person_90000000009.json')
        } 
        else if (nhsNumber == "9111231130") {
            response.body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json')
            response.status = 404
        }
        else if (nhsNumber == "9000000017") {
            console.log("Returning related person 9000000017")
            response.body = context.read('classpath:mocks/stubs/relatedPersonResponses/related_person_9000000017.json')
            response.status = 200
        }
        else {
            response.body = EMPTY_SEARCHSET
        }
    }
}
