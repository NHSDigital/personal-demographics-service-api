package patients.healthcareWorker.updatePatientDetails;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import com.intuit.karate.http.HttpServer;

import mocks.MockRunner;

public class TestUpdatePatientDetailsParallel {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }

    @Test
    void testParallel() {
        Results results = Runner.path("classpath:patients/healthcareWorker/updatePatientDetails")
                .outputJunitXml(true)
                .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}
