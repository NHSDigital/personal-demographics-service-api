package patients.healthcareWorker;

import com.intuit.karate.junit5.Karate;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;

import patients.MockRunner;

class healthcareWorkerTests {

    static final Logger logger = LoggerFactory.getLogger(healthcareWorkerTests.class);
    
    static HttpServer server;

    // @BeforeAll
    // static void beforeAll() {
    //     server = MockRunner.start("src/test/java/patients", 8080);
    //     System.setProperty("mockserver.port", server.getPort() + "");  
    // }    

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

    // @AfterAll
    // static void afterAll() {
    //     server.stop();
    // }   
}