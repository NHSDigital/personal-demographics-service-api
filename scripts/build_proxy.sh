#!/bin/bash

set -o nounset errexit pipefail

# Collect the API Proxy and Hosted Target (Sandbox server)
# files into build/apiproxy/ and deploy to Apigee

mkdir -p build
rm -rf build/apiproxy
cp -Rv apiproxy build/
cp -f build/apiproxy/proxies/default_temp.xml build/apiproxy/proxies/default.xml
rm -rf build/apiproxy/proxies/default_temp.xml
mkdir -p build/apiproxy/resources/hosted
rsync -av --copy-links --exclude="node_modules" --filter=':- .gitignore' sandbox/ build/apiproxy/resources/hosted
