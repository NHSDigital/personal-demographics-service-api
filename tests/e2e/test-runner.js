doc = `
API Management Postman Test Runner

Usage:
  test-runner.js <token_app_url> <environment_url> <collection_path> <environment_file_path>
  test-runner.js -h | --help

  -h --help  Show this text.
`;


const fs = require('fs');
const path = require('path');
const docopt = require('docopt').docopt;
const newman = require('newman');
const puppeteer = require('puppeteer');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function retry(func, times) {
    let result;
    let success = false;
    let error;

    for (let i = 0; i < times; i++) {
        try {
            result = await func();
            success = true;
            break;
        } catch (e) {
            error = e;
            console.error(e);
        }
    }

    if (!success) {
        throw error;
    }

    return result;
}

async function gotoLogin(browser, login_url) {
    const page = await browser.newPage();
    await page.goto(login_url, { waitUntil: 'networkidle2', timeout: 30000 });
    await page.waitForSelector('#start', { timeout: 30000 });
    await page.click("#start");
    await page.waitForSelector('button[class="btn btn-lg btn-primary btn-block"]', {timeout: 30000});
    await page.click('button[class="btn btn-lg btn-primary btn-block"]');    
    return page;
}

function nhsIdLogin(login_url, callback) {
    (async () => {
        console.log("Oauth journey on " + login_url);
        const browser = await puppeteer.launch({ headless: true });
        const page = await retry(async () => { return await gotoLogin(browser, login_url); }, 3);                
        let credentialsJSON = await page.$eval('body > div > div > pre', e => e.innerText);
        let credentials = JSON.parse(credentialsJSON.replace(/'/g, '"'));
        await browser.close();
        callback(credentials);
    })();
}

function collectionRunner(url, collection_path, environment_path) {
    const collection = JSON.parse(fs.readFileSync(
        path.resolve(collection_path)
    ));
    const environment = JSON.parse(fs.readFileSync(
        path.resolve(environment_path)
    ));

    return (credentials) => {
        collection.auth = {
		        "type": "bearer",
		        "bearer": [
			          {
				            "key": "token",
				            "value": credentials.access_token,
				            "type": "string"
			          }
		        ]};

        newman.run({
            collection: collection,
            reporters: ['cli', 'junit'],
            reporter: {
                junit: {
                    export: './test-report.xml'
                }
            },
            environment: environment, // What is going on here?
            environment: {
                "id": "0eba6cf0-3fd1-4b3f-b6be-4b20153baf8d",
                "name": "environment-params",
                "values": [
                    {
                        "key": "environment",
                        "value": url,
                        "type": "text",
                        "enabled": true
                    },
                ],
                "timestamp": 1404119927461,
                "_postman_variable_scope": "environment",
                "_postman_exported_at": "2020-04-03T14:31:26.200Z",
                "_postman_exported_using": "Postman/4.8.0"
            },
            globals: {
                "id": "5bfde907-2a1e-8c5a-2246-4aff74b74236",
                "name": "global-params",
                "values": [
                    {
                        "key": "token",
                        "value": credentials.access_token,
                        "type": "text",
                        "enabled": true
                    },
                    {
                        "key": "nhsd-session-urid-header",
                        "value": "NHSD-Session-URID",
                        "type": "text",
                        "enabled": true
                    },
                    {
                        "key": "role_id",
                        "value": "1234567890",
                        "enabled": true
                    },
                ],
                "timestamp": 1404119927461,
                "_postman_variable_scope": "globals",
                "_postman_exported_at": "2020-04-03T14:31:26.200Z",
                "_postman_exported_using": "Postman/4.8.0"
            },
        }, function (err) {
            if (err) { throw err; }
            console.log('collection run complete!');
        }).on('start', function (err, args) {
            console.log('Running against ' + url);
            console.log('Using collection file ' + collection_path);
            console.log('Using environment file ' + environment_path);
        });
    };
}

function main(args) {
    nhsIdLogin(        
        args['<token_app_url>'],
        collectionRunner(
            args['<environment_url>'],
            args['<collection_path>'],
            args['<environment_file_path>']
        )
    );
}

args = docopt(doc);
main(args);
