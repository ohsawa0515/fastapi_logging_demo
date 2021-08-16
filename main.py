import boto3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from logging_context import LoggingContextRoute
from boto3_type_annotations.s3 import Client as S3Client
from botocore.exceptions import ClientError


S3_BUCKET = 'shu0515-fastapi-test'

app = FastAPI()
app.router.route_class = LoggingContextRoute


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


class S3Hoge():
    def head(self, bucket, key: str) -> bool:
        try:
            client = boto3.client("s3")
            client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise e


def s3_client() -> S3Client:
    return boto3.client("s3")


def s3_head(client: S3Client, bucket, key: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/items/")
def post_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/exception")
def occur_exception():
    raise HTTPException(status_code=500, detail='GET error!')


@app.post("/exception")
def occur_exception_post():
    raise HTTPException(status_code=500, detail='POST error!')


@app.get("/files/{name}")
def get_file(name: str, s3_hoge: S3Hoge = Depends()):
    try:
        result = s3_hoge.head(S3_BUCKET, name)
        return {"exists": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
