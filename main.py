from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from logging_context import LoggingContextRoute


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


@app.get("/exception")
def occur_exception():
    raise HTTPException(status_code=500, detail='GET error!')


@app.post("/exception")
def occur_exception_post():
    raise HTTPException(status_code=500, detail='POST error!')
