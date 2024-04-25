from locust import HttpUser, LoadTestShape, SequentialTaskSet, constant, task
from uuid import uuid4

from config import AUTH_MS_BASE_URL, PRODUCTS_MS_BASE_URL, WISHLIST_MS_BASE_URL
from utils.formatCSVShapeData import formatCSVShapeData
from utils.randomize import generateRandomPhoneNumber

class TestWishlistMicroservice(SequentialTaskSet):
    @task
    def before_start(self):
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

        response = self.client.get(f"{PRODUCTS_MS_BASE_URL}/product")
        self.product = response.json()['products'][0]

    @task
    def create_wishlist(self):
        payload = {
            "name": f"Test Wishlist+{str(uuid4())}"
        }
        response = self.client.post("/wishlist", json=payload, headers=self.headers)
        if response.status_code != 201:
            raise Exception("Failed to create new wishlist")
        self.new_wishlist = response.json()
    
    @task
    def get_all_of_my_wishlist(self):
        response = self.client.get("/wishlist", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get all of my wishlist")
        self.all_of_my_wishlist = response.json()
    
    @task
    def add_product_to_wishlist(self):
        payload = {
            "wishlist_id": self.new_wishlist['id'],
            "product_id": self.product['id']
        }
        response = self.client.post('/wishlist/add', json=payload, headers=self.headers)
        if response.status_code != 201:
            raise Exception("Failed to add product to wishlist")

    @task
    def get_wishlist_detail_by_id(self):
        response = self.client.get(f"/wishlist/{self.new_wishlist['id']}", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get wishlist by ID")
        self.my_wishlist_detail = response.json()
    
    @task
    def update_wishlist(self):
        payload = {
            "name": f"UPDATED Test Wishlist+{str(uuid4())}"
        }
        response = self.client.put(f"/wishlist/{self.new_wishlist['id']}", json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to update wishlist")

    @task
    def delete_product_from_wishlist(self):
        payload = {
            "id": self.my_wishlist_detail['id']
        }
        response = self.client.delete("/wishlist/remove", json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to delete product from wishlist")

    @task
    def delete_wishlist(self):
        response = self.client.delete(f"/wishlist/{self.new_wishlist['id']}", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to delete wishlist")

class WishlistMicroserviceUser(HttpUser):
    host = WISHLIST_MS_BASE_URL
    tasks = [TestWishlistMicroservice]
    wait_time = constant(0.5)

class PoissonShapeWishlist(LoadTestShape):
    stages = formatCSVShapeData(
        'shape/poisson_max_500.csv',
        WishlistMicroserviceUser
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
