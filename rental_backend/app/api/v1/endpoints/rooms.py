from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import Role, PaymentStatus
from app.schemas.room import RoomOut, RoomStatusCard
from app.crud.rooms import list_rooms, list_empty_rooms, get_room
from app.crud.payments import get_payment
from app.utils.qrcode_utils import make_qr_png_bytes
from app.utils.date_key import to_date_key
from app.models.water import Water
from app.models.electric import Electric
from app.schemas.room import RoomBillInfo
from app.utils.date_key import to_date_key, prev_month_key


router = APIRouter(prefix="/rooms")

@router.get("", response_model=list[RoomOut])
def all_rooms(db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    return list_rooms(db)

@router.get("/empty", response_model=list[RoomOut])
def empty_rooms(db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    return list_empty_rooms(db)

@router.get("/status-cards", response_model=list[RoomStatusCard])
def room_status_cards(date_key: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    if date_key is None:
        date_key = to_date_key(date.today())

    cards: list[RoomStatusCard] = []
    for r in list_rooms(db):
        rp = get_payment(db, r.room_no, date_key)

        # No row yet -> treat as OPENING
        if rp is None:
            cards.append(RoomStatusCard(
                room_no=r.room_no,
                color="white",
                status_text="OPENING",
                debt=r.debt,
                remaining=r.price + r.debt,
            ))
            continue

        if rp.status == "OPENING":
            cards.append(RoomStatusCard(r.room_no, "white", "OPENING", r.debt, rp.remaining))
        elif rp.status == "IN_PROGRESS":
            cards.append(RoomStatusCard(r.room_no, "blue", "IN_PROGRESS", r.debt, rp.remaining))
        elif rp.status == "ACCEPTED":
            cards.append(RoomStatusCard(r.room_no, "green", "ACCEPTED", 0.0, 0.0))
        elif rp.status == "DEBT":
            cards.append(RoomStatusCard(r.room_no, "red", "DEBT", r.debt, rp.remaining))
        else:
            # fallback for old data
            cards.append(RoomStatusCard(r.room_no, "white", rp.status, r.debt, rp.remaining))

    return cards


@router.get("/{room_no}/qr")
def room_qr(room_no: str, db: Session = Depends(get_db), _=Depends(require_roles(Role.owner, Role.admin))):
    # Put any deep-link you want here. For now, encode room_no only.
    _ = get_room(db, room_no)
    png = make_qr_png_bytes(f"room:{room_no}")
    return Response(content=png, media_type="image/png")

@router.get("/{room_no}/bill", response_model=RoomBillInfo)
def room_bill_info(
    room_no: str,
    date_key: str,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.owner, Role.admin)),
):
    room = get_room(db, room_no)
    prev_key = prev_month_key(date_key)

    # ---- WATER (use readings)
    prev_water = (
        db.query(Water)
        .filter(Water.room_no == room_no, Water.date_key == prev_key)
        .order_by(desc(Water.report_date), desc(Water.id))
        .first()
    )
    cur_water = (
        db.query(Water)
        .filter(Water.room_no == room_no, Water.date_key == date_key)
        .order_by(desc(Water.report_date), desc(Water.id))
        .first()
    )

    prev_water_num = prev_water.current_num if prev_water else None
    cur_water_num = cur_water.current_num if cur_water else None

    # usage + price rule: (new - previous) * 2500
    water_usage = 0
    if cur_water_num is not None:
        base = prev_water_num if prev_water_num is not None else 0
        water_usage = max(0, cur_water_num - base)
    total_water_price_khr = float(water_usage * 2500)

    # ---- ELECTRICITY (use readings + stored price)
    prev_elec = (
        db.query(Electric)
        .filter(Electric.room_no == room_no, Electric.date_key == prev_key)
        .order_by(desc(Electric.report_date), desc(Electric.id))
        .first()
    )
    cur_elec = (
        db.query(Electric)
        .filter(Electric.room_no == room_no, Electric.date_key == date_key)
        .order_by(desc(Electric.report_date), desc(Electric.id))
        .first()
    )

    prev_elec_num = prev_elec.current_num if prev_elec else None
    cur_elec_num = cur_elec.current_num if cur_elec else None

    # total electricity price for the month (KHR) from DB
    total_electricity_price_khr = (
        db.query(func.coalesce(func.sum(Electric.price), 0.0))
        .filter(Electric.room_no == room_no, Electric.date_key == date_key)
        .scalar()
        or 0.0
    )
    total_electricity_price_khr = float(total_electricity_price_khr)

    # ---- TOTALS
    # totals in KHR: water + electric + (room_price_usd * 4000)
    total_khr = total_water_price_khr + total_electricity_price_khr + room.price

    # totals in USD: room_price_usd + (water + electric)/4000
    total_usd = total_khr / 4000

    return RoomBillInfo(
        room_no=room.room_no,
        room_price_usd=float(room.price),

        previous_month_water=prev_water_num,
        current_month_water=cur_water_num,
        total_water_usage=int(water_usage),
        total_water_price_khr=float(total_water_price_khr),

        previous_month_electricity=prev_elec_num,
        current_month_electricity=cur_elec_num,
        total_electricity_price_khr=float(total_electricity_price_khr),

        total_usd=float(total_usd),
        total_khr=float(total_khr),
    )
