import os
import requests
import json
import urllib.parse as urlparse
from common.auth import Auth
from urllib.parse import parse_qs
from locust import HttpUser, task, between

class PersonalDemographicsUser(HttpUser):
    wait_time = between(5, 9)

    def auth(self):
        return Auth(
            os.environ["LOCUST_HOST"],
            os.environ["APIGEE_ENVIRONMENT"],
            os.environ["API_KEY"]
        )

    def on_start(self):
        authenticator = self.auth()
        self.credentials = authenticator.login()
        self.headers = { 
            "Authorization": self.credentials["token_type"] + " " + self.credentials["access_token"],
            "NHSD-Identity-UUID": "1234567890",
            "NHSD-Session-URID": "1234567890",
        }
  
    @task(1)
    def pds_api(self):
        self.client.get("/personal-demographics-APM-620-rate-limiting/Patient/5900018512", headers=self.headers)


