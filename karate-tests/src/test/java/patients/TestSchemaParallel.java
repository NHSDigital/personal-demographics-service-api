package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;


public class TestSchemaParallel {

    @Test
    void testSchemaParallel() {
        Results results = Runner.path("classpath:patients")
                .outputJunitXml(true)
                .tags("~@sandbox-only", "~@no-oas", "~@oas-bug", "~@smoke-only")
                .karateEnv("prism")
                .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

}