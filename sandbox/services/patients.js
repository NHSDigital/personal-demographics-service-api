const fs = require('fs')

module.exports = {
    examplePatientSmith: JSON.parse(fs.readFileSync('mocks/Patient.json')),
    examplePatientSmyth: JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json'))
}