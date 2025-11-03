function is_request_restricted() {
    const splitPathsuffix = context.getVariable('proxy.pathsuffix').split("/");
    const fullUrl = context.getVariable('proxy.url')

    // Ignore polling
    const sync_wrapped = context.getVariable('request.header.x-sync-wrapped');
    if (splitPathsuffix[1] == "_poll" && sync_wrapped == "true"){
        return false
    }

    // Ensure correct vector of trust
    const allowed_vots = ["P9.Cp.Cd","P9.Cm","P9.Cp.Ck"];
    const vot_on_request = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.vot');
    if (allowed_vots.includes(vot_on_request)) {
        return true
    }

    const id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
    const coverageRegex = new RegExp(/Coverage\?subscriber%3Aidentifier=\d{10}$/)
    if (splitPathsuffix[1] == "Coverage"){
        const httpVerb = context.getVariable('request.verb');
        if (httpVerb === "POST") {
            return false
        }
        if (!coverageRegex.test(fullUrl)) {
            context.setVariable('apigee.invalid_coverage_search', true);
            return true
        }
        if (fullUrl.slice(-10) != id_token_nhs_number){
            return true
        }
        return false
    }

    const request_path_nhs_number = splitPathsuffix[2];
    if ((request_path_nhs_number != id_token_nhs_number)) {
        return true
    }

    return false
}

var method_is_restricted = is_request_restricted();
context.setVariable('apigee.method_is_restricted', method_is_restricted);