#!/bin/bash

if [ $CIRCLE_BRANCH = "master" ] then
    curl --fail -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" -H "Accept: application/json;charset=utf-8" -H "Authorization: Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0" -X POST https://login.apigee.com/oauth/token -d 'username='$APIGEE_USER'&password='$APIGEE_PASS'&grant_type=password' | jq -r .access_token > /tmp/access_token
    echo 'export APIGEE_ACCESS_TOKEN=$(cat /tmp/access_token)' >> $BASH_ENV
    curl --fail -X PUT 'https://apigee.com/dapi/api/organizations/emea-demo8/specs/doc/'$APIGEE_SPEC_ID'/content' -H 'Authorization: Bearer '$APIGEE_ACCESS_TOKEN'' -H 'Content-Type: text/plain' --data '@dist/patient-information-api.json'
    curl --fail -X PUT "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/apidocs/$APIGEE_PORTAL_API_ID" -H 'Authorization: Bearer '$APIGEE_ACCESS_TOKEN'' -H 'Content-Type: application/json' --data $'{\n  "specId": "patient-information-api-automated-latest",\n  "imageUrl": null,\n  "orgName": "emea-demo8"\n}'
    curl --fail -X PUT "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/apidocs/$APIGEE_PORTAL_API_ID/snapshot" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN"i $
else
    echo "On non-master branch $CIRCLE_BRANCH, will not deploy"
fi
