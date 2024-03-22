package patients;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import net.masterthought.cucumber.Configuration;
import net.masterthought.cucumber.ReportBuilder;

import org.apache.commons.io.FileUtils;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;


public class TestParallel {

    @Test
    void testDevParallel() {
        Results results = Runner.path("classpath:patients")
                .outputCucumberJson(true)
                .outputJunitXml(true)
                .karateEnv("dev")
                .parallel(5);
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());

        generateReport(results.getReportDir());
        assertEquals(0, results.getFailCount(), results.getErrorMessages());
    }

    public static void generateReport(String karateOutputPath) {
        Collection<File> jsonFiles = FileUtils.listFiles(new File(karateOutputPath), new String[] {"json"}, true);
        List<String> jsonPaths = new ArrayList<String>(jsonFiles.size());
        for(File file : jsonFiles){
            jsonPaths.add(file.getAbsolutePath());
        }
        Configuration config = new Configuration(new File("target"), "REST API Automation - Karate");
        ReportBuilder reportBuilder = new ReportBuilder(jsonPaths, config);
        reportBuilder.generateReports();
    }

}