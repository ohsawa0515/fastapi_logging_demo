import boto3
import os
import time
import asyncio
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from logging_context import LoggingContextRoute
from botocore.exceptions import ClientError
from timeout_middleware import TimeoutMiddleware

REQUEST_TIMEOUT = os.getenv("REQUEST_TIMEOUT", 5)
S3_BUCKET = 'shu0515-fastapi-test'

app = FastAPI()
app.router.route_class = LoggingContextRoute
app.add_middleware(TimeoutMiddleware, timeout=REQUEST_TIMEOUT)


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


class S3():
    def __init__(self):
        self.client = boto3.client("s3")

    def head(self, bucket, key: str) -> bool:
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise e

    def get(self, bucket, key: str) -> str:
        try:
            body = self.client.get_object(Bucket=bucket, Key=key)['Body'].read()
            return body.decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return ""
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


@app.get("/files/exists/{name}")
def get_exists_file(name: str, s3: S3 = Depends()):
    try:
        result = s3.head(S3_BUCKET, name)
        return {"exists": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{name}")
def get_file(name: str, s3: S3 = Depends()):
    try:
        result = s3.get(S3_BUCKET, name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sleep/{wait_time}")
def wait_for(wait_time: int):
    time.sleep(wait_time)
    return {"Wait time(sec)": wait_time}


@app.get("/async_sleep/{wait_time}")
async def async_wait_for(wait_time: int):
    await asyncio.sleep(wait_time)
    return {"Wait time(sec)": wait_time}
