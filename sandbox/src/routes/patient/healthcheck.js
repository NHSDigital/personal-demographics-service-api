module.exports = [{
  /*
      _health endpoint for container liveness check
  */
  method: 'GET',
  path: '/_health',
  /*jslint unparam: true*/
  handler: (request, h) => {
      return h.response(
        {
          status: "pass",
          ping: "pong",
          version: JSON.parse(process.env.VERSION_INFO)
        }
      )
      .code(200)
    }
    /*jslint unparam: false*/
}]
