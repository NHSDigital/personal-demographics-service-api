const fs = require('fs');

let routes = [];

/* 
    Imports all of the routes from the files in the directory
*/
fs.readdirSync(__dirname)
  .filter(file => file != 'index.js')
  .forEach(file => {
    routes = routes.concat(require(`./${file}`))
  });

module.exports = routes;