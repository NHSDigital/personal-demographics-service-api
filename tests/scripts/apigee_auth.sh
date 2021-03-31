#!/bin/bash

export SSO_LOGIN_URL=https://login.apigee.com
export APIGEE_API_TOKEN=$(get_token -u $APIGEE_LOGIN)