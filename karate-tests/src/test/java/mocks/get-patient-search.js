/*
    Stubs
*/
session.stubs = session.stubs || {
    examplePatientSmith: context.read('classpath:mocks/stubs/searchResponses/Patient.json'),
    examplePatientSmyth: context.read('classpath:mocks/stubs/searchResponses/Patient-Jayne-Smyth.json'),
    examplePatientSmythe: context.read('classpath:mocks/stubs/searchResponses/Sensitive_Patient.json'),
    examplePatientMinimal: context.read('classpath:mocks/stubs/searchResponses/Minimal_Patient.json'),
    exampleSearchPatientSmith: context.read('classpath:mocks/stubs/searchResponses/PatientSearch.json').entry[0].resource,
    exampleSearchPatientSmyth: context.read('classpath:mocks/stubs/searchResponses/PatientSearch-Jayne-Smyth.json').entry[0].resource,
    exampleSearchPatientSmythe: context.read('classpath:mocks/stubs/searchResponses/Sensitive_PatientSearch.json').entry[0].resource,
    exampleSearchPatientMinimal: context.read('classpath:mocks/stubs/searchResponses/Minimal_PatientSearch.json').entry[0].resource,
    exampleSearchPatientCompoundName: context.read('classpath:mocks/stubs/searchResponses/PatientCompoundName.json')
}


/*
    Handler for search Patient functionality
*/
if (request.pathMatches('/Patient') && request.get) {
    response.headers = {
        'x-request-id': request.header('x-request-id'),
        'x-correlation-id': request.header('x-correlation-id')
    };
    
    const paramsCount = Object.keys(request.params).length
    let family = getParam(request, 'family')
    console.log("family: " + family)
    let gender = getParam(request, 'gender')
    let birthDate = getParam(request, 'birthdate')
    console.log("birthDate: " + birthDate)
    let phone = getParam(request, 'phone')
    const email = getParam(request, 'email')
    const fuzzyMatch = getParam(request, '_fuzzy-match')
    const exactMatch = getParam(request, '_exact-match')
    const history = getParam(request, 'history')
    const maxResults = getParam(request, '_max-results')
    const given = getParam(request, 'given')
    const deathDate = getParam(request, 'death-date')
    const postalCode = getParam(request, 'address-postcode')
    const gp = getParam(request, 'general-practitioner')

    const requestID = request.header('x-request-id')
    
    if (!requestID) {
        response.body = context.read('classpath:stubs/errorResponses/MISSING_VALUE_x-request-id.json')
        response.status = 400
    } else if (!isValidUUID(requestID)) {
        let body = context.read('classpath:stubs/errorResponses/INVALID_VALUE_x-request-id.json')
        body['issue'][0]['diagnostics'] = `Invalid value - '${request.header('x-request-id')}' in header 'X-Request-ID'`
        response.body = body
        response.status = 400
    }
    // no params
    else if (paramsCount == 0) {
        console.log("*********no params*********")
        const diagnostics = "Not enough search parameters were provided for a valid search, you must supply family and birthDate as a minimum and only use recognised parameters from the api catalogue."
        let body = context.read('classpath:stubs/patient/errorResponses/missing_value.json')
        body["issue"][0]["diagnostics"] = diagnostics
        response.body = body
        response.status = 400
    }
    // email wrong
    else if (email=="janet.smythe@example.com") {
        console.log("*********email=='janet.smythe@example.com'*********")
        returnEmptyBundle()
    }
    // "restricted (sensitive) patient search"
    else if (family=="Smythe") {
        console.log("*********family=='Smythe'*********")
        returnBundle('JanetSmythe_bundle.json')
    }
    // multiparam requests
    else if (fuzzyMatch=="false") {
        console.log("*********Fuzzy match = false*********")
        //  && exactMatch=="false" && history=="true" && maxResults=="1" && family=="Smith" && gender=="female" && birthDate=="eq2010-10-22"
        if (
           phone=="01632960587" && email=="jane.smith@example.com" 
        ) {
            returnBundle('JaneSmith_bundle.json')
        } else {
            // TODO: Find out why this diagnostics message doesn't make much sense to me - need to provide BOTH phone and email?
            const diagnostics = "Not enough search parameters were provided for a valid search, you must supply family and birthDate as a minimum and only use recognised parameters from the api catalogue."
            returnMissingValueError(diagnostics)
        }
    }
    // fuzzy match = true
    else if (fuzzyMatch=="true") {
        console.log("*********Fuzzy match = true*********")
        if (email=="jane.smith@example.com") {
            console.log("******email=jane.smith*********")
            returnBundle("JaneSmith_bundle.json")
        }
        else if (birthDate=="2010-10-22") {
            console.log("******birthDate='2010-10-22'*********")
            // TODO a bit strange - the fuzzy match mocking returns this result, even though I think the search would also return Jane Smith in reality 
            // full query params are {"family":"Smith","given":"jane","gender":"female","birthdate":"2010-10-22","_fuzzy-match":True}
            returnBundle('JayneSmythe_bundle.json') }
            // wildcard searches
        else if (family=="sm*" && gender=="female" && birthDate=="eq2010-10-22") {
            console.log("*********Wildcard searches*********")
            // search with limited results
            if (maxResults=="1" && !email) {
                // - Search with limited results
                // - Search with limited results inc phone
                returnTooManyMatchesError()
            } else if (maxResults=="1" && email=="janet.smythe@example.com") {
                // - Search with limited results inc email
                returnEmptyBundle()
            } else if (phone=="01632960587" || email=="jane.smith@example.com") {
                returnBundle("JaneSmith_bundle.json")
            } else {
                returnBundle('JaneSmith_JanetSmythe_bundle.json')
            }
        }
// else {
//             // covers 4 scenarios, since they're all have the same result:
//             // - Fuzzy search
//             // - Fuzzy search including phone
//             // - Fuzzy search including email
//             // - Fuzzy search including phone and email
//             returnBundle('JaneSmith_bundle.json')
//         }
    }
    // simpler requests
    else if (family=="smith" && gender=="female") {
        console.log("*********Simpler requests*********")
        if (phone=="0121111111" || email=="deb.trotter@example.com") { returnEmptyBundle() }
        else if (
            birthDate=="ge2010-10-21,le2010-10-23" || 
            birthDate=="eq2010-10-22" && phone=="01632960587" ||
            birthDate=="eq2010-10-22" && email=="jane.smith@example.com" ||
            birthDate=="eq2010-10-22" && phone=="01632960587" && email=="jane.smith@example.com" ||
            birthDate=="eq2010-10-22") {
                returnBundle('JaneSmith_bundle.json')
            }  
        else if (birthDate) { validateDate(birthDate, "birthdate") }
        else if (deathDate) { validateDate(deathDate, "death-date") }
    }
    // wildcard searches
    else if (family=="sm*" && gender=="female" && birthDate=="eq2010-10-22") {
        console.log("*********Wildcard searches*********")
        // search with limited results
        if (maxResults=="1" && !email) {
            // - Search with limited results
            // - Search with limited results inc phone
            returnTooManyMatchesError()
        } else if (maxResults=="1" && email=="janet.smythe@example.com") {
            // - Search with limited results inc email
            returnEmptyBundle()
        } else if (phone=="01632960587" || email=="jane.smith@example.com") {
            returnBundle("JaneSmith_bundle.json")
        } else {
            returnBundle('JaneSmith_JanetSmythe_bundle.json')
        }
    }
    // no search results found
    else {
        returnEmptyBundle()
    }
}