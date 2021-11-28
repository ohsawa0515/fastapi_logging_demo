import main
from fastapi.testclient import TestClient
from main import app

S3_BUCKET = 'test-bucket-foo'


class MockS3():
    def head(self, bucket, key: str) -> bool:
        return True

    def get(self, bucket, key: str) -> str:
        return "test foo"


client = TestClient(app)
app.dependency_overrides[main.S3] = MockS3


class TestApi:
    def test_hello_world(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["Hello"] == "World"

    def test_get_item(self):
        response = client.get("/items/1234?q=abcd")
        assert response.status_code == 200
        assert response.json() == {
            "item_id": 1234,
            "q": "abcd",
        }

    def test_post_item(self):
        response = client.post("/items/",
                               headers={"Content-Type": "application/json"},
                               json={
                                   "name": "foo",
                                   "price": 1000,
                                   "is_offer": True,
                               })
        assert response.status_code == 200
        assert response.json() == {
            "item_name": "foo",
            "item_price": 1000,
        }

    def test_put_item(self):
        response = client.put("items/1234",
                              headers={"Content-Type": "application/json"},
                              json={
                                  "name": "foo",
                                  "price": 1000,
                                  "is_offer": True,
                              })
        assert response.status_code == 200
        assert response.json() == {
            "item_name": "foo",
            "item_id": 1234,
        }

    def test_get_exception(self):
        response = client.get("/exception")
        assert response.status_code == 500

    def test_post_exception(self):
        response = client.post("/exception")
        assert response.status_code == 500

    def test_exists_file(self):
        response = client.get("/files/exists/foo.txt")
        assert response.status_code == 200
        assert response.json() == {
            "exists": True,
        }

    def test_get_file(self):
        response = client.get("/files/foo.txt")
        assert response.status_code == 200
        assert response.json() == {
            "message": "test foo",
        }

    def test_sleep(self):
        response = client.get("/sleep/3")
        assert response.status_code == 504

    def test_async_sleep(self):
        response = client.get("/async_sleep/3")
        assert response.status_code == 504
