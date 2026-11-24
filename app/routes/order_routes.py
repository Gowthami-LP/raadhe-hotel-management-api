from datetime import UTC, datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from app.database.connection import database
from app.schemas.order_schema import OrderCreate, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Food Orders"])
orders_collection = database["food_orders"]
menu_collection = database["menu_items"]


def convert_order(order):
    order["id"] = str(order.pop("_id"))
    return order


def parse_object_id(order_id: str) -> ObjectId:
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID",
        )
    return ObjectId(order_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    order_items = []
    total_amount = 0

    for requested_item in order.items:
        if not ObjectId.is_valid(requested_item.menu_item_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu item ID",
            )

        menu_item = menu_collection.find_one(
            {"_id": ObjectId(requested_item.menu_item_id)}
        )
        if menu_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )
        if not menu_item.get("is_available", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item '{menu_item['name']}' is unavailable",
            )

        subtotal = menu_item["price"] * requested_item.quantity
        total_amount += subtotal
        order_items.append(
            {
                "menu_item_id": str(menu_item["_id"]),
                "name": menu_item["name"],
                "price": menu_item["price"],
                "quantity": requested_item.quantity,
                "subtotal": subtotal,
            }
        )

    order_data = order.model_dump(exclude={"items"})
    order_data.update(
        {
            "items": order_items,
            "total_amount": total_amount,
            "status": "placed",
            "created_at": datetime.now(UTC),
        }
    )
    result = orders_collection.insert_one(order_data)
    order_data["_id"] = result.inserted_id
    return convert_order(order_data)


@router.get("/")
def get_orders():
    return [convert_order(order) for order in orders_collection.find()]


@router.get("/{order_id}")
def get_order(order_id: str):
    order = orders_collection.find_one({"_id": parse_object_id(order_id)})
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return convert_order(order)


@router.patch("/{order_id}/status")
def update_order_status(order_id: str, order_status: OrderStatusUpdate):
    order = orders_collection.find_one_and_update(
        {"_id": parse_object_id(order_id)},
        {"$set": {"status": order_status.status}},
        return_document=ReturnDocument.AFTER,
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return convert_order(order)
