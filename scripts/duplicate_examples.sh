#!/bin/bash

# Patient
cp build/examples/resources/Patient.json build/examples/resources/Patient-Jayne-Smyth.json
cp build/examples/resources/PatientSearch.json build/examples/resources/PatientSearch-Jayne-Smyth.json
cp build/examples/resources/PatientSearch.json build/examples/resources/PatientSearch-CompoundName.json
sed -i -e 's/9000000009/9000000015/g; s/Jane/John Paul/g; s/female/male/g; s/Mrs/Mr/g; s/jane.smith@example.com/johnp.smith@example.com/g;' build/examples/resources/PatientSearch-CompoundName.json
sed -i -e 's/9000000009/9000000017/g; s/Jane/Jayne/g; s/Smith/Smyth/g; s/jane.smith@example.com/jayne.smyth@example.com/g;' build/examples/resources/Patient-Jayne-Smyth.json
sed -i -e 's/9000000009/9000000017/g; s/Jane/Jayne/g; s/Smith/Smyth/g; s/jane.smith@example.com/jayne.smyth@example.com/g;' build/examples/resources/PatientSearch-Jayne-Smyth.json
sed -i -e 's/9000000009/9000000025/g; s/Jane/Janet/g; s/Smith/Smythe/g;' build/examples/resources/Sensitive_Patient.json
sed -i -e 's/9000000009/9000000025/g; s/Jane/Janet/g; s/Smith/Smythe/g; s/2010-10-22/2005-06-16/g' build/examples/resources/Sensitive_PatientSearch.json
sed -i -e 's/9000000009/9000000033/g; s/Jane/John/g; s/Smith/Jones/g; s/jane.smith@example.com/john.jones@example.com/g;' build/examples/resources/Minimal_Patient.json
sed -i -e 's/9000000009/9000000033/g; s/Jane/John/g; s/Smith/Jones/g; s/jane.smith@example.com/john.jones@example.com/g;' build/examples/resources/Minimal_PatientSearch.json

# Related Person
sed -i -e 's/507B7621/B3380E98/g' build/examples/resources/Referenced_RelatedPerson.json
sed -i -e 's/507B7621/F4CF8B96/g; s/9000000009/9000000017/g' build/examples/resources/Personal_Details_RelatedPerson.json
