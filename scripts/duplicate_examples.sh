#!/bin/bash

# Patient
cp build/examples/resources/Patient.json build/examples/resources/Patient-Jayne-Smyth.json
cp build/examples/resources/Search_Patient.json build/examples/resources/Search_Patient-Jayne-Smyth.json
sed -i -e 's/9000000009/9000000017/g; s/Jane/Jayne/g; s/Smith/Smyth/g;' build/examples/resources/Patient-Jayne-Smyth.json
sed -i -e 's/9000000009/9000000017/g; s/Jane/Jayne/g; s/Smith/Smyth/g;' build/examples/resources/Search_Patient-Jayne-Smyth.json
sed -i -e 's/9000000009/9000000025/g; s/Jane/Janet/g; s/Smith/Smythe/g;' build/examples/resources/Sensitive_Patient.json
sed -i -e 's/9000000009/9000000025/g; s/Jane/Janet/g; s/Smith/Smythe/g; s/2010-10-22/2005-06-16/g' build/examples/resources/Sensitive_Search_Patient.json

# Related Person
sed -i -e 's/507B7621/B3380E98/g' build/examples/resources/Referenced_RelatedPerson.json
sed -i -e 's/507B7621/F4CF8B96/g; s/9000000009/9000000017/g' build/examples/resources/Personal_Details_RelatedPerson.json
