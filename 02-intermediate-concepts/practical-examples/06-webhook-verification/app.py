"""HMAC-SHA256 webhook demo; persistent duplicate detection."""
import hashlib
import hmac
import json
import os
import sqlite3
from fastapi import FastAPI, Header, Request, HTTPException
from pydantic import BaseModel, ValidationError

class Event(BaseModel):
    type: str
    resource_id: str

def create_app(db_file='webhooks.db', secret=None):
    app=FastAPI(title='2024 — Signed Webhooks')
    def db():
        conn=sqlite3.connect(db_file,timeout=10,isolation_level=None)
        conn.row_factory=sqlite3.Row
        return conn
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS processed_events (
            event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, resource_id TEXT NOT NULL
        )""")

    @app.post('/webhooks/events')
    async def ingest(request:Request,x_event_id: str | None = Header(default=None), x_signature: str | None = Header(default=None)):
        key=secret if secret is not None else os.getenv('WEBHOOK_SECRET')
        if not key: raise HTTPException(503,'WEBHOOK_SECRET is not configured')
        if not x_event_id or len(x_event_id)>100 or not x_signature:
            raise HTTPException(400,'Event ID and signature are required')
        raw=await request.body()
        if len(raw)>64*1024: raise HTTPException(413,'Payload too large')
        expected='sha256='+hmac.new(key.encode(),raw,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,x_signature):
            raise HTTPException(401,'Invalid signature')
        try:
            event=Event.model_validate_json(raw)
        except ValidationError:
            raise HTTPException(422,'Expected type and resource_id')
        if not event.type or not event.resource_id: raise HTTPException(422,'Missing event fields')
        with db() as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                previous=conn.execute('SELECT * FROM processed_events WHERE event_id=?',(x_event_id,)).fetchone()
                if previous:
                    if previous['event_type']!=event.type or previous['resource_id']!=event.resource_id:
                        raise HTTPException(409,'Event ID reused with different content')
                    conn.commit()
                    return {'result':'duplicate','event_id':x_event_id}
                conn.execute('INSERT INTO processed_events VALUES (?,?,?)',(x_event_id,event.type,event.resource_id))
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
        return {'result':'recorded','event_id':x_event_id}
    return app

app=create_app()
