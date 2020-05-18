const fs = require('fs')

module.exports = {
    retrieve: {
        examplePatientSmith: JSON.parse(fs.readFileSync('mocks/Patient.json')),
        examplePatientSmyth: JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json')),
        examplePatientSmythe: JSON.parse(fs.readFileSync('mocks/Sensitive_Patient.json'))
    },
    search: {
        exampleSearchPatientSmith: JSON.parse(fs.readFileSync('mocks/Search_Patient.json')),
        exampleSearchPatientSmyth: JSON.parse(fs.readFileSync('mocks/Search_Patient-Jayne-Smyth.json')),
        exampleSearchPatientSmythe: JSON.parse(fs.readFileSync('mocks/Sensitive_Search_Patient.json'))
    }
}