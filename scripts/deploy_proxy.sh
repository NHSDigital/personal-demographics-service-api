#!/bin/bash

set -o nounset errexit pipefail

# Collect the API Proxy and Hosted Target (Sandbox server)
# files into build/apiproxy/ and deploy to Apigee

./build_proxy.sh
node_modules/.bin/apigeetool deployproxy --environments "$APIGEE_ENVIRONMENTS" --api "$APIGEE_APIPROXY" --directory "build/proxies/$PROXY_TYPE/apiproxy" --verbose
