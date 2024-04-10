from uuid import uuid4
from locust import HttpUser, SequentialTaskSet, constant, task

from config import AUTH_MS_BASE_URL, ORDERS_MS_BASE_URL, PRODUCTS_MS_BASE_URL
from utils.randomize import generateRandomPhoneNumber

class TestShoppingCartMicroservice(SequentialTaskSet):
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
    def add_items_to_cart(self):
        payload = {
            "product_id": self.product['id'],
            "quantity": 1
        }
        response = self.client.post("/cart", json=payload, headers=self.headers)
        if response.status_code != 201:
            raise Exception("Failed to add items to cart")
        self.cart_item = response.json()
    
    @task
    def edit_cart_item_data(self):
        payload = {
            "cart_id": self.cart_item['id'],
            "quantity": 2
        }
        response = self.client.put("/cart", json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to edit cart item data")
        self.edited_cart_item = response.json()
    
    @task
    def get_all_items_in_cart(self):
        response = self.client.get("/cart", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get all items in cart")
        self.all_items_in_cart = response.json()
    
    @task
    def delete_cart_item(self):
        payload = {
            "product_id": self.edited_cart_item['product_id']
        }
        response = self.client.delete("/cart", json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to delete cart item")

class ShoppingCartMicroserviceUser(HttpUser):
    host = ORDERS_MS_BASE_URL
    tasks = [TestShoppingCartMicroservice]
    wait_time = constant(0.5)