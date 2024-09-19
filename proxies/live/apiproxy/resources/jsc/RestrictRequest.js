var id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
var request_pathsuffix = context.getVariable('proxy.pathsuffix');
var request_path_nhs_number = request_pathsuffix.split("/")[2];
var method_is_restricted = true
var sync_wrapped = context.getVariable('request.header.x-sync-wrapped');
var vot = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.vot');
var allowed_vots = ["P9.Cp.Cd","P9.Cm","P9.Cp.Ck"];

// if (allowed_vots.indexOf(vot) > -1) {
//     method_is_restricted = false
// }

if (request_pathsuffix.split("/")[1] == "_poll" && sync_wrapped == "true"){
    method_is_restricted = false
}

if ((request_path_nhs_number == id_token_nhs_number) && (allowed_vots.indexOf(vot) > -1)) {
    method_is_restricted = false
}
context.setVariable('apigee.method_is_restricted', method_is_restricted);