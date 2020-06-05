const patientRoutes = require('./patient')
const statusRoutes = require('./get-status')

const routes = [].concat(patientRoutes, statusRoutes)

module.exports = routes
