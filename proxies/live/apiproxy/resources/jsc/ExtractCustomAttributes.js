function extractCustomAttributes(json) {
    if (json) {
        const parsed = JSON.parse(json);
        if (parsed?.pds?.["custom-attributes"]) {
            context.setVariable("extractedCustomAttributes", JSON.stringify(parsed.pds["custom-attributes"]))
        }
    }
}

extractCustomAttributes(context.getVariable("app.apim-app-flow-vars"))