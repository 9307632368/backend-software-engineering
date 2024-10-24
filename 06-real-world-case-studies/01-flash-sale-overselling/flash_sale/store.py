"""SQLite reservation store. A single transaction decides stock and idempotency."""
from __future__ import annotations

import hashlib
import sqlite3
import uuid
from pathlib import Path


class StoreError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class FlashSaleStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    stock INTEGER NOT NULL CHECK(stock >= 0),
                    price_cents INTEGER NOT NULL CHECK(price_cents >= 0)
                );
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    sku TEXT NOT NULL REFERENCES products(sku),
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    total_cents INTEGER NOT NULL,
                    UNIQUE(client_id, idempotency_key)
                );
            """)

    def add_product(self, sku: str, name: str, stock: int, price_cents: int) -> None:
        """Seed test data; do not expose as an unprotected public API."""
        if stock < 0 or price_cents < 0:
            raise ValueError("Stock and price must be nonnegative")
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO products(sku,name,stock,price_cents) VALUES(?,?,?,?)",
                (sku, name, stock, price_cents),
            )

    def get_product(self, sku: str) -> dict:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
        if row is None:
            raise StoreError(404, "Product not found")
        return dict(row)

    def get_order(self, order_id: str) -> dict:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT order_id,client_id,sku,quantity,total_cents FROM orders WHERE order_id=?",
                (order_id,),
            ).fetchone()
        if row is None:
            raise StoreError(404, "Order not found")
        return dict(row)

    def place_order(self, client_id: str, key: str, sku: str, quantity: int) -> tuple[dict, bool]:
        """Return (order, replayed). No external payment is performed here."""
        request_hash = hashlib.sha256(f"{sku}:{quantity}".encode()).hexdigest()
        conn = self._connection()
        try:
            # BEGIN IMMEDIATE: reserve the writer lock before checking stock.
            conn.execute("BEGIN IMMEDIATE")
            previous = conn.execute(
                "SELECT * FROM orders WHERE client_id=? AND idempotency_key=?", (client_id, key)
            ).fetchone()
            if previous is not None:
                if previous["request_hash"] != request_hash:
                    raise StoreError(409, "Idempotency key reused with different order details")
                output = {field: previous[field] for field in
                          ("order_id", "client_id", "sku", "quantity", "total_cents")}
                conn.execute("COMMIT")
                return output, True

            product = conn.execute("SELECT price_cents FROM products WHERE sku=?", (sku,)).fetchone()
            if product is None:
                raise StoreError(404, "Product not found")

            updated = conn.execute(
                "UPDATE products SET stock=stock-? WHERE sku=? AND stock>=?",
                (quantity, sku, quantity),
            ).rowcount
            if updated != 1:
                raise StoreError(409, "Not enough stock")
            order_id = str(uuid.uuid4())
            total = product["price_cents"] * quantity
            conn.execute(
                "INSERT INTO orders VALUES(?,?,?,?,?,?,?)",
                (order_id, client_id, key, request_hash, sku, quantity, total),
            )
            conn.execute("COMMIT")
            return dict(order_id=order_id, client_id=client_id, sku=sku,
                        quantity=quantity, total_cents=total), False
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
