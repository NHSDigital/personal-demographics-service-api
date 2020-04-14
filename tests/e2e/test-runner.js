const newman = require('newman');
const puppeteer = require('puppeteer');

const username = '910000000001';
const password = 'Password1';
var access_token = '';
var jwt_token = ''


function nhsIdLogin(_callback) {
    (async () => {
        let herokuapp_url = process.argv[3];
        console.log("Oauth journey on " + herokuapp_url);
        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();
        await page.goto(herokuapp_url, { waitUntil: 'networkidle2' });
        await page.click("#start")
        await page.waitForSelector('#idToken1');
        await page.type('#idToken1', username);
        await page.type('#idToken2', password);
        await page.click('#loginButton_0');
        await page.waitForNavigation();

        let tokens = await page.$eval('body > div > div > pre', e => e.innerText);
        setTokens(tokens);        
        await browser.close();
        _callback();
    })();
}

function setTokens(json) {
    let parts = json.split(",");
    access_token = parts[0].split(":")[1].trim();
    jwt_token = parts[2].split(":")[1].trim();

    access_token = access_token.replace(/'/g, '');
    jwt_token = jwt_token.replace(/'/g, '');
}

function runPostmanCollection() {
    newman.run({
        collection: require(process.argv[2]),
        reporters: ['cli', 'junit'],
        globals: {
            "id": "5bfde907-2a1e-8c5a-2246-4aff74b74236",
            "name": "global-params",
            "values": [
                {
                    "key": "token",
                    "value": access_token,
                    "type": "text",
                    "enabled": true
                },
                {
                    "key": "jwt",
                    "value": jwt_token,
                    "type": "text",
                    "enabled": true
                },
                {
                    "key": "environment",
                    "value": process.argv[4],
                    "type": "text",
                    "enabled": true
                }
            ],
            "timestamp": 1404119927461,
            "_postman_variable_scope": "globals",
            "_postman_exported_at": "2020-04-03T14:31:26.200Z",
            "_postman_exported_using": "Postman/4.8.0"
        },
        // globals: require('/Users/gurdeep/Documents/Postman/globals.json'),
        // environment: require('/Users/gurdeep/Documents/Postman/veit05.json'),
    }, function (err) {
        if (err) { throw err; }
        console.log('collection run complete!');
    }).on('start', function (err, args) {
        console.log('Running against ' + process.argv[4]);
        console.log("Access Token: " + access_token);
        console.log("JWT: " + jwt_token);
    });
}

function run() {
    nhsIdLogin(runPostmanCollection);
}

run();
