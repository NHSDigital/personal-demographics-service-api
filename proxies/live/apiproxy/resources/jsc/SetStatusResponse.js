var apiproxy_revision = context.getVariable('apiproxy.revision');

var spine_response_code = context.getVariable('spineHealthcheckResponse.status.code');
var spine_response = context.getVariable('spineHealthcheckResponse.content');
var spine_request_url= context.getVariable('spineHealthcheckRequest.url');

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
    "outcome": spine_response,
    "links" : {"self": spine_request_url}
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
"releaseId" : "10485", 
"commitId": "f70bde83654790c2540621be9f1e3f40d7debdb8",
"checks" : spine_service
};


context.proxyResponse.content = JSON.stringify(response);

context.setVariable("response.header.Content-Type", "application/json");
