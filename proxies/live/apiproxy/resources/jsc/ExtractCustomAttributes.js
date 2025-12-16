function extractCustomAttributes(json) {
    if (json) {
        const parsed = JSON.parse(json);
        // Cannot use optional chaining (?.) as Apigee JavaScript runtime doesn't support ES2020 syntax
        // eslint-disable-next-line @typescript-eslint/prefer-optional-chain
        if (parsed && parsed.pds && parsed.pds["custom-attributes"]) {
            context.setVariable("extractedCustomAttributes", JSON.stringify(parsed.pds["custom-attributes"]))
        }
    }
}

extractCustomAttributes(context.getVariable("app.apim-app-flow-vars"))