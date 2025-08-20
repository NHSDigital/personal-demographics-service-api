package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import com.intuit.karate.http.HttpServer;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestLocalMockParallel {

    static HttpServer server;

    @Test
    void testLocalMockParallel() {
        Results results = Runner.path("classpath:patients")
            .karateEnv("local-sandbox")
            .tags("@sandbox, @sandbox-only", "~@smoke-only", "~@rateLimit")
            .outputJunitXml(true)
            .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}