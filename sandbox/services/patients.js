const fs = require('fs')

module.exports = {
    examplePatientSmith: JSON.parse(fs.readFileSync('mocks/Patient.json')),
    examplePatientSmyth: JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json')),
    exampleSearchPatientSmith: JSON.parse(fs.readFileSync('mocks/Search_Patient.json')),
    exampleSearchPatientSmyth: JSON.parse(fs.readFileSync('mocks/Search_Patient-Jayne-Smyth.json'))
}