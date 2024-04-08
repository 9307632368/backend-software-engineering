"""Lesson 05: persistent support tickets using sqlite3 and parameterized SQL."""
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=120)
    priority: str = Field(pattern="^(low|medium|high)$")


class Ticket(BaseModel):
    id: int
    subject: str
    priority: str
    status: str


def init_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tickets (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   subject TEXT NOT NULL,
                   priority TEXT NOT NULL,
                   status TEXT NOT NULL DEFAULT 'open'
               )"""
        )


def get_db(request: Request):
    connection = sqlite3.connect(request.app.state.db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def create_app(db_path: str | Path = "data/support_tickets.db") -> FastAPI:
    target = Path(db_path)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        init_database(target)
        yield

    app = FastAPI(title="Support Tickets | SQLite", lifespan=lifespan)
    app.state.db_path = target

    @app.post("/tickets", response_model=Ticket, status_code=status.HTTP_201_CREATED)
    def create_ticket(payload: TicketCreate, connection: sqlite3.Connection = Depends(get_db)):
        with connection:
            cursor = connection.execute(
                "INSERT INTO tickets (subject, priority) VALUES (?, ?)",
                (payload.subject, payload.priority),
            )
            row = connection.execute(
                "SELECT * FROM tickets WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return dict(row)

    @app.get("/tickets", response_model=list[Ticket])
    def list_tickets(limit: int = Query(default=20, ge=1, le=100),
                     connection: sqlite3.Connection = Depends(get_db)):
        rows = connection.execute("SELECT * FROM tickets ORDER BY id LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    @app.get("/tickets/{ticket_id}", response_model=Ticket)
    def read_ticket(ticket_id: int, connection: sqlite3.Connection = Depends(get_db)):
        row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return dict(row)

    @app.patch("/tickets/{ticket_id}/close", response_model=Ticket)
    def close_ticket(ticket_id: int, connection: sqlite3.Connection = Depends(get_db)):
        with connection:
            cursor = connection.execute(
                "UPDATE tickets SET status = 'closed' WHERE id = ? AND status = 'open'",
                (ticket_id,),
            )
            if cursor.rowcount == 0:
                row = connection.execute("SELECT status FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Ticket not found")
                raise HTTPException(status_code=409, detail="Ticket already closed")
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row)

    @app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_ticket(ticket_id: int, connection: sqlite3.Connection = Depends(get_db)):
        with connection:
            cursor = connection.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Ticket not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
