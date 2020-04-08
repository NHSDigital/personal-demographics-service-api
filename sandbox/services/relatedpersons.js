const fs = require('fs')

module.exports = {
    P_9000000009: {
        exampleFullResponse: JSON.parse(fs.readFileSync('mocks/RelatedPerson.json')),
        exampleReferencedResponse: JSON.parse(fs.readFileSync('mocks/Referenced_RelatedPerson.json'))
    },
    P_9000000017: {
        examplePersonDetailsResponse: JSON.parse(fs.readFileSync('mocks/Personal_Details_RelatedPerson.json'))
    }
}