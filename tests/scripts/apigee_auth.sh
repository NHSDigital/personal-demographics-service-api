#!/bin/bash

echo "Getting apigee login ..."
export SSO_LOGIN_URL=https://login.apigee.com
export APIGEE_API_TOKEN=$(get_token -u $APIGEE_LOGIN)
echo $APIGEE_API_TOKEN