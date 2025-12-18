/* eslint-disable no-var, vars-on-top */
// Apigee JavaScript runtime doesn't support ES6 features (let/const)
// Must use 'var' instead of 'const'/'let' for variable declarations
function extractCustomAttributes(json) {
    if (json) {
        var parsed = JSON.parse(json);
        // Cannot use optional chaining (?.) as Apigee JavaScript runtime doesn't support ES2020 syntax
        if (parsed && parsed.pds && parsed.pds["custom-attributes"]) {
            context.setVariable("extractedCustomAttributes", JSON.stringify(parsed.pds["custom-attributes"]))
        }
    }
}

extractCustomAttributes(context.getVariable("app.apim-app-flow-vars"))