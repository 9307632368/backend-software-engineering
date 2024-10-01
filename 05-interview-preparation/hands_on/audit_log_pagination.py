"""Interview practice 04: filtered pagination using parameterized SQL."""
import math
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class AuditIn(BaseModel):
    actor: str = Field(min_length=1, max_length=80)
    event_type: str = Field(min_length=1, max_length=50)
    details: str = Field(default='', max_length=500)


def create_app(db_path: str = 'audit.sqlite3') -> FastAPI:
    app = FastAPI(title='Interview 04 - Audit Log Pagination')
    db_path = str(Path(db_path))
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL, event_type TEXT NOT NULL, details TEXT NOT NULL)''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type, id)')
        conn.commit()

    @app.post('/events', status_code=201)
    def create_event(event: AuditIn):
        with closing(sqlite3.connect(db_path)) as conn:
            new_id = conn.execute('INSERT INTO events(actor,event_type,details) VALUES(?,?,?)',
                                  (event.actor, event.event_type, event.details)).lastrowid
            conn.commit()
        return {'id': new_id, **event.model_dump()}

    @app.get('/events')
    def list_events(page: int = Query(ge=1, default=1), size: int = Query(ge=1, le=50, default=10),
                    event_type: str | None = Query(default=None)):
        clause = ' WHERE event_type=?' if event_type is not None else ''
        params = (event_type,) if event_type is not None else ()
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            total = conn.execute('SELECT COUNT(*) FROM events' + clause, params).fetchone()[0]
            rows = conn.execute('SELECT * FROM events' + clause + ' ORDER BY id DESC LIMIT ? OFFSET ?',
                                params + (size, (page - 1) * size)).fetchall()
        return {'page': page, 'size': size, 'total': total, 'pages': math.ceil(total / size),
                'items': [dict(r) for r in rows]}

    return app


app = create_app()
