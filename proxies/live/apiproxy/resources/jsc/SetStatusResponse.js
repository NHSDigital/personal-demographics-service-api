
var apiproxy_revision = context.getVariable('apiproxy.revision');
var spine_response_code = context.getVariable('response.status.code');
var spine_response = context.getVariable('response.content');

var spine_status = "fail";

if(spine_response_code/ 100 == 2){
    spine_status = "pass";
}

var spine_service = {
"spine:status" : [
    {
    "status": spine_status, 
    "timeout" : "false",
    "responseCode" : spine_response_code,
    "outcome": spine_response
   }]
};

var apigee_status = "pass";

if(spine_status != "pass"){
    apigee_status = "fail";
}



var response = { 
"status" : apigee_status,
"version" : "personal-demographics-pr-394" ,
"revision" : apiproxy_revision, 
"releaseId" : "10111", 
"commitId": "911d8dee679a7cd5ab0d337e10fcaa9f76ff75f8",
"checks" : spine_service
};


context.proxyResponse.content = JSON.stringify(response);

context.setVariable("response.header.Content-Type", "application/json");

