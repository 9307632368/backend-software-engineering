from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import router as auth_router
from .core import configure_database, current_user, get_db, require_role, settings, hash_password
from .models import Comment, Ticket, TicketEvent, User

class NewAgent(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class NewTicket(BaseModel):
    subject: str = Field(min_length=4, max_length=150)
    description: str = Field(min_length=10, max_length=3000)
    priority: Literal["low", "normal", "high"] = "normal"

class NewComment(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    internal: bool = False

class StatusUpdate(BaseModel):
    status: Literal["in_progress", "resolved", "reopened", "closed"]

class Assignment(BaseModel):
    agent_id: int = Field(gt=0)

allowed = {
    "open": {"in_progress", "closed"},
    "in_progress": {"resolved", "closed"},
    "resolved": {"reopened", "closed"},
    "reopened": {"in_progress", "closed"},
    "closed": set(),
}

def visible(ticket: Ticket, user: User):
    return user.role in ("admin", "agent") or ticket.owner_id == user.id

def present(ticket: Ticket, user: User):
    staff = user.role in ("admin", "agent")
    return {"id": ticket.id, "owner_id": ticket.owner_id, "assigned_to": ticket.assigned_to,
            "subject": ticket.subject, "description": ticket.description,
            "status": ticket.status, "priority": ticket.priority,
            "comments": [{"id": c.id, "author_id": c.author_id, "body": c.body, "internal": c.internal}
                         for c in sorted(ticket.comments, key=lambda x: x.id) if staff or not c.internal]}

def create_app(database_url=None, jwt_secret=None):
    app = FastAPI(title="Support Desk API", version="1.0")
    url, secret = settings(database_url, jwt_secret)
    app.state.jwt_secret = secret
    configure_database(app, url)
    app.include_router(auth_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/staff/agents", status_code=201)
    def create_agent(data: NewAgent, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin")
        agent = User(email=str(data.email).lower(), password_hash=hash_password(data.password), role="agent")
        db.add(agent)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Email already registered")
        db.refresh(agent)
        return {"id": agent.id, "email": agent.email, "role": agent.role}

    @app.post("/tickets", status_code=201)
    def create_ticket(data: NewTicket, user: User = Depends(current_user), db: Session = Depends(get_db)):
        ticket = Ticket(owner_id=user.id, **data.model_dump())
        db.add(ticket)
        db.flush()
        db.add(TicketEvent(ticket_id=ticket.id, actor_id=user.id, action="created"))
        db.commit()
        db.refresh(ticket)
        return present(ticket, user)

    @app.get("/tickets")
    def list_tickets(user: User = Depends(current_user), db: Session = Depends(get_db),
                     limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                     status: str | None = None):
        query = select(Ticket).order_by(Ticket.id.desc()).limit(limit).offset(offset)
        if user.role not in ("admin", "agent"):
            query = query.where(Ticket.owner_id == user.id)
        if status:
            query = query.where(Ticket.status == status)
        return [present(t, user) for t in db.scalars(query).all()]

    @app.get("/tickets/{ticket_id}")
    def ticket_detail(ticket_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        ticket = db.get(Ticket, ticket_id)
        if ticket is None or not visible(ticket, user):
            raise HTTPException(404, "Ticket not found")
        return present(ticket, user)

    @app.post("/tickets/{ticket_id}/comments", status_code=201)
    def comment(ticket_id: int, data: NewComment, user: User = Depends(current_user), db: Session = Depends(get_db)):
        ticket = db.get(Ticket, ticket_id)
        if ticket is None or not visible(ticket, user):
            raise HTTPException(404, "Ticket not found")
        if data.internal:
            require_role(user, "admin", "agent")
        if ticket.status == "closed":
            raise HTTPException(409, "Closed ticket cannot receive new comments")
        row = Comment(ticket_id=ticket.id, author_id=user.id, body=data.body, internal=data.internal)
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"id": row.id, "ticket_id": ticket.id, "internal": row.internal, "body": row.body}

    @app.patch("/tickets/{ticket_id}/assign")
    def assign(ticket_id: int, data: Assignment, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin", "agent")
        ticket = db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(404, "Ticket not found")
        agent = db.get(User, data.agent_id)
        if not agent or agent.role not in ("admin", "agent"):
            raise HTTPException(422, "Assignee must be an agent/admin")
        if ticket.status == "closed":
            raise HTTPException(409, "Closed ticket cannot be assigned")
        ticket.assigned_to = agent.id
        db.add(TicketEvent(ticket_id=ticket.id, actor_id=user.id, action=f"assigned:{agent.id}"))
        db.commit()
        return {"id": ticket.id, "assigned_to": agent.id}

    @app.patch("/tickets/{ticket_id}/status")
    def change_status(ticket_id: int, data: StatusUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin", "agent")
        ticket = db.get(Ticket, ticket_id)
        if ticket is None:
            raise HTTPException(404, "Ticket not found")
        if data.status not in allowed[ticket.status]:
            raise HTTPException(409, f"Cannot transition {ticket.status} to {data.status}")
        before = ticket.status
        ticket.status = data.status
        db.add(TicketEvent(ticket_id=ticket.id, actor_id=user.id, action=f"status:{before}->{data.status}"))
        db.commit()
        return {"id": ticket.id, "status": ticket.status}

    @app.get("/tickets/{ticket_id}/events")
    def event_history(ticket_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
        require_role(user, "admin", "agent")
        if not db.get(Ticket, ticket_id):
            raise HTTPException(404, "Ticket not found")
        return [{"actor_id": e.actor_id, "action": e.action}
                for e in db.scalars(select(TicketEvent).where(TicketEvent.ticket_id == ticket_id).order_by(TicketEvent.id))]

    return app

app = create_app()
