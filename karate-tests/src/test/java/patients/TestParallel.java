package patients;

// import java.io.File;
// import java.util.ArrayList;
// import java.util.Collection;
// import java.util.List;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

// import net.masterthought.cucumber.Configuration;
// import net.masterthought.cucumber.ReportBuilder;
// import org.apache.commons.io.FileUtils;


public class TestParallel {

    @Test
    void testDevParallel() {
        Results results = Runner.path("classpath:patients")
                .tags("~@wip")        
                .outputJunitXml(true)
                .karateEnv("dev")
                .parallel(1);
        // generateReport(results.getReportDir());
        assertTrue(results.getFailCount() == 0, results.getErrorMessages());
    }

    // public static void generateReport(String karateOutputPath) {
    //     Collection<File> jsonFiles = FileUtils.listFiles(new File(karateOutputPath), new String[] {"json"}, true);
    //     List<String> jsonPaths = new ArrayList<>(jsonFiles.size());
    //     jsonFiles.forEach(file -> jsonPaths.add(file.getAbsolutePath()));
    //     Configuration config = new Configuration(new File("target"), "dev");
    //     ReportBuilder reportBuilder = new ReportBuilder(jsonPaths, config);
    //     reportBuilder.generateReports();
    // }

}