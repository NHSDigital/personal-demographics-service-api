package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class GetPatientByTwoAppsSimulation extends Simulation {
  var app1Users = 20
  var app2Users = 6
  var duration = 1
  
  val protocol = karateProtocol()
  
  protocol.runner.karateEnv("veit07")
    
    // track the index of the request that returns 429
  var requestCounter = 0
  var app1_429s: Seq[Int] = Seq()
  var app2_429s: Seq[Int] = Seq()

// Scenario for App1
  val scn1 = scenario("App1Test")
    .exec(session => {
      requestCounter += 1
      session.set("requestIndex", requestCounter).set("appName", "App1")
    })
    .exec(karateFeature("classpath:patients/rateLimits/getPatientDetails/getPatientForRateLimitingApp.feature"))
    .exec { session =>
      if (session.contains("is429") && session("is429").as[Boolean]) {
       app1_429s = app1_429s :+ session("requestIndex").as[Int]
      }
      session
    }
// Scenario for App2
    val scn2 = scenario("App2Test")
    .exec(session => {
      requestCounter += 1
      session.set("requestIndex", requestCounter).set("appName", "App2")
    })
    .exec(karateFeature("classpath:patients/rateLimits/getPatientDetails/getPatientForDefaultApp.feature"))
    .exec { session =>
      if (session.contains("is429") && session("is429").as[Boolean]) {
      app2_429s = app2_429s :+ session("requestIndex").as[Int]
      }
      session
    }  
  // Setup with both scenarios  
    setUp(
      scn1.inject(constantUsersPerSec(app1Users) during (duration second)).protocols(protocol),
      scn2.inject(constantUsersPerSec(app2Users) during (duration second)).protocols(protocol)
    )
  
  // hook to run after simulation ends
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from App1Test: ${app1Users}")
    println(s"Total requests from App2Test: ${app2Users}")
    if (app1_429s.nonEmpty) {
      println(s"Total 429 responses from App1Test: ${app1_429s.size}")
    }else if(app1_429s.nonEmpty){
      println(s"Total 429 responses from App2Test: ${app2_429s.size}")
    } 
  }
}
