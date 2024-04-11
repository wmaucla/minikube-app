from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Wait time between requests, in seconds

    @task
    def access_docs(self):
        self.client.get("/docs")

    @task
    def get_user_data(self):
        self.client.get("/get_user_data/account.ef517fe2035046c28edb1b012acc20b6")