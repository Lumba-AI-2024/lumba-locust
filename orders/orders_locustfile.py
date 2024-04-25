import random
from uuid import uuid4
from locust import HttpUser, LoadTestShape, SequentialTaskSet, constant, task

from config import AUTH_MS_BASE_URL, ORDERS_MS_BASE_URL, PRODUCTS_MS_BASE_URL
from utils.formatCSVShapeData import formatCSVShapeData
from utils.randomize import generateRandomPhoneNumber

class TestOrdersMicroservice(SequentialTaskSet):
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

        # 3. Add products to cart
        response = self.client.get(f"{PRODUCTS_MS_BASE_URL}/product")
        self.product = response.json()['products'][0]
        payload = {
            "product_id": self.product['id'],
            "quantity": 1
        }
        response = self.client.post("/cart", json=payload, headers=self.headers)
        if response.status_code != 201:
            raise Exception("Failed to add items to cart")
        self.cart_item = response.json()

    @task
    def place_order(self):
        payload = {
            "shipping_provider": "JNE",
        }
        response = self.client.post("/order", json=payload, headers=self.headers)
        if response.status_code != 201:
            raise Exception("Failed to create new order")
        self.new_order = response.json()
    
    @task
    def get_all_of_my_orders(self):
        response = self.client.get("/order", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get all of my orders")
        self.all_of_my_orders = response.json()
    
    @task
    def get_order_detail_by_order_id(self):
        # Get a random index from the list of all products
        random_index = random.randint(0, len(self.all_of_my_orders) - 1)

        # Get a random order ID
        order_id = self.all_of_my_orders[random_index]['id']

        response = self.client.get(f"/order/{order_id}", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get order by order ID")
        self.my_order_detail = response.json()

    @task
    def pay_order(self):
        payload = {
            "payment_method": "QRIS",
            "payment_reference": str(uuid4()),
            "amount": self.new_order['order']['total_amount']
        }
        response = self.client.post(f'/order/{self.new_order["order"]["id"]}/pay', json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to pay order")
    
    @task
    def cancel_order(self):
        response = self.client.post(f"/order/{self.new_order['order']['id']}/cancel", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to cancel order")

class OrdersMicroserviceUser(HttpUser):
    host = ORDERS_MS_BASE_URL
    tasks = [TestOrdersMicroservice]
    wait_time = constant(0.5)

class PoissonShapeOrders(LoadTestShape):
    stages = formatCSVShapeData(
        'shape/poisson_max_500.csv',
        OrdersMicroserviceUser
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
