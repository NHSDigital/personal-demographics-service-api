import json

with open('../build/personal-demographics.json', 'r') as pdsFullSpec:
    fullSpec = json.load(pdsFullSpec)

with open('../short-version/personal-demographics-short-version.json', 'r') as pdsShortSpec:
    shortSpec = json.load(pdsShortSpec)

shortSpec['components'] = fullSpec['components']

with open('../short-version/personal-demographics-short-version.json', 'w') as data_file:
    json.dump(shortSpec, data_file, indent=4)
