from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import router as auth_router
from .core import configure_database, current_user, get_db, require_role, settings
from .models import Booking, BookingEvent, Service, Slot, User

class ServiceInput(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=500)

class SlotInput(BaseModel):
    starts_at: datetime

class BookingInput(BaseModel):
    slot_id: int = Field(gt=0)

def canonical(dt: datetime):
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise HTTPException(422, "Timezone offset required; use Z for UTC")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def view_booking(booking: Booking, db: Session):
    slot = db.get(Slot, booking.slot_id)
    return {"id": booking.id, "user_id": booking.user_id, "slot_id": booking.slot_id,
            "status": booking.status, "starts_at": slot.starts_at, "service_id": slot.service_id}

def create_app(database_url=None, jwt_secret=None):
    app = FastAPI(title="Appointment Booking API", version="1.0")
    url, key = settings(database_url, jwt_secret)
    app.state.jwt_secret = key
    configure_database(app, url)
    app.include_router(auth_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/services", status_code=201)
    def add_service(data: ServiceInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        service = Service(**data.model_dump())
        db.add(service)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Service name already exists")
        db.refresh(service)
        return {"id": service.id, "name": service.name, "description": service.description}

    @app.get("/services")
    def services(db: Session = Depends(get_db)):
        return [{"id": s.id, "name": s.name, "description": s.description}
                for s in db.scalars(select(Service).order_by(Service.id))]

    @app.post("/services/{service_id}/slots", status_code=201)
    def create_slot(service_id: int, data: SlotInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        if not db.get(Service, service_id):
            raise HTTPException(404, "Service not found")
        moment = canonical(data.starts_at)
        if datetime.strptime(moment, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise HTTPException(422, "New slots must be in the future")
        dt = datetime.fromisoformat(moment.replace("Z", "+00:00"))
        if dt.minute % 30 != 0 or dt.second != 0:
            raise HTTPException(422, "Slots must start on a 30-minute UTC boundary")
        slot = Slot(service_id=service_id, starts_at=moment)
        db.add(slot)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Slot already exists")
        db.refresh(slot)
        return {"id": slot.id, "service_id": slot.service_id, "starts_at": slot.starts_at, "booked": slot.booked}

    @app.get("/services/{service_id}/slots")
    def available_slots(service_id: int, only_available: bool = True, db: Session = Depends(get_db)):
        if not db.get(Service, service_id):
            raise HTTPException(404, "Service not found")
        q = select(Slot).where(Slot.service_id == service_id, Slot.starts_at > datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")).order_by(Slot.starts_at)
        if only_available:
            q = q.where(Slot.booked.is_(False))
        return [{"id": s.id, "starts_at": s.starts_at, "booked": s.booked} for s in db.scalars(q)]

    @app.post("/bookings", status_code=201)
    def reserve(data: BookingInput, request_key: str = Header(min_length=8, max_length=100, alias="Idempotency-Key"),
                user: User = Depends(current_user), db: Session = Depends(get_db)):
        prior = db.scalar(select(Booking).where(Booking.user_id == user.id, Booking.request_key == request_key))
        if prior:
            return view_booking(prior, db)
        slot = db.get(Slot, data.slot_id)
        if slot is None:
            raise HTTPException(404, "Slot not found")
        if slot.starts_at <= datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"):
            raise HTTPException(409, "This slot is in the past")
        # Atomic claim; two clients cannot both change booked=False to True.
        changed = db.execute(update(Slot).where(Slot.id == data.slot_id, Slot.booked.is_(False)).values(booked=True))
        if changed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, "Slot already booked")
        booking = Booking(user_id=user.id, slot_id=slot.id, request_key=request_key, status="confirmed")
        db.add(booking)
        db.flush()
        db.add(BookingEvent(booking_id=booking.id, actor_id=user.id, action="confirmed"))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Booking conflict; check existing booking before retry")
        db.refresh(booking)
        return view_booking(booking, db)

    @app.get("/bookings")
    def bookings(user: User = Depends(current_user), db: Session = Depends(get_db),
                 limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
        q = select(Booking).order_by(Booking.id.desc()).limit(limit).offset(offset)
        if user.role != "admin":
            q = q.where(Booking.user_id == user.id)
        return [view_booking(x, db) for x in db.scalars(q)]

    @app.get("/bookings/{booking_id}")
    def get_booking(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        booking = db.get(Booking, booking_id)
        if booking is None or (user.role != "admin" and booking.user_id != user.id):
            raise HTTPException(404, "Booking not found")
        return view_booking(booking, db)

    @app.post("/bookings/{booking_id}/cancel")
    def cancel(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        booking = db.get(Booking, booking_id)
        if booking is None or (user.role != "admin" and booking.user_id != user.id):
            raise HTTPException(404, "Booking not found")
        slot = db.get(Slot, booking.slot_id)
        if slot.starts_at <= datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"):
            raise HTTPException(409, "Cannot cancel a started/past slot")
        changed = db.execute(update(Booking).where(Booking.id == booking_id, Booking.status == "confirmed").values(status="cancelled"))
        if changed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, "Booking is not confirmed")
        db.execute(update(Slot).where(Slot.id == booking.slot_id).values(booked=False))
        db.add(BookingEvent(booking_id=booking.id, actor_id=user.id, action="cancelled"))
        db.commit()
        return {"id": booking_id, "status": "cancelled"}

    @app.get("/bookings/{booking_id}/events")
    def history(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        booking = db.get(Booking, booking_id)
        if booking is None or (user.role != "admin" and booking.user_id != user.id):
            raise HTTPException(404, "Booking not found")
        return [{"action": e.action, "actor_id": e.actor_id}
                for e in db.scalars(select(BookingEvent).where(BookingEvent.booking_id == booking.id).order_by(BookingEvent.id))]

    return app

app = create_app()
