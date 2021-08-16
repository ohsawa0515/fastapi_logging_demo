from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


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
