from locust import HttpUser, LoadTestShape, SequentialTaskSet, constant, task
from uuid import uuid4

from config import AUTH_MS_BASE_URL
from utils.formatCSVShapeData import formatCSVShapeData
from utils.randomize import generateRandomPhoneNumber

class TestAuthenticationMicroservice(SequentialTaskSet):
    @task
    def register_user(self):
        payload = {
            "username": f"vincentsuryakim+{str(uuid4())}",
            "email": f"vincentsuryakim+{str(uuid4())}@gmail.com",
            "password": "Zhaolusi123",
            "full_name": "Vincent Suryakim",
            "address": "Via Monte Cengio, 19",
            "phone_number": generateRandomPhoneNumber()
        }
        self.client.post("/user/register", json=payload)
        self.user_data = payload
    
    @task
    def login_user(self):
        payload = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }
        self.client.post("/user/login", json=payload)

class AuthenticationMicroserviceUser(HttpUser):
    host = AUTH_MS_BASE_URL
    tasks = [TestAuthenticationMicroservice]
    wait_time = constant(0.5)

class PoissonShapeAuth(LoadTestShape):
    stages = formatCSVShapeData(
        'shape/poisson_max_500.csv',
        AuthenticationMicroserviceUser
    )
    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except:
                    tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
