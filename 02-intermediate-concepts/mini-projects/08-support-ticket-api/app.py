"""Support tickets: persistence, simple state machine and an audit timeline.

X-Actor-Role is only a learning stub, NOT actual authentication.
"""
import sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

class TicketIn(BaseModel):
    customer_email: str = Field(min_length=5,max_length=120)
    subject: str = Field(min_length=3,max_length=120)
    description: str = Field(min_length=10,max_length=1000)

class Assignment(BaseModel):
    assignee: str = Field(min_length=2,max_length=80)

class Transition(BaseModel):
    status: str

ALLOWED={'open':{'in_progress','closed'},'in_progress':{'resolved','closed'},'resolved':{'closed','in_progress'},'closed':set()}

def create_app(db_file='tickets.db'):
    app=FastAPI(title='2024 — Support Ticket Mini Project')
    def db():
        c=sqlite3.connect(db_file,timeout=10,isolation_level=None)
        c.row_factory=sqlite3.Row
        return c
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tickets (
          id INTEGER PRIMARY KEY AUTOINCREMENT, customer_email TEXT NOT NULL,
          subject TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL,
          assignee TEXT, created_at TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL,
          action TEXT NOT NULL, actor TEXT NOT NULL, created_at TEXT NOT NULL
        )""")

    def now(): return datetime.now(timezone.utc).isoformat()
    def require_role(role):
        if role not in {'agent','admin'}:
            raise HTTPException(403,'Agent or admin role required (demo header)')

    def record(conn,ticket_id,action,actor):
        conn.execute('INSERT INTO events(ticket_id,action,actor,created_at) VALUES (?,?,?,?)',
                     (ticket_id,action,actor,now()))

    @app.post('/tickets',status_code=201)
    def create(data:TicketIn):
        if '@' not in data.customer_email: raise HTTPException(422,'Invalid demo email address')
        with db() as c:
            try:
                c.execute('BEGIN IMMEDIATE')
                cursor=c.execute("""INSERT INTO tickets (customer_email,subject,description,status,created_at)
                VALUES (?,?,?,'open',?)""", (data.customer_email,data.subject,data.description,now()))
                record(c,cursor.lastrowid,'created','customer')
                row=dict(c.execute('SELECT * FROM tickets WHERE id=?',(cursor.lastrowid,)).fetchone())
                c.commit()
                return row
            except BaseException:
                c.rollback();raise

    @app.get('/tickets')
    def list_tickets(status:str | None=None,limit:int=Query(default=30,ge=1,le=100)):
        with db() as c:
            if status:
                rows=c.execute('SELECT * FROM tickets WHERE status=? ORDER BY id DESC LIMIT ?',(status,limit)).fetchall()
            else:
                rows=c.execute('SELECT * FROM tickets ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        return {'items':[dict(x) for x in rows]}

    @app.get('/tickets/{ticket_id}')
    def get(ticket_id:int):
        with db() as c:
            row=c.execute('SELECT * FROM tickets WHERE id=?',(ticket_id,)).fetchone()
        if not row: raise HTTPException(404,'Ticket not found')
        return dict(row)

    @app.patch('/tickets/{ticket_id}/assign')
    def assign(ticket_id:int,data:Assignment,x_actor_role:str | None=Header(default=None),x_actor:str | None=Header(default=None)):
        require_role(x_actor_role)
        with db() as c:
            try:
                c.execute('BEGIN IMMEDIATE')
                row=c.execute('SELECT status FROM tickets WHERE id=?',(ticket_id,)).fetchone()
                if not row: raise HTTPException(404,'Ticket not found')
                if row['status']=='closed': raise HTTPException(409,'Cannot assign a closed ticket')
                c.execute('UPDATE tickets SET assignee=? WHERE id=?',(data.assignee,ticket_id))
                record(c,ticket_id,'assigned:'+data.assignee,x_actor or 'demo-agent')
                c.commit()
            except BaseException:
                c.rollback();raise
        return {'ticket_id':ticket_id,'assignee':data.assignee}

    @app.patch('/tickets/{ticket_id}/status')
    def transition(ticket_id:int,data:Transition,x_actor_role:str | None=Header(default=None),x_actor:str | None=Header(default=None)):
        require_role(x_actor_role)
        with db() as c:
            try:
                c.execute('BEGIN IMMEDIATE')
                row=c.execute('SELECT status FROM tickets WHERE id=?',(ticket_id,)).fetchone()
                if not row: raise HTTPException(404,'Ticket not found')
                if data.status not in ALLOWED[row['status']]:
                    raise HTTPException(409,f"Cannot change {row['status']} to {data.status}")
                c.execute('UPDATE tickets SET status=? WHERE id=?',(data.status,ticket_id))
                record(c,ticket_id,'status:'+data.status,x_actor or 'demo-agent')
                c.commit()
            except BaseException:
                c.rollback();raise
        return {'ticket_id':ticket_id,'status':data.status}

    @app.get('/tickets/{ticket_id}/history')
    def history(ticket_id:int,x_actor_role:str | None=Header(default=None)):
        require_role(x_actor_role)
        with db() as c:
            if not c.execute('SELECT id FROM tickets WHERE id=?',(ticket_id,)).fetchone():
                raise HTTPException(404,'Ticket not found')
            rows=c.execute('SELECT * FROM events WHERE ticket_id=? ORDER BY id',(ticket_id,)).fetchall()
        return {'events':[dict(row) for row in rows]}

    return app

app=create_app()
