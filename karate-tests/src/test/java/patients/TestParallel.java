package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestParallel {

    @Test
    void testDevParallel() {
        Results results = Runner.path("classpath:patients")
                .outputJunitXml(true)
                .tags("@ehictest")
                .karateEnv("veit07")
                .parallel(2);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }


}