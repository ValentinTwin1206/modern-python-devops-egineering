from fastapi_crud.main import Item, create_item, delete_item, list_items, read_item


def setup_function() -> None:
    from fastapi_crud import main as m

    m._items.clear()
    m._next_id = 1


def test_create_and_read_item() -> None:
    created = create_item(Item(name="Book", price=9.5))
    assert created["id"] == 1
    assert read_item(1) == Item(name="Book", price=9.5)


def test_list_and_delete_item() -> None:
    create_item(Item(name="Pen", price=1.0))
    assert list(list_items().keys()) == [1]
    delete_item(1)
    assert list_items() == {}
