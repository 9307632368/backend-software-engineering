"""Idempotent event processor, with reconciliation for early webhooks."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


class StoreError(Exception):
    def __init__(self, code: int, message: str):
        self.code, self.message = code, message
        super().__init__(message)


class PaymentStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _db(self):
        db = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _setup(self):
        with self._db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
              CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                amount_cents INTEGER NOT NULL CHECK(amount_cents>0),
                state TEXT NOT NULL DEFAULT 'pending'
                    CHECK(state IN ('pending','succeeded','failed'))
              );
              CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                fingerprint TEXT NOT NULL,
                payment_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                outcome TEXT NOT NULL
                  CHECK(outcome IN ('applied','ignored','awaiting_payment'))
              );
            """)

    def create_payment(self, payment_id: str, amount_cents: int):
        with self._db() as db:
            try:
                db.execute("INSERT INTO payments(payment_id,amount_cents) VALUES(?,?)",
                           (payment_id, amount_cents))
            except sqlite3.IntegrityError as exc:
                raise StoreError(409, "Payment already exists") from exc
        return {"payment_id":payment_id,"amount_cents":amount_cents,"state":"pending"}

    def get_payment(self, payment_id: str):
        with self._db() as db:
            row=db.execute("SELECT * FROM payments WHERE payment_id=?",(payment_id,)).fetchone()
        if not row: raise StoreError(404,"Payment not found")
        return dict(row)

    @staticmethod
    def _apply(db, payment_id, amount_cents, event_type):
        payment=db.execute("SELECT * FROM payments WHERE payment_id=?",(payment_id,)).fetchone()
        if not payment: return "awaiting_payment"
        if payment["amount_cents"] != amount_cents:
            raise StoreError(409,"Webhook amount differs from original payment")
        if payment["state"] != "pending":
            return "ignored"  # terminal states cannot be overwritten by late events
        new_state="succeeded" if event_type == "payment.succeeded" else "failed"
        db.execute("UPDATE payments SET state=? WHERE payment_id=?",(new_state,payment_id))
        return "applied"

    def ingest_event(self, event: dict) -> tuple[str, bool]:
        fingerprint=hashlib.sha256(json.dumps(event,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        db=self._db()
        try:
            db.execute("BEGIN IMMEDIATE")
            old=db.execute("SELECT fingerprint,outcome FROM events WHERE event_id=?",
                           (event["event_id"],)).fetchone()
            if old:
                if old["fingerprint"] != fingerprint:
                    raise StoreError(409,"Same event ID used for different payload")
                db.execute("COMMIT")
                return old["outcome"], True
            outcome=self._apply(db,event["payment_id"],event["amount_cents"],event["type"])
            db.execute("INSERT INTO events VALUES (?,?,?,?,?,?)",
                       (event["event_id"],fingerprint,event["payment_id"],
                        event["type"],event["amount_cents"],outcome))
            db.execute("COMMIT")
            return outcome, False
        except Exception:
            if db.in_transaction: db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def reconcile(self) -> dict:
        """Retry early deliveries; call explicitly. Can also be a scheduled task."""
        db=self._db()
        try:
            db.execute("BEGIN IMMEDIATE")
            events=db.execute("SELECT * FROM events WHERE outcome='awaiting_payment' ORDER BY event_id").fetchall()
            applied=0
            still_pending=0
            ignored=0
            for event in events:
                # An invalid amount remains queued for investigation, rather than
                # silently applying the wrong amount or blocking other events.
                try:
                    outcome=self._apply(db,event["payment_id"],event["amount_cents"],event["event_type"])
                except StoreError:
                    still_pending+=1
                    continue
                if outcome == "awaiting_payment":
                    still_pending+=1
                else:
                    db.execute("UPDATE events SET outcome=? WHERE event_id=?",(outcome,event["event_id"]))
                    applied+=int(outcome=="applied")
                    ignored+=int(outcome=="ignored")
            db.execute("COMMIT")
            return {"applied":applied,"ignored":ignored,"awaiting_payment":still_pending}
        except Exception:
            if db.in_transaction:db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def stats(self):
        with self._db() as db:
            return {r["outcome"]:r["count"] for r in db.execute(
                "SELECT outcome,COUNT(*) AS count FROM events GROUP BY outcome")}
