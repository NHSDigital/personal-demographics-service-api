#!/bin/bash

set -o nounset errexit pipefail

# Collect the API Proxy and Hosted Target (Sandbox server)
# files into dist/apiproxy/ and deploy to Apigee

mkdir -p dist
rm -rf dist/apiproxy
cp -R apiproxy/ dist/
mkdir -p dist/apiproxy/resources/hosted/mocks
cp sandbox/*.js sandbox/*.json sandbox/*.yaml dist/apiproxy/resources/hosted/
cp -L sandbox/mocks/*.json dist/apiproxy/resources/hosted/mocks/
node_modules/.bin/apigeetool deployproxy --environments "$APIGEE_ENVIRONMENTS" --api "$APIGEE_APIPROXY" --directory dist/ --verbose
