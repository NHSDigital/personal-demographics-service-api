package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class GetPatientByTwoAppsSimulation extends Simulation {
 // === Configuration ===
  val app1Users = 41
  val app2Users = 30
  val duration = 1 // in minutes

  val protocol = karateProtocol()
  protocol.runner.karateEnv("veit07")

  // === State Tracking ===
  var requestCounter = 0
  var app1_429s, app2_429s = Seq[Int]()
  var app1_429Timestamps, app2_429Timestamps = Seq[String]()

  // === Helper to Handle 429 Tracking ===
  def track429(session: Session, appLabel: String): Session = {
    if (session.contains("is429") && session("is429").as[Boolean]) {
      val index = session("requestIndex").as[Int]
      val timestamp = session("timestamp429").as[String]
      val entry = s"Request $index at $timestamp"

      appLabel match {
        case "App1" =>
          app1_429s = app1_429s :+ index
          app1_429Timestamps = app1_429Timestamps :+ entry
        case "App2" =>
          app2_429s = app2_429s :+ index
          app2_429Timestamps = app2_429Timestamps :+ entry
      }
    }
    session
  }

  // === Scenario Definitions ===
  def scenarioForApp(appLabel: String, featurePath: String) = {
    scenario(s"${appLabel}Test")
      .exec(session => {
        requestCounter += 1
        session.set("requestIndex", requestCounter).set("appName", appLabel)
      })
      .exec(karateFeature(featurePath))
      .exec(session => track429(session, appLabel))
  }

  val scn1 = scenarioForApp("App1", "classpath:patients/rateLimits/getPatientDetails/getPatientForRateLimitingApp.feature")
  val scn2 = scenarioForApp("App2", "classpath:patients/rateLimits/getPatientDetails/getPatientForDefaultApp.feature")

  // === Simulation Setup ===
  setUp(
    scn1.inject(rampUsers(app1Users) during (duration minute)).protocols(protocol),
    scn2.inject(rampUsers(app2Users) during (duration minute)).protocols(protocol)
  )

  // === Report Output ===
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from App1Test: $app1Users")
    println(s"Total requests from App2Test: $app2Users")

    def print429s(appLabel: String, count: Int, timestamps: Seq[String]) = {
      println(s"Total 429 responses from $appLabel: $count")
      if (timestamps.nonEmpty) timestamps.foreach(println)
      else println("No 429 responses received")
    }

    print429s("App1Test", app1_429s.size, app1_429Timestamps)
    print429s("App2Test", app2_429s.size, app2_429Timestamps)
  }
}
