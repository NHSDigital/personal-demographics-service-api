package patients.healthcareWorker.getPatientDetails;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import com.intuit.karate.http.HttpServer;

import mocks.MockRunner;

public class TestGetPatientDetailsMockParallel {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        server = MockRunner.start("src/test/java/mocks", 8080);
    }

    @Test
    void testMockParallel() {
        Results results = Runner.path("classpath:patients/healthcareWorker/getPatientDetails")
                .tags("@sandbox")
                .outputJunitXml(true)
                .karateEnv("mock")
                .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }  
}
