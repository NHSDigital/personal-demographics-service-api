package patients.healthcareWorker;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;

public class MockPatchPatientTests {

        static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        server = MockRunner.start("src/test/java/mocks", 8080);
    }
    
    @Karate.Test
    Karate testPatchPatient() {
        return Karate.run("patchPatient").relativeTo(getClass());
    }

}
