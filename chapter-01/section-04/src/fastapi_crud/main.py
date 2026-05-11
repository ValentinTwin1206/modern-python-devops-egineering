"""Minimal FastAPI CRUD API for the Pipenv showcase."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Items API", version="1.0.0")


class Item(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    price: float = Field(ge=0)


_items: dict[int, Item] = {}
_next_id: int = 1


@app.get("/items")
def list_items() -> dict[int, Item]:
    return _items


@app.post("/items", status_code=201)
def create_item(item: Item) -> dict[str, int | Item]:
    global _next_id
    item_id = _next_id
    _next_id += 1
    _items[item_id] = item
    return {"id": item_id, "item": item}


@app.get("/items/{item_id}")
def read_item(item_id: int) -> Item:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return _items[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    if _items.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail="Item not found")


def main() -> None:
    uvicorn.run("fastapi_crud.main:app", host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
