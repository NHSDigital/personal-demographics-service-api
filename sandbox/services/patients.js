const fs = require('fs')

module.exports = {
    retrieve: {
        examplePatientSmith: JSON.parse(fs.readFileSync('mocks/Patient.json')),
        examplePatientSmyth: JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json')),
        examplePatientSmythe: JSON.parse(fs.readFileSync('mocks/Sensitive_Patient.json'))
    },
    search: {
        exampleSearchPatientSmith: JSON.parse(fs.readFileSync('mocks/PatientSearch.json')),
        exampleSearchPatientSmyth: JSON.parse(fs.readFileSync('mocks/PatientSearch-Jayne-Smyth.json')),
        exampleSearchPatientSmythe: JSON.parse(fs.readFileSync('mocks/Sensitive_PatientSearch.json'))
    }
}