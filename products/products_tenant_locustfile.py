from uuid import uuid4
from locust import HttpUser, SequentialTaskSet, constant, task

from config import AUTH_MS_BASE_URL, PRODUCTS_MS_BASE_URL

class TestProductsMicroserviceAsTenant(SequentialTaskSet):
    @task
    def before_start(self):
        payload = {
            "username": "vincentsuryakim",
            "password": "Zhaolusi123"
        }
        response = self.client.post(f"{AUTH_MS_BASE_URL}/user/login", json=payload)
        self.headers = {
            "Authorization": f"Bearer {response.json()['token']}"
        }

    @task
    def create_new_category(self):
        payload = {
            "name": f"Category Test+{str(uuid4())}"
        }
        response = self.client.post("/product/category", json=payload, headers=self.headers)
        if response.status_code == 201:
            self.new_category = response.json()
        else:
            raise Exception("Failed to create new category")

    @task
    def edit_category(self):
        payload = {
            "name": f"UPDATED Category Test+{str(uuid4())}"
        }
        response = self.client.put(f"/product/category/{self.new_category['id']}", json=payload, headers=self.headers)
        if response.status_code == 200:
            self.edited_category = response.json()
        else:
            raise Exception("Failed to edit category")

    @task
    def category_exist_in_all_categories(self):
        response = self.client.get(f"/product/category")

        # Check if the edited category exists in the list of all categories
        category_list = response.json()['categories']
        is_exist = False
        for category in category_list:
            if category['id'] == self.edited_category['id']:
                is_exist = True
                break

        if response.status_code == 200:
            if not is_exist:
                raise Exception("Edited category does not exist in the list of all categories")
            else:
                self.category_exist = True
        else:
            raise Exception("Failed to get category")

    @task
    def create_new_product(self):
        payload = {
            "name": f"iPad+{str(uuid4())}",
            "description": "Apple iPad 2021",
            "price":  10000000,
            "quantity_available": 10,
            "category_id": self.new_category['id']
        }
        response = self.client.post("/product", json=payload, headers=self.headers)
        if response.status_code == 201:
            self.new_product = response.json()
        else:
            raise Exception("Failed to create new product")

    @task
    def edit_product(self):
        payload = {
            "name": f"UPDATED iPad+{str(uuid4())}",
        }
        response = self.client.put(f"/product/{self.new_product['id']}", json=payload, headers=self.headers)
        if response.status_code == 200:
            self.edited_product = response.json()
        else:
            raise Exception("Failed to edit product")

    @task
    def get_product_information(self):
        response = self.client.get(f"/product/{self.edited_product['id']}")
        if response.status_code != 200:
            raise Exception("Failed to get product information")
        else:
            self.product_info = response.json()

    @task
    def product_exist_in_all_products(self):
        response = self.client.get("/product")

        # Check if the edited product exists in the list of all products
        product_list = response.json()['products']
        is_exist = False
        for product in product_list:
            if product['id'] == self.edited_product['id']:
                is_exist = True
                break

        if response.status_code == 200:
            if not is_exist:
                raise Exception("Edited product does not exist in the list of all products")
            else:
                self.product_exist = True
        else:
            raise Exception("Failed to get product")

    @task
    def delete_product(self):
        response = self.client.delete(f"/product/{self.edited_product['id']}", headers=self.headers)

        if response.status_code != 200:
            raise Exception("Failed to delete product")
        else:
            self.product_deleted = False

    @task
    def delete_category(self):
        response = self.client.delete(f"/product/category/{self.edited_category['id']}", headers=self.headers)

        if response.status_code != 200:
            raise Exception("Failed to delete category")

class ProductsMicroserviceUser(HttpUser):
    host = PRODUCTS_MS_BASE_URL
    tasks = [TestProductsMicroserviceAsTenant]
    wait_time = constant(0.5)