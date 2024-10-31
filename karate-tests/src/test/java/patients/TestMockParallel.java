package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import com.intuit.karate.http.HttpServer;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import mocks.MockRunner;


public class TestMockParallel {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        server = MockRunner.start("src/test/java/mocks", 8080);
    }
    
    @Test
    void testMockParallel() {
        Results results = Runner.path("classpath:patients")
            .karateEnv("mock")
            .tags("@sandbox, @sandbox-only", "~@smoke-only")
            .outputJunitXml(true)
            .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}