function is_request_restricted() {
    var fullPathSuffix = context.getVariable('proxy.pathsuffix')
    var splitPathsuffix = context.getVariable('proxy.pathsuffix').split("/");

    // Ignore polling
    var sync_wrapped = context.getVariable('request.header.x-sync-wrapped');
    if (splitPathsuffix[1] == "_poll" && sync_wrapped == "true"){
        return false
    }

    // Ensure correct vector of trust
    var allowed_vots = ["P9.Cp.Cd","P9.Cm","P9.Cp.Ck"];
    var vot_on_request = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.vot');
    if (allowed_vots.indexOf(vot_on_request) == -1) {
        return true
    }

    // If GET coverage
    var id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
    var coverageRegex = new RegExp(/^Coverage\?beneficiary:identifier=[0-9]{10}$/)
    if (splitPathsuffix[1] == "Coverage"){
        if (!coverageRegex.test(fullPathSuffix)){
            return true // TODO: Make sure the error is around the path not being expected
        } else if (fullPathSuffix.slice(-10) != id_token_nhs_number){
            return true 
        }
    }

    var request_path_nhs_number = request_pathsuffix.split("/")[2];
    var id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
    if ((request_path_nhs_number == id_token_nhs_number)) {
        return false
    }

    return true
}

var method_is_restricted = is_request_restricted();
context.setVariable('apigee.method_is_restricted', method_is_restricted);