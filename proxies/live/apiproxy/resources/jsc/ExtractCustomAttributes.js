var customAttributeValue = context.getVariable("app.apim-app-flow-vars");

if (customAttributeValue) {
    try {
        var parsed = JSON.parse(customAttributeValue);
        if (parsed.pds && parsed.pds["custom-attributes"]) {
            context.setVariable("extractedCustomAttributes", JSON.stringify(parsed.pds["custom-attributes"]))
        }
    } catch (e) {
        context.setVariable("extractedCustomAttributes", "unknown");
    }
}