package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestParallel {

    @Test
    void testDevParallel() {
        Results results = Runner.path("classpath:patients")
                .tags("~@sandbox")
                .outputJunitXml(true)
                .karateEnv("dev")
                .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }


}