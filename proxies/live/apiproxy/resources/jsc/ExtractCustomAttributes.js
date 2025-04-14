function extractCustomAttributes(json) {
    if (json) {
        try {
            var parsed = JSON.parse(json);
            if (parsed.pds && parsed.pds["custom-attributes"]) {
                context.setVariable("extractedCustomAttributes", JSON.stringify(parsed.pds["custom-attributes"]))
            }
        } catch (e) {
            context.setVariable("extractedCustomAttributesException", e)
        }
    }
}

extractCustomAttributes(context.getVariable("app.apim-app-flow-vars"))