from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import router as auth_router
from .core import configure_database, current_user, get_db, require_role, settings
from .models import Audit, Order, OrderItem, Product, User

class NewProduct(BaseModel):
    sku: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    price_cents: int = Field(gt=0)
    stock: int = Field(ge=0)

class StockAdjustment(BaseModel):
    delta: int = Field(ge=0, le=100000)  # replenishment only in this API

class CartLine(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)

class Checkout(BaseModel):
    items: list[CartLine] = Field(min_length=1, max_length=50)

def view_order(order):
    return {"id": order.id, "user_id": order.user_id, "status": order.status,
            "total_cents": order.total_cents, "items": [
                {"product_id": line.product_id, "quantity": line.quantity, "unit_price_cents": line.unit_price_cents}
                for line in order.items]}

def create_app(database_url=None, jwt_secret=None):
    app = FastAPI(title="Order Management API", version="1.0", description="Local learning project — no live payment processing")
    url, key = settings(database_url, jwt_secret)
    app.state.jwt_secret = key
    configure_database(app, url)
    app.include_router(auth_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/products")
    def list_products(db: Session = Depends(get_db)):
        return [{"id": p.id, "sku": p.sku, "name": p.name, "price_cents": p.price_cents, "stock": p.stock}
                for p in db.scalars(select(Product).order_by(Product.id)).all()]

    @app.post("/products", status_code=201)
    def add_product(data: NewProduct, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        row = Product(**data.model_dump())
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "SKU already exists")
        db.refresh(row)
        return {"id": row.id, **data.model_dump()}

    @app.post("/products/{product_id}/replenish")
    def replenish(product_id: int, data: StockAdjustment, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        result = db.execute(update(Product).where(Product.id == product_id).values(stock=Product.stock + data.delta))
        if result.rowcount != 1:
            raise HTTPException(404, "Product not found")
        db.commit()
        return {"id": product_id, "stock": db.get(Product, product_id).stock}

    @app.post("/orders", status_code=201)
    def place_order(data: Checkout, idempotency_key: str = Header(min_length=8, max_length=100, alias="Idempotency-Key"),
                    user: User = Depends(current_user), db: Session = Depends(get_db)):
        prior = db.scalar(select(Order).where(Order.user_id == user.id, Order.idempotency_key == idempotency_key))
        if prior:
            return view_order(prior)
        if len({i.product_id for i in data.items}) != len(data.items):
            raise HTTPException(422, "Duplicate product IDs in the same checkout")
        total, lines = 0, []
        for line in data.items:
            product = db.get(Product, line.product_id)
            if not product:
                raise HTTPException(404, f"Product {line.product_id} missing")
            # Conditional UPDATE is atomic and avoids read-check-write oversell.
            changed = db.execute(update(Product).where(Product.id == product.id, Product.stock >= line.quantity)
                                 .values(stock=Product.stock - line.quantity))
            if changed.rowcount != 1:
                db.rollback()
                raise HTTPException(409, f"Insufficient stock for product {line.product_id}")
            total += product.price_cents * line.quantity
            lines.append(OrderItem(product_id=product.id, quantity=line.quantity, unit_price_cents=product.price_cents))
        order = Order(user_id=user.id, idempotency_key=idempotency_key, status="placed", total_cents=total)
        db.add(order)
        db.flush()
        for item in lines:
            item.order_id = order.id
            db.add(item)
        db.add(Audit(order_id=order.id, actor_id=user.id, event="placed"))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Checkout conflict; fetch existing order before retry")
        db.refresh(order)
        return view_order(order)

    @app.get("/orders")
    def orders(user: User = Depends(current_user), db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
        q = select(Order).order_by(Order.id.desc()).limit(limit).offset(offset)
        if user.role != "admin":
            q = q.where(Order.user_id == user.id)
        return [view_order(o) for o in db.scalars(q).all()]

    @app.get("/orders/{order_id}")
    def get_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        o = db.get(Order, order_id)
        if o is None or (user.role != "admin" and o.user_id != user.id):
            raise HTTPException(404, "Order not found")
        return view_order(o)

    @app.post("/orders/{order_id}/cancel")
    def cancel_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        o = db.get(Order, order_id)
        if o is None or (user.role != "admin" and o.user_id != user.id):
            raise HTTPException(404, "Order not found")
        # Conditional status change prevents repeat restocking for sequential calls.
        changed = db.execute(update(Order).where(Order.id == order_id, Order.status == "placed").values(status="cancelled"))
        if changed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, "Order cannot be cancelled in its current state")
        for line in o.items:
            db.execute(update(Product).where(Product.id == line.product_id).values(stock=Product.stock + line.quantity))
        db.add(Audit(order_id=o.id, actor_id=user.id, event="cancelled"))
        db.commit()
        return {"id": order_id, "status": "cancelled"}

    @app.post("/orders/{order_id}/fulfill")
    def fulfill(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        changed = db.execute(update(Order).where(Order.id == order_id, Order.status == "placed").values(status="fulfilled"))
        if changed.rowcount != 1:
            raise HTTPException(409, "Order not found or not in placed state")
        db.add(Audit(actor_id=user.id, order_id=order_id, event="fulfilled"))
        db.commit()
        return {"id": order_id, "status": "fulfilled"}

    @app.get("/orders/{order_id}/audit")
    def audit(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        if not db.get(Order, order_id):
            raise HTTPException(404, "Order not found")
        return [{"event": x.event, "actor_id": x.actor_id} for x in db.scalars(select(Audit).where(Audit.order_id == order_id).order_by(Audit.id))]

    return app

app = create_app()
