function fn() {
  // https://github.com/karatelabs/karate#configure for all the options
  karate.configure('connectTimeout', 5000);
  karate.configure('readTimeout', 10000);
  var env = karate.env; // get java system property 'karate.env'

  if (env == 'ci') {
    // this hides sensitive details from the logs:
    // https://github.com/karatelabs/karate#report-verbosity
    var LM = Java.type('demo.headers.DemoLogModifier');
    karate.configure('logModifier', new LM());
  } else if (env == 'mock') {
    var port = karate.properties['mockserver.port'] || '8080';      
    var config = {
      oauth2MockURL: `http://localhost:${port}`,
      baseURL: `http://localhost:${port}`,
      clientID: java.lang.System.getenv('CLIENT_ID')      
    };
  } else {
    var config = { 
      oauth2MockURL: `${java.lang.System.getenv('OAUTH_BASE_URI')}/${java.lang.System.getenv('OAUTH_PROXY')}`,
      baseURL: `${java.lang.System.getenv('OAUTH_BASE_URI')}/${java.lang.System.getenv('PDS_BASE_PATH')}`,
      clientID: java.lang.System.getenv('CLIENT_ID'),
      clientSecret: java.lang.System.getenv('CLIENT_SECRET'),
      signingKey: java.lang.System.getenv('APPLICATION_RESTRICTED_SIGNING_KEY_PATH'),
      apiKey: java.lang.System.getenv('APPLICATION_RESTRICTED_API_KEY'),
      keyID: java.lang.System.getenv('KEY_ID'),
      internalServerURL: `${java.lang.System.getenv('INTERNAL_SERVER_BASE_URI')}/personal-demographics/FHIR/R4`
    };
  } 
  return config;
}