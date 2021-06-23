var id_token_nhs_number = context.getVariable('jwt.DecodeJWT.DecodeIdToken.claim.nhs_number');
var request_pathsuffix = context.getVariable('proxy.pathsuffix');
var request_path_nhs_number = request_pathsuffix.split("/")[2];
var method_is_restricted = true

if (request_pathsuffix.split("/")[1] == "_poll"){
    method_is_restricted = false
}

if (request_path_nhs_number == id_token_nhs_number){
    method_is_restricted = false
}
context.setVariable('apigee.method_is_restricted', method_is_restricted);