from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from app.database.connection import database
from app.schemas.reservation_schema import (
    ReservationCreate,
    ReservationStatusUpdate,
)


router = APIRouter(prefix="/reservations", tags=["Table Reservations"])
reservations_collection = database["reservations"]


def convert_reservation(reservation):
    reservation["id"] = str(reservation.pop("_id"))
    return reservation


def parse_object_id(reservation_id: str) -> ObjectId:
    if not ObjectId.is_valid(reservation_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reservation ID",
        )
    return ObjectId(reservation_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: ReservationCreate):
    reservation_date = reservation.reservation_date.isoformat()
    reservation_time = reservation.reservation_time.strftime("%H:%M")

    existing_reservation = reservations_collection.find_one(
        {
            "reservation_date": reservation_date,
            "reservation_time": reservation_time,
            "table_number": reservation.table_number,
        }
    )
    if existing_reservation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Table is already reserved for this date and time",
        )

    reservation_data = reservation.model_dump()
    reservation_data["reservation_date"] = reservation_date
    reservation_data["reservation_time"] = reservation_time
    reservation_data["status"] = "confirmed"
    reservation_data["created_at"] = datetime.now(timezone.utc)

    result = reservations_collection.insert_one(reservation_data)
    reservation_data["_id"] = result.inserted_id
    return convert_reservation(reservation_data)


@router.get("/")
def get_reservations():
    return [
        convert_reservation(reservation)
        for reservation in reservations_collection.find()
    ]


@router.get("/{reservation_id}")
def get_reservation(reservation_id: str):
    reservation = reservations_collection.find_one(
        {"_id": parse_object_id(reservation_id)}
    )
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )
    return convert_reservation(reservation)


@router.patch("/{reservation_id}/status")
def update_reservation_status(
    reservation_id: str,
    reservation_status: ReservationStatusUpdate,
):
    reservation = reservations_collection.find_one_and_update(
        {"_id": parse_object_id(reservation_id)},
        {"$set": {"status": reservation_status.status}},
        return_document=ReturnDocument.AFTER,
    )
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )
    return convert_reservation(reservation)
