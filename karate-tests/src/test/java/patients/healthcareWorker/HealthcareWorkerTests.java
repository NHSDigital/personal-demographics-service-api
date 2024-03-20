package patients.healthcareWorker;

import com.intuit.karate.junit5.Karate;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.intuit.karate.http.HttpServer;

class HealthcareWorkerTests {

    static final Logger logger = LoggerFactory.getLogger(HealthcareWorkerTests.class);
    
    static HttpServer server;

    @Karate.Test
    Karate testGetPatient() {
        return Karate.run("getPatient").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testPatchPatient() {
        return Karate.run("patchPatient").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testPostPatient() {
        return Karate.run("postPatient").relativeTo(getClass());
    }  

}