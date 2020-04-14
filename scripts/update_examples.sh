#!/bin/bash

jq -rM . <build/examples/resources/Patient.json >specification/components/examples/Patient.json
jq -rM . <build/examples/resources/Patient-Jayne-Smyth.json >specification/components/examples/Patient-Jayne-Smyth.json
jq -rM . <build/examples/resources/Search_Patient.json >specification/components/examples/Search_Patient.json
jq -rM . <build/examples/resources/Search_Patient-Jayne-Smyth.json >specification/components/examples/Search_Patient-Jayne-Smyth.json
jq -rM . <build/examples/resources/Sensitive_Patient.json >specification/components/examples/Sensitive_Patient.json
jq -rM . <build/examples/resources/Sensitive_Search_Patient.json >specification/components/examples/Sensitive_Search_Patient.json
