import boto3
from fastapi.testclient import TestClient
from main import app
from moto import mock_s3

S3_BUCKET = 'test-bucket-foo'

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

    @mock_s3
    def test_get_file(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=S3_BUCKET,
                                CreateBucketConfiguration={
                                    'LocationConstraint': 'ap-northeast-1'
                                })
        s3_client.upload_file("tests/foo.txt", S3_BUCKET, "foo.txt")
        response = client.get("/files/foo.txt")
        assert response.status_code == 200
