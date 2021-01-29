import time
import datetime
import sys
import json
from logging import getLogger, StreamHandler, DEBUG
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel


logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
logger.addHandler(handler)
logger.setLevel(DEBUG)


class LoggingContextRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = round(time.time() - before, 4)

            record = {}
            time_local = datetime.datetime.fromtimestamp(before)
            record["time_local"] = time_local.strftime("%Y/%m/%d %H:%M:%S%Z")
            if await request.body():
                record["request_body"] = (await request.body()).decode("utf-8")
            record["request_headers"] = {
                k.decode("utf-8"): v.decode("utf-8") for (k, v) in request.headers.raw
            }
            record["remote_addr"] = request.client.host
            record["request_uri"] = request.url.path
            record["request_method"] = request.method
            record["request_time"] = str(duration)
            record["status"] = response.status_code
            record["response_body"] = response.body.decode("utf-8")
            record["response_headers"] = {
                k.decode("utf-8"): v.decode("utf-8") for (k, v) in response.headers.raw
            }
            logger.info(json.dumps(record))
            return response

        return custom_route_handler


app = FastAPI()
app.router.route_class = LoggingContextRoute


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


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
