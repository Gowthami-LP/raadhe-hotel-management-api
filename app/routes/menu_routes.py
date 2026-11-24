from datetime import UTC, datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from app.database.connection import database
from app.schemas.menu_schema import MenuItemCreate, MenuItemUpdate

router = APIRouter(prefix="/menu", tags=["Menu Management"])
menu_collection = database["menu_items"]


def convert_menu_item(item):
    item["id"] = str(item.pop("_id"))
    return item


def parse_object_id(item_id: str) -> ObjectId:
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid menu item ID",
        )
    return ObjectId(item_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_menu_item(menu: MenuItemCreate):
    menu_data = menu.model_dump()
    menu_data["created_at"] = datetime.now(UTC)
    result = menu_collection.insert_one(menu_data)
    menu_data["_id"] = result.inserted_id
    return convert_menu_item(menu_data)


@router.get("/")
def get_menu_items():
    return [convert_menu_item(item) for item in menu_collection.find()]


@router.get("/{item_id}")
def get_menu_item(item_id: str):
    item = menu_collection.find_one({"_id": parse_object_id(item_id)})
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return convert_menu_item(item)


@router.patch("/{item_id}")
def update_menu_item(item_id: str, menu: MenuItemUpdate):
    update_data = menu.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one menu item field must be provided",
        )

    item = menu_collection.find_one_and_update(
        {"_id": parse_object_id(item_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return convert_menu_item(item)


@router.delete("/{item_id}")
def delete_menu_item(item_id: str):
    result = menu_collection.delete_one({"_id": parse_object_id(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return {"message": "Menu item has been deleted successfully"}
