setup();
const { extractCustomAttributes } = require("./ExtractCustomAttributes.js");

function setup() {
    global.context = {};
    global.context.getVariable = jest.fn()
}

beforeEach(() => {
    global.context.setVariable = jest.fn()
})

test("custom-attributes extracted to JSON", () => {
    // arrange
    const input = '{"pds": {"custom-attributes": {"custom-attr-1": "true", "custom-attr-2": "xyz", "custom-attr-3": "123"}}}';

    // act
    extractCustomAttributes(input)

    // assert
    expect(global.context.setVariable.mock.calls[0][1]).toBe('{"custom-attr-1":"true","custom-attr-2":"xyz","custom-attr-3":"123"}')
})

test("missing pds attribute not extracted to JSON", () => {
    // arrange
    const input = '{"custom-attributes": {"custom-attr-1": "true", "custom-attr-2": "xyz", "custom-attr-3": "123"}}';

    // act
    extractCustomAttributes(input)

    // assert
    expect(global.context.setVariable.mock.calls[0]).toBeUndefined()
})

test("malformed json not extracted to JSON", () => {
    // arrange
    const input = 'malformed:json';

    // act
    extractCustomAttributes(input)

    // assert
    expect(global.context.setVariable.mock.calls[0]).toBeUndefined()
})
