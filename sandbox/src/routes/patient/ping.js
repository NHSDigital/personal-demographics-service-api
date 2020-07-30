module.exports = [
    {
        /*
            Ping for hosted target
        */
        method: 'GET',
        path: '/_ping',
        /*jslint unparam: true*/
        handler: (request, h) => {
            const data = { key: 'pong' }
            return h.response(data).code(200)
        }
        /*jslint unparam: false*/
    }
]
