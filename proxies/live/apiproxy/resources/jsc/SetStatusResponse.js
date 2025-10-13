const apiproxy_revision = context.getVariable('apiproxy.revision');

const spine_response_code = context.getVariable('spineHealthcheckResponse.status.code');
const spine_response = context.getVariable('spineHealthcheckResponse.content');
const spine_request_url = context.getVariable('spineHealthcheckRequest.url');

const spine_request_has_failed = context.getVariable("servicecallout.ServiceCallout.CallSpineHealthcheck.failed");

let spine_status = "fail";

if(spine_response_code/ 100 == 2){
    spine_status = "pass";
}

let timeout = "false";

if(spine_response_code === null && spine_request_has_failed){
    timeout = "true";
}



const spine_service = {
"spine:status" : [
    {
    "status": spine_status, 
    "timeout" : timeout,
    "responseCode" : spine_response_code,
    "outcome": spine_response,
    "links" : {"self": spine_request_url}
   }]
};

let apigee_status = "pass";

if(spine_status != "pass"){
    apigee_status = "fail";
}



const response = {  
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
