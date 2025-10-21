const jestWhen = require('jest-when');

setup();

const extractCustomAttributes = () => {
    jest.resetModules();
    return require("./ExtractCustomAttributes.js")
}

function setup() {
    globalThis.context = {};
    globalThis.context.getVariable = jest.fn()
}

beforeEach(() => {
    globalThis.context.setVariable = jest.fn()
})

test("custom-attributes extracted to extractedCustomAttributes", () => {
    // arrange
    const input = '{"pds": {"custom-attributes": {"custom-attr-1": "true", "custom-attr-2": "xyz", "custom-attr-3": "123"}}}';
    jestWhen.when(globalThis.context.getVariable).calledWith("app.apim-app-flow-vars").mockReturnValue(input)
    
    // act
    extractCustomAttributes()

    // assert
    expect(globalThis.context.setVariable.mock.calls[0][1]).toBe('{"custom-attr-1":"true","custom-attr-2":"xyz","custom-attr-3":"123"}')
})

test("missing pds attribute does not set extractedCustomAttributes", () => {
    // arrange
    const input = '{"custom-attributes": {"custom-attr-1": "true", "custom-attr-2": "xyz", "custom-attr-3": "123"}}';
    jestWhen.when(globalThis.context.getVariable).calledWith("app.apim-app-flow-vars").mockReturnValue(input)

    // act
    extractCustomAttributes()

    // assert
    expect(globalThis.context.setVariable.mock.calls[0]).toBeUndefined()
})

test("malformed json does not set extractedCustomAttributes", () => {
    // arrange
    const input = 'malformed:json';
    jestWhen.when(globalThis.context.getVariable).calledWith("app.apim-app-flow-vars").mockReturnValue(input)

    // act
    try {
        extractCustomAttributes()
    } catch {
    }
     
    // assert
    expect(globalThis.context.setVariable.mock.calls[0]).toBeUndefined()
})

test("empty json does not set extractedCustomAttributes", () => {
    // arrange
    const input = '';
    jestWhen.when(globalThis.context.getVariable).calledWith("app.apim-app-flow-vars").mockReturnValue(input)

    // act
    extractCustomAttributes()
     
    // assert
    expect(globalThis.context.setVariable.mock.calls[0]).toBeUndefined()
})
