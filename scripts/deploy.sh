#!/bin/bash

if [[ -v $APIGEE_USER ]]; then
    echo "APIGEE_USER is not set!"
    exit 1
fi

if [[ -v $APIGEE_PASS ]]; then
    echo "APIGEE_PASS is not set!"
    exit 1
fi

if [[ -v $APIGEE_SPEC_ID ]]; then
    echo "APIGEE_SPEC_ID is not set!"
    exit 1
fi

if [[ -v $APIGEE_PORTAL_API_ID ]]; then
    echo "APIGEE_PORTAL_API_ID is not set!"
    exit 1
fi


if [ $CIRCLE_BRANCH = "master" ]; then
    curl --fail -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" -H "Accept: application/json;charset=utf-8" -H "Authorization: Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0" -X POST https://login.apigee.com/oauth/token -d 'username='$APIGEE_USER'&password='$APIGEE_PASS'&grant_type=password' | jq -r .access_token > /tmp/access_token
    APIGEE_ACCESS_TOKEN=$(cat /tmp/access_token)
    curl --fail -X PUT "https://apigee.com/dapi/api/organizations/emea-demo8/specs/doc/$APIGEE_SPEC_ID/content" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN" -H 'Content-Type: text/plain' --data '@dist/patient-information-api.json'
    curl --fail -X PUT "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/apidocs/$APIGEE_PORTAL_API_ID" -H 'Authorization: Bearer $APIGEE_ACCESS_TOKEN" -H 'Content-Type: application/json' --data $'{\n  "specId": "patient-information-api-automated-latest",\n  "imageUrl": null,\n  "orgName": "emea-demo8"\n}'
    curl --fail -X PUT "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/apidocs/$APIGEE_PORTAL_API_ID/snapshot" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN"
else
    echo "On non-master branch $CIRCLE_BRANCH, will not deploy"
fi
