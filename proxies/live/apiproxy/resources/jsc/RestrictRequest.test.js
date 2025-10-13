const jestWhen = require('jest-when');

const restrictRequestjs = './RestrictRequest.js'

const restrictRequest = () => {
    jest.resetModules();
    return require(restrictRequestjs)
}

function setupEmptyContext() {
    const fields = [
        "proxy.pathsuffix",
        "request.header.x-sync-wrapped",
        "jwt.DecodeJWT.DecodeIdToken.claim.vot",
        "jwt.DecodeJWT.DecodeIdToken.claim.nhs_number",
        "request.verb"
    ]
    global.context = {};
    global.context.getVariable = jest.fn()
    for (const field of fields){
        jestWhen.when(global.context.getVariable).calledWith(field).mockReturnValue("")
    }

    global.context.setVariable = jest.fn()
}

beforeEach(() => {
    setupEmptyContext();
})

test("Polling requests are not restricted", () => {
    const pollPath = "/_poll/123456789"
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(pollPath)

    const isSyncWrapped = "true"
    jestWhen.when(global.context.getVariable).calledWith("request.header.x-sync-wrapped").mockReturnValue(isSyncWrapped)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("P9.Cp.Cd is an allowed vector of trust", () => {
    const p9cpcdVetorOfTrust = "P9.Cp.Cd"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cpcdVetorOfTrust)
    
    const nhsNumber = "1234567890"
    const patientPath = "/Patient/" + nhsNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(patientPath)
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("P9.Cm is an allowed vector of trust", () => {
    const p9cmVetorOfTrust = "P9.Cm"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cmVetorOfTrust)
    
    const nhsNumber = "1234567890"
    const patientPath = "/Patient/" + nhsNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(patientPath)
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("P9.Cp.Ck is an allowed vector of trust", () => {
    const p9cpckVetorOfTrust = "P9.Cp.Ck"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cpckVetorOfTrust)
    
    const nhsNumber = "1234567890"
    const patientPath = "/Patient/" + nhsNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(patientPath)
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("P5.Cp.Ck is not an allowed vector of trust", () => {
    const p5cpckVetorOfTrust = "P5.Cp.Ck"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p5cpckVetorOfTrust)
    
    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(true)
})

test("Searching for Coverage using a different NHS number to NHS-Login token is not accepted", () => {
    const p9cmVetorOfTrust = "P9.Cm"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cmVetorOfTrust)

    const getVerb = "GET"
    jestWhen.when(global.context.getVariable).calledWith("request.verb").mockReturnValue(getVerb)

    const covergeSearchPathSuffix = "/Coverage"
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(covergeSearchPathSuffix)

    const nhsNumber = "1234567890"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    const differentNHSNumber = "0987654321"
    const coverageFullURL = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Coverage?subscriber%3Aidentifier=" + differentNHSNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.url").mockReturnValue(coverageFullURL)


    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(true)
})

test("Searching for Coverage using a malformed NHS number is not accepted", () => {
    const p9cmVetorOfTrust = "P9.Cm"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cmVetorOfTrust)

    const getVerb = "GET"
    jestWhen.when(global.context.getVariable).calledWith("request.verb").mockReturnValue(getVerb)

    const covergeSearchPathSuffix = "/Coverage"
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(covergeSearchPathSuffix)

    const nhsNumber = "1234567890"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    const malformedNHSNumber = nhsNumber + 'X'
    const coverageFullURL = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Coverage?subscriber%3Aidentifier=" + malformedNHSNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.url").mockReturnValue(coverageFullURL)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.invalid_coverage_search')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(true)
    expect(global.context.setVariable.mock.calls[1][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[1][1]).toBe(true)
})

test("Patient searching for their own Coverage is allowed", () => {
    const p9cmVetorOfTrust = "P9.Cm"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cmVetorOfTrust)

    const getVerb = "GET"
    jestWhen.when(global.context.getVariable).calledWith("request.verb").mockReturnValue(getVerb)

    const covergeSearchPathSuffix = "/Coverage"
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(covergeSearchPathSuffix)

    const nhsNumber = "1234567890"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(nhsNumber)

    const coverageFullURL = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Coverage?subscriber%3Aidentifier=" + nhsNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.url").mockReturnValue(coverageFullURL)
    
    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("NHS numbers for POST Coverage is not validated/restricted here", () => {
    const p9cmVetorOfTrust = "P9.Cm"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cmVetorOfTrust)

    const getVerb = "POST"
    jestWhen.when(global.context.getVariable).calledWith("request.verb").mockReturnValue(getVerb)

    const covergeSearchPathSuffix = "/Coverage"
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(covergeSearchPathSuffix)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(false)
})

test("Patient attempting to retrieve another patients record is rejected", () => {
    const p9cpcdVetorOfTrust = "P9.Cp.Cd"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(p9cpcdVetorOfTrust)
    
    const nhsNumber = "1234567890"
    const patientPath = "/Patient/" + nhsNumber
    jestWhen.when(global.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(patientPath)

    const differentNHSNumber = "9876543210"
    jestWhen.when(global.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(differentNHSNumber)

    restrictRequest()
    expect(global.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(global.context.setVariable.mock.calls[0][1]).toBe(true)
})
