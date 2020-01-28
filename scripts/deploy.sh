#!/bin/bash

set -euo pipefail

if [ $CIRCLE_BRANCH = "master" ]; then
    curl --fail -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" -H "Accept: application/json;charset=utf-8" -H "Authorization: Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0" -X POST https://login.apigee.com/oauth/token -d 'username='$APIGEE_USER'&password='$APIGEE_PASS'&grant_type=password' | jq -r .access_token > /tmp/access_token
    APIGEE_ACCESS_TOKEN=$(cat /tmp/access_token)
    curl --fail -X PUT "https://apigee.com/dapi/api/organizations/emea-demo8/specs/doc/$APIGEE_SPEC_ID/content" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN" -H 'Content-Type: text/plain' --data '@dist/patient-demographics-service-api.json'
    curl --fail -X PUT "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/apidocs/$APIGEE_PORTAL_API_ID/snapshot" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN"
    curl --fail -X POST "https://apigee.com/portals/api/sites/emea-demo8-nhsdportal/resource-entitlements/apis/$APIGEE_PORTAL_API_ID" -H "Authorization: Bearer $APIGEE_ACCESS_TOKEN" -H 'Content-Type: application/json' --data $'{"isPublic": true, "authEntitled": false, "explicitAudiences": [], "orgname": "emea-demo8"}'
    cd sandbox && npm run deploy
else
    echo "On non-master branch $CIRCLE_BRANCH, will not deploy"
fi
