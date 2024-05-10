package patients.healthcareWorker.getPatientDetails;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;


public class TestGetPatientDetailsSingles {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }
    
    @Karate.Test
    Karate testThis() {
        return Karate.run("getPatientErrorScenarios").tags("@this").relativeTo(getClass());
    }    
    
    @Karate.Test
    Karate testGetPatientByNHSNumber() {
        return Karate.run("getPatientByNHSNumber").relativeTo(getClass());
    }    
    
    @Karate.Test
    Karate testGetPatientErrorScenarios() {
        return Karate.run("getPatientErrorScenarios").relativeTo(getClass());
    }

    @Karate.Test
    Karate testGetPatientInvalidRoleErrors() {
        return Karate.run("getPatientErrorScenarios").relativeTo(getClass());
    }
}