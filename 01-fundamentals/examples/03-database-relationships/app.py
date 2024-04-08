"""Users, products, and orders with real foreign-key relationships."""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    price_cents: Mapped[int] = mapped_column()
    stock: Mapped[int] = mapped_column()

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")

class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price_cents: Mapped[int] = mapped_column()
    order: Mapped["Order"] = relationship(back_populates="lines")

class UserInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)

class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price_cents: int = Field(gt=0)
    stock: int = Field(ge=0)

class OrderInput(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0)

def create_app(database_url: str = "sqlite:///shop_example.db") -> FastAPI:
    api = FastAPI(title="Database Relationships Example")
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    def get_db():
        with SessionLocal() as session:
            yield session

    @api.post("/users", status_code=201)
    def create_user(payload: UserInput, db: Session = Depends(get_db)):
        user = User(name=payload.name)
        db.add(user); db.commit(); db.refresh(user)
        return {"id": user.id, "name": user.name}

    @api.post("/products", status_code=201)
    def create_product(payload: ProductInput, db: Session = Depends(get_db)):
        if db.scalar(select(Product).where(Product.name == payload.name)):
            raise HTTPException(409, "Product name already exists")
        product = Product(**payload.model_dump())
        db.add(product); db.commit(); db.refresh(product)
        return {"id": product.id, "name": product.name, "stock": product.stock}

    @api.post("/orders", status_code=201)
    def create_order(payload: OrderInput, db: Session = Depends(get_db)):
        if not db.get(User, payload.user_id):
            raise HTTPException(404, "User not found")
        product = db.get(Product, payload.product_id)
        if product is None:
            raise HTTPException(404, "Product not found")
        if product.stock < payload.quantity:
            raise HTTPException(409, "Insufficient stock")
        product.stock -= payload.quantity
        order = Order(user_id=payload.user_id)
        order.lines.append(OrderLine(product_id=product.id, quantity=payload.quantity, unit_price_cents=product.price_cents))
        db.add(order); db.commit(); db.refresh(order)
        return {"id": order.id, "total_cents": payload.quantity * product.price_cents}

    @api.get("/users/{user_id}/orders")
    def list_orders(user_id: int, db: Session = Depends(get_db)):
        if not db.get(User, user_id):
            raise HTTPException(404, "User not found")
        orders = db.scalars(select(Order).where(Order.user_id == user_id)).all()
        return [{"order_id": order.id,
                 "lines": [{"product_id": line.product_id, "quantity": line.quantity, "unit_price_cents": line.unit_price_cents} for line in order.lines]}
                for order in orders]

    return api

app = create_app()
