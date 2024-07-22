package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestSmoke {
    
    @Test
    void testSmoke() {
        Results results = Runner.path("classpath:patients")
            .karateEnv("int")
            .tags("@smoke, @smoke-only")
            .outputJunitXml(true)
            .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}