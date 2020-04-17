const newman = require('newman');
const puppeteer = require('puppeteer');

const username = '910000000001';
const password = 'Password1';
var access_token = '';
var jwt_token = '';


function nhsIdLogin(_callback) {
    (async () => {
        let herokuapp_url = process.argv[3];
        console.log("Oauth journey on " + herokuapp_url);
        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();
        await page.goto(herokuapp_url, { waitUntil: 'networkidle2' });
        await page.click("#start");
        await page.waitForSelector('#idToken1');
        await page.type('#idToken1', username);
        await page.type('#idToken2', password);
        await page.click('#loginButton_0');
        await page.waitForNavigation();

        let tokenJson = await page.$eval('body > div > div > pre', e => e.innerText);
        setTokens(tokenJson);
        await browser.close();
        _callback();
    })();
}

function setTokens(json) {
    let data = JSON.parse(json);
    access_token = json.access_token;
    jwt_token = json.id_token;
}

function runPostmanCollection() {
    newman.run({
        collection: require(process.argv[2]),
        reporters: ['cli', 'junit'],
        reporter: {
            junit: {
                export: './test-report.xml'
            }
        },
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
        environment: require(process.argv[5])
    }, function (err) {
        if (err) { throw err; }
        console.log('collection run complete!');
    }).on('start', function (err, args) {
        console.log('Running against ' + process.argv[4]);
        console.log('Using environment file ' + process.argv[5]);
    });
}

function run() {
    nhsIdLogin(runPostmanCollection);
}

run();
