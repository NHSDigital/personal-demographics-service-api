/* eslint-disable no-var, vars-on-top */
// Apigee JavaScript runtime doesn't support ES6 features (let/const)
// Must use 'var' instead of 'const'/'let' for variable declarations
function is_request_restricted() {
    var splitPathsuffix = context.getVariable('proxy.pathsuffix').split("/");
    var fullUrl = context.getVariable('proxy.url')

    // Ignore polling
    var sync_wrapped = context.getVariable('request.header.x-sync-wrapped');
    if (splitPathsuffix[1] == "_poll" && sync_wrapped == "true"){
        return false
    }

    // Ensure correct vector of trust
    var allowed_vots = ["P9.Cp.Cd","P9.Cm","P9.Cp.Ck"];
    var vot_on_request = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.vot');
    // eslint-disable-next-line unicorn/prefer-includes <<< can be removed when Apigee supports ES2020
    if (allowed_vots.indexOf(vot_on_request) === -1) {
        return true
    }

    var id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
    var coverageRegex = new RegExp(/Coverage\?subscriber%3Aidentifier=\d{10}$/)
    if (splitPathsuffix[1] == "Coverage"){
        var httpVerb = context.getVariable('request.verb');
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

    var request_path_nhs_number = splitPathsuffix[2];
    if ((request_path_nhs_number != id_token_nhs_number)) {
        return true
    }

    return false
}

var method_is_restricted = is_request_restricted();
context.setVariable('apigee.method_is_restricted', method_is_restricted);