package patients.healthcareWorker.createPatient;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;

public class TestCreatePatient {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }

    @Karate.Test
    Karate testCreate() {
        return Karate.run("postPatient").relativeTo(getClass());
    }

}