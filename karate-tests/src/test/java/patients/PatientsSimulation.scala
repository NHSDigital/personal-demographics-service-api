package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class PatientsSimulation extends Simulation {
  
  val protocol = karateProtocol()
  
    protocol.runner.karateEnv("perf")
  
    val unrestricted = scenario("unrestricted").exec(karateFeature("classpath:patients/healthcareWorker/getPatientDetails/getPatientByNHSNumber.feature"))
    val sensitive = scenario("sensitive").exec(karateFeature("classpath:patients/healthcareWorker/getPatientDetails/getPatientByNHSNumber.feature"))
    
    setUp(
      unrestricted.inject(rampUsers(100) during (10 seconds)).protocols(protocol),
      sensitive.inject(rampUsers(100) during (10 seconds)).protocols(protocol),
    )
  
}
