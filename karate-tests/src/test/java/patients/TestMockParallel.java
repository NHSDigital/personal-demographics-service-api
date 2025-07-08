package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestMockParallel {

    @Test
    void testMockParallel() {
        Results results = Runner.path("classpath:patients")
            .karateEnv("sandbox")
            .tags("@sandbox, @sandbox-only", "~@smoke-only", "~@rateLimit")
            .outputJunitXml(true)
            .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}