from datetime import date
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

import qrcode

from app.db.session import get_db
from app.api.deps import get_current_user, assert_house_access
from app.models.enums import Role, PaymentStatus
from app.schemas.room import RoomCreate, RoomUpdate, RoomOut, RoomStatusCard, RoomBillInfo
from app.crud.rooms import create_room, list_rooms, list_empty_rooms, get_room
from app.crud.payments import get_payment
from app.models.room import Room
from app.models.water import Water
from app.models.electric import Electric
from app.utils.date_key import to_date_key, prev_month_key, make_room_id

router = APIRouter(prefix="/api/v1/houses/{house_id}/rooms")

from sqlalchemy import exists

@router.put("/{room_id}", response_model=RoomOut)
def update_room(house_id: int, room_id: str, payload: "RoomUpdate", db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")

    r = get_room(db, room_id)
    if r.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    if payload.price_usd is not None:
        r.price_usd = float(payload.price_usd)
    if payload.status is not None:
        r.status = payload.status

    db.commit()
    db.refresh(r)
    return r

@router.delete("/{room_id}")
def delete_room(house_id: int, room_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role != Role.owner.value:
        raise HTTPException(status_code=403, detail="Only owner can delete room")

    r = get_room(db, room_id)
    if r.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    # Prevent delete if there are related records
    from app.models.customer import Customer
    from app.models.room_payment import RoomPayment
    from app.models.water import Water
    from app.models.electric import Electric
    from app.models.issue_ticket import IssueTicket
    from app.models.room_note import RoomNote
    from app.models.user_login import UserLogin

    has_related = (
        db.query(exists().where(Customer.room_id == room_id)).scalar()
        or db.query(exists().where(RoomPayment.room_id == room_id)).scalar()
        or db.query(exists().where(Water.room_id == room_id)).scalar()
        or db.query(exists().where(Electric.room_id == room_id)).scalar()
        or db.query(exists().where(IssueTicket.room_id == room_id)).scalar()
        or db.query(exists().where(RoomNote.room_id == room_id)).scalar()
        or db.query(exists().where(UserLogin.room_id == room_id)).scalar()
    )
    if has_related:
        raise HTTPException(status_code=400, detail="Cannot delete room with related records")

    db.delete(r)
    db.commit()
    return {"ok": True, "deleted": room_id}


@router.post("", response_model=RoomOut)
def add_room(house_id: int, payload: RoomCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    room_id = make_room_id(house_id, payload.room_no.strip())
    r = Room(room_id=room_id, house_id=house_id, room_no=payload.room_no.strip(), price_usd=payload.price_usd)
    return create_room(db, r)

@router.get("", response_model=list[RoomOut])
def all_rooms(house_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    return list_rooms(db, house_id)

@router.get("/empty", response_model=list[RoomOut])
def empty_rooms(house_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    return list_empty_rooms(db, house_id)

@router.get("/status-cards", response_model=list[RoomStatusCard])
def status_cards(house_id: int, date_key: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    if user.role not in (Role.owner.value, Role.admin.value):
        raise HTTPException(status_code=403, detail="Forbidden")
    if date_key is None:
        date_key = to_date_key(date.today())

    cards: list[RoomStatusCard] = []
    for r in list_rooms(db, house_id):
        rp = get_payment(db, r.room_id, date_key)

        # Currency rule:
        # - debt is stored in KHR
        # - room price USD converted to KHR (rate=4000) when combined
        if rp is None:
            remaining_khr = float((r.price_usd * 4000) + float(r.debt or 0.0))
            cards.append(
                RoomStatusCard(
                    room_id=r.room_id,
                    room_no=r.room_no,
                    color="white",
                    status_text="OPENING",
                    payment_status="OPENING",
                    remaining_khr=remaining_khr,
                    remaining_usd=float(remaining_khr / 4000),
                )
            )
            continue

        if rp.status == PaymentStatus.opening.value:
            color = "white"
        elif rp.status == PaymentStatus.in_progress.value:
            color = "blue"
        elif rp.status == PaymentStatus.accepted.value:
            color = "green"
        elif rp.status == PaymentStatus.debt.value:
            color = "red"
        else:
            color = "white"

        remaining_khr = float(rp.remaining_usd)  # remaining_usd column holds KHR (v4.1+)
        cards.append(
            RoomStatusCard(
                room_id=r.room_id,
                room_no=r.room_no,
                color=color,
                status_text=rp.status,
                payment_status=rp.status,
                remaining_khr=remaining_khr,
                remaining_usd=float(remaining_khr / 4000),
            )
        )

    return cards


@router.get("/{room_id}/qr")
def room_qr(house_id: int, room_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    r = get_room(db, room_id)
    if r.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    img = qrcode.make(room_id)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/{room_id}/bill", response_model=RoomBillInfo)
def room_bill(house_id: int, room_id: str, date_key: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    assert_house_access(db, user, house_id)
    r = get_room(db, room_id)
    if r.house_id != house_id:
        raise HTTPException(status_code=404, detail="Room not found in house")

    prev_key = prev_month_key(date_key)

    prev_water = db.query(Water).filter(Water.room_id == room_id, Water.date_key == prev_key).order_by(desc(Water.report_date), desc(Water.id)).first()
    cur_water = db.query(Water).filter(Water.room_id == room_id, Water.date_key == date_key).order_by(desc(Water.report_date), desc(Water.id)).first()

    prev_water_num = prev_water.current_num if prev_water else None
    cur_water_num = cur_water.current_num if cur_water else None

    water_usage = 0
    if cur_water_num is not None:
        base = prev_water_num if prev_water_num is not None else 0
        water_usage = max(0, cur_water_num - base)
    total_water_khr = float(water_usage * 2500)

    prev_elec = db.query(Electric).filter(Electric.room_id == room_id, Electric.date_key == prev_key).order_by(desc(Electric.report_date), desc(Electric.id)).first()
    cur_elec = db.query(Electric).filter(Electric.room_id == room_id, Electric.date_key == date_key).order_by(desc(Electric.report_date), desc(Electric.id)).first()

    prev_elec_num = prev_elec.current_num if prev_elec else None
    cur_elec_num = cur_elec.current_num if cur_elec else None

    total_elect_khr = float(
        db.query(func.coalesce(func.sum(Electric.price_khr), 0.0)).filter(Electric.room_id == room_id, Electric.date_key == date_key).scalar() or 0.0
    )

    room_price_khr = float(r.price_usd * 4000)
    debt_khr = float(r.debt or 0.0)

    total_khr = float(room_price_khr + total_water_khr + total_elect_khr + debt_khr)
    total_usd = float(total_khr / 4000)

    return RoomBillInfo(
        room_id=r.room_id,
        room_no=r.room_no,
        room_price_usd=float(r.price_usd),
        previous_month_water=prev_water_num,
        current_month_water=cur_water_num,
        total_water_usage=int(water_usage),
        total_water_price_khr=total_water_khr,
        previous_month_electricity=prev_elec_num,
        current_month_electricity=cur_elec_num,
        total_electricity_price_khr=total_elect_khr,
        total_usd=total_usd,
        total_khr=total_khr,
    )
