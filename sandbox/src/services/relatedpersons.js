const fs = require('fs')

module.exports = {
    "9000000009": {
        exampleFullResponse: JSON.parse(fs.readFileSync('mocks/RelatedPerson.json')).entry[0].resource,
        exampleReferencedResponse: JSON.parse(fs.readFileSync('mocks/Referenced_RelatedPerson.json')).entry[0].resource
    },
    "9000000017": {
        examplePersonDetailsResponse: JSON.parse(fs.readFileSync('mocks/Personal_Details_RelatedPerson.json')).entry[0].resource
    }
}