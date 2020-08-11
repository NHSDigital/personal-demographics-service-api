module.exports = [{
  /*
      _health endpoint for container liveness check
  */
  method: 'GET',
  path: '/_health',
  /*jslint unparam: true*/
  handler: (request, h) => {
      return h.response().code(200)
    }
    /*jslint unparam: false*/
}]
