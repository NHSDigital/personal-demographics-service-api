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
    globalThis.context = {};
    globalThis.context.getVariable = jest.fn()
    for (const field of fields){
        jestWhen.when(globalThis.context.getVariable).calledWith(field).mockReturnValue("")
    }

    globalThis.context.setVariable = jest.fn()
}

beforeEach(() => {
    setupEmptyContext();
})

test("Polling requests are not restricted", () => {
    const pollPath = "/_poll/123456789"
    jestWhen.when(globalThis.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(pollPath)

    const isSyncWrapped = "true"
    jestWhen.when(globalThis.context.getVariable).calledWith("request.header.x-sync-wrapped").mockReturnValue(isSyncWrapped)

    restrictRequest()
    expectMethodIsRestricted(false)
})

function expectMethodIsRestricted(value){
    expect(globalThis.context.setVariable.mock.calls[0][0]).toBe('apigee.method_is_restricted')
    expect(globalThis.context.setVariable.mock.calls[0][1]).toBe(value)
}

function setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb = undefined, differentNHSNumber = undefined, coverageFullURL = undefined){
    jestWhen.when(globalThis.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.vot").mockReturnValue(vectorOfTrust);
    jestWhen.when(globalThis.context.getVariable).calledWith("proxy.pathsuffix").mockReturnValue(searchPathSuffix);
    jestWhen.when(globalThis.context.getVariable).calledWith("jwt.DecodeJWT.DecodeIdToken.claim.nhs_number").mockReturnValue(differentNHSNumber === undefined ? nhsNumber : differentNHSNumber);

    if(getVerb !== undefined){
        jestWhen.when(globalThis.context.getVariable).calledWith("request.verb").mockReturnValue(getVerb);
    }

    if(coverageFullURL !== undefined){
        jestWhen.when(globalThis.context.getVariable).calledWith("proxy.url").mockReturnValue(coverageFullURL);
    }
}

describe("P* vectors of trust", () => {
    let searchPathSuffix = "/Coverage";
    let nhsNumber = "1234567890";
    let vectorOfTrust = "P9.Cm"; // default for tests in this describe block
    let getVerb = "GET"; // default for tests in this describe block
    let differentNHSNumber = "0987654321";
    let coverageFullURL = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Coverage?subscriber%3Aidentifier=";

    beforeEach(() => {
        searchPathSuffix = "/Coverage";
        nhsNumber = "1234567890";
        vectorOfTrust = "P9.Cm";
        getVerb = "GET";
        differentNHSNumber = "0987654321";
        coverageFullURL = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Coverage?subscriber%3Aidentifier=";
    });

    test("P9.Cm is an allowed vector of trust", () => {
        searchPathSuffix = "/Patient/" + nhsNumber;
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix);

        restrictRequest();
        expectMethodIsRestricted(false);
    });

    test("Searching for Coverage using a different NHS number to NHS-Login token is not accepted", () => {       
        coverageFullURL = coverageFullURL + differentNHSNumber;
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb, undefined, coverageFullURL);

        restrictRequest();
        expectMethodIsRestricted(true);
    });

    test("Searching for Coverage using a malformed NHS number is not accepted", () => {
        const malformedNHSNumber = nhsNumber + 'X';
        coverageFullURL = coverageFullURL + malformedNHSNumber;
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb, coverageFullURL);
        
        restrictRequest();
        expect(globalThis.context.setVariable.mock.calls[0][0]).toBe('apigee.invalid_coverage_search');
        expect(globalThis.context.setVariable.mock.calls[0][1]).toBe(true);
        expect(globalThis.context.setVariable.mock.calls[1][0]).toBe('apigee.method_is_restricted');
        expect(globalThis.context.setVariable.mock.calls[1][1]).toBe(true);
    });

    test("Patient searching for their own Coverage is allowed", () => {
        let coverageFullURLWithNHSNumber = coverageFullURL + nhsNumber;

        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb, undefined ,coverageFullURLWithNHSNumber);

        restrictRequest();
        expectMethodIsRestricted(false);
    });

    test("NHS numbers for POST Coverage is not validated/restricted here", () => {
        getVerb = "POST";
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb);

        restrictRequest();
        expectMethodIsRestricted(false);
    });

    test("P9.Cp.Ck is an allowed vector of trust", () => {
        vectorOfTrust = "P9.Cp.Ck";
        searchPathSuffix = "/Patient/" + nhsNumber;
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix);

        restrictRequest();
        expectMethodIsRestricted(false);
    });

    test("P5.Cp.Ck is not an allowed vector of trust", () => {
        vectorOfTrust = "P5.Cp.Ck";
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix);
        
        restrictRequest();
        expectMethodIsRestricted(true);
    });

    test("P9.Cp.Cd is an allowed vector of trust", () => {
        vectorOfTrust = "P9.Cp.Cd";
        searchPathSuffix = "/Patient/" + nhsNumber;
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb);

        restrictRequest();
        expectMethodIsRestricted(false);
    });

    test("Patient attempting to retrieve another patients record is rejected", () => {
        vectorOfTrust = "P9.Cp.Cd";
        searchPathSuffix = "/Patient/" + nhsNumber;
        getVerb = undefined;
        differentNHSNumber = "9876543210";
        setupContextOverrides(nhsNumber, vectorOfTrust, searchPathSuffix, getVerb, differentNHSNumber);

        restrictRequest();
        expectMethodIsRestricted(true);
    });
});