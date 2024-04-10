import random
from locust import HttpUser, constant, task, SequentialTaskSet
from uuid import uuid4

from config import AUTH_MS_BASE_URL, PRODUCTS_MS_BASE_URL

class TestProductsMicroserviceAsUser(SequentialTaskSet):
    @task
    def before_start(self):
        # 1. Login
        payload = {
            "username": "vincentsuryakim",
            "password": "Zhaolusi123"
        }
        response = self.client.post(f"{AUTH_MS_BASE_URL}/user/login", json=payload)
        self.headers = {
            "Authorization": f"Bearer {response.json()['token']}"
        }

        # 2. Add categories
        payload = {
            "name": f"Category Test+{str(uuid4())}"
        }
        response = self.client.post("/product/category", json=payload, headers=self.headers)
        if response.status_code == 201:
            self.new_category = response.json()
        else:
            raise Exception("Failed to create new category")

        # 3. Add products
        payload = {
            "name": f"Product Test+{str(uuid4())}",
            "description": "This is a test product",
            "price": 10000,
            "quantity_available": 10,
            "category_id": self.new_category['id']
        }
        response = self.client.post("/product", json=payload, headers=self.headers)
        if response.status_code == 201:
            self.new_product = response.json()
        else:
            raise Exception("Failed to create new product")

    @task
    def get_all_products(self):
        response = self.client.get("/product")
        self.all_products = response.json()['products']

    @task
    def get_product_by_id(self):
        # Get a random index from the list of all products
        random_index = random.randint(0, len(self.all_products) - 1)

        # Get a random product ID
        product_id = self.all_products[random_index]['id']        

        response = self.client.get(f"/product/{product_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get product with ID {product_id}")
    
    @task
    def get_all_categories(self):
        response = self.client.get("/product/category")
        self.all_categories = response.json()['categories']

    @task
    def get_products_by_category(self):
        response = self.client.get(f"/product/category/{self.new_category['id']}")
        if response.status_code == 200:
            self.products_by_category = response.json()['products']
        else:
            raise Exception(f"Failed to get products with category ID {self.new_category['id']}")

    @task
    def get_products_by_id_retrieved_from_category(self):
        # Get a random index from the list of all categories
        random_index = random.randint(0, len(self.products_by_category) - 1)

        # Get a random product ID
        product_id = self.products_by_category[random_index]['id']

        self.client.get(f"/product/{product_id}")

class ProductsMicroserviceUserAsTenant(HttpUser):
    host = PRODUCTS_MS_BASE_URL
    tasks = [TestProductsMicroserviceAsUser]
    wait_time = constant(0.5)