from locust import HttpUser, constant, task, SequentialTaskSet
from uuid import uuid4

from config import AUTH_MS_BASE_URL, TENANT_MS_BASE_URL
from utils.randomize import generateRandomPhoneNumber

class TestTenantMicroservice(SequentialTaskSet):
    @task
    def login(self):
        # 1. Register
        payload = {
            "username": f"vincentsuryakim+{str(uuid4())}",
            "email": f"vincentsuryakim+{str(uuid4())}@gmail.com",
            "password": "Zhaolusi123",
            "full_name": "Vincent Suryakim",
            "address": "Via Monte Cengio, 19",
            "phone_number": generateRandomPhoneNumber()
        }
        self.client.post(f"{AUTH_MS_BASE_URL}/user/register", json=payload)

        # 2. Login
        payload = {
            "username": payload['username'],
            "password": payload['password']
        }
        response = self.client.post(f"{AUTH_MS_BASE_URL}/user/login", json=payload)
        self.headers = {
            "Authorization": f"Bearer {response.json()['token']}"
        }
    
    @task
    def create_new_tenant(self):
        payload = {
            "name": f"Tenant Test+{str(uuid4())}"
        }
        response = self.client.post("/tenant", json=payload, headers=self.headers)
        if response.status_code == 201:
            self.new_tenant = response.json()
        else:
            raise Exception("Failed to create new tenant")
    
    @task
    def edit_tenant(self):
        payload = {
            "name": f"UPDATED Tenant Test+{str(uuid4())}"
        }
        response = self.client.put(f"/tenant/{self.new_tenant['tenants']['id']}", json=payload, headers=self.headers)
        if response.status_code == 200:
            self.edited_tenant = response.json()['tenantDetails']
        else:
            raise Exception("Failed to edit tenant")
        
    @task
    def get_tenant_information(self):
        response = self.client.get(f"/tenant/{self.edited_tenant['tenant_id']}", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get tenant information")
        else:
            self.finished_retrieve_tenant_information = True
    
    @task
    def delete_tenant(self):
        payload = {
            "tenant_id": self.edited_tenant['tenant_id']
        }
        response = self.client.delete("/tenant", json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to delete tenant")

class TenantMicroserviceUser(HttpUser):
    host = TENANT_MS_BASE_URL
    tasks = [TestTenantMicroservice]
    wait_time = constant(0.5)