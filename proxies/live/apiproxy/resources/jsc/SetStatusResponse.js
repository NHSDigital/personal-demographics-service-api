var apiproxy_revision = context.getVariable('apiproxy.revision');

var spine_response_code = context.getVariable('spineHealthcheckResponse.status.code');
var spine_response = context.getVariable('spineHealthcheckResponse.content');
var spine_request_url = context.getVariable('spineHealthcheckRequest.url');

var spine_request_has_failed = context.getVariable("servicecallout.ServiceCallout.CallSpineHealthcheck.failed");

var spine_status = "fail";

if(spine_response_code/ 100 == 2){
    spine_status = "pass";
}

timeout = "false";

if(spine_response_code === null && spine_request_has_failed){
    timeout = "true";
}



var spine_service = {
"spine:status" : [
    {
    "status": spine_status, 
    "timeout" : timeout,
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
"version" : "{{ DEPLOYED_VERSION }}" ,
"revision" : apiproxy_revision, 
"releaseId" : "{{ RELEASE_RELEASEID }}", 
"commitId": "{{ SOURCE_COMMIT_ID }}",
"checks" : spine_service
};

context.setVariable("status.response", JSON.stringify(response));
context.setVariable("response.content", JSON.stringify(response));
context.setVariable("response.header.Content-Type", "application/json");
