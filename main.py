import time
import sys
import json
from logging import getLogger, StreamHandler, DEBUG
from fastapi import FastAPI, Request
from pydantic import BaseModel


logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
logger.addHandler(handler)
logger.setLevel(DEBUG)

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 4)

    record = {}
    record["request_time"] = str(process_time)
    record["remote_addr"] = request.client.host
    record["server_port"] = request.client.port
    record["request_uri"] = request.url.path
    record["request_method"] = request.method
    record["status"] = response.status_code
    record["response_headers"] = {
        k.decode("utf-8"): v.decode("utf-8")
        for (k, v) in response.headers.raw
    }
    logger.info(json.dumps(record))
    return response


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
