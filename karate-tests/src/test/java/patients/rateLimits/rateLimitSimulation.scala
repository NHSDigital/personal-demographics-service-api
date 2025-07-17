package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class GetPatientRateLimitSimulation extends Simulation {
  val requestingApp = System.getProperty("requestingApp")

  val numberOfRequests = Integer.getInteger("numberOfRequests")
  val duration = Integer.getInteger("duration")  

  val protocol = karateProtocol()
  protocol.runner.karateEnv("veit07")

  var requestCounter = 0
  var all429s: Seq[Int] = Seq()

  val scn = scenario("RateLimitTest")
    .exec(session => {
      requestCounter += 1
      session.set("requestIndex", requestCounter)
    })
    .exec(karateSet("requestingApp", session => requestingApp))
    .exec(karateFeature(s"classpath:patients/rateLimits/getPatientDetails.feature"))
    .exec { session =>
      if (session.contains("is429") && session("is429").as[Boolean]) {
      all429s = all429s :+ session("requestIndex").as[Int]
      }
      session
    }
    
    setUp(
      scn.inject(rampUsers(numberOfRequests) during (duration.seconds)).protocols(protocol)
    )
  
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from $requestingApp: $numberOfRequests")
    if (all429s.nonEmpty) {
      println(s"Total 429 responses: ${all429s.size}")
    }else {
      println("No 429 responses received")
    }
  }
}
