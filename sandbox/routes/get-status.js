module.exports = [
  {
    method: 'GET',
    path: '/_status',
    handler: () => {
      return "OK";
    }
  }
]
