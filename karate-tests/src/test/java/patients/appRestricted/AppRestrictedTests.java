package patients.appRestricted;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;

class AppRestrictedTests {
    
    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }
    
    @Karate.Test
    Karate testGetPatient() {
        return Karate.run("getPatient").relativeTo(getClass());
    }  

    @Karate.Test
    Karate testCreatePatient() {
        return Karate.run("createPatientError").relativeTo(getClass());
    }  

}
