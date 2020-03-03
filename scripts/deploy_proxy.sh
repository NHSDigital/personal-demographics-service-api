#!/bin/bash

set -o nounset errexit pipefail

# Collect the API Proxy and Hosted Target (Sandbox server)
# files into dist/apiproxy/ and deploy to Apigee

mkdir -p dist
rm -rf dist/apiproxy
cp -Rv apiproxy dist/
sed "s/PROXY_BASE_PATH/$APIGEE_BASE_PATH/g" dist/apiproxy/proxies/default.xml > dist/apiproxy/proxies/default_temp.xml
cp -f dist/apiproxy/proxies/default_temp.xml dist/apiproxy/proxies/default.xml
rm -rf dist/apiproxy/proxies/default_temp.xml
mkdir -p dist/apiproxy/resources/hosted
rsync -av --copy-links --exclude="node_modules" --filter=':- .gitignore' sandbox/ dist/apiproxy/resources/hosted
node_modules/.bin/apigeetool deployproxy --environments "$APIGEE_ENVIRONMENTS" --api "$APIGEE_APIPROXY" --directory dist/ --verbose
