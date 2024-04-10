"""Email templates + FastAPI BackgroundTasks. Demo sender does not send real mail."""
from dataclasses import dataclass
from string import Template
from uuid import uuid4
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

TEMPLATES = {
    "welcome": ("Welcome to the demo", Template("Hi $name, thanks for signing up!")),
    "order": ("Order update", Template("Hi $name, your order $order_id is now being prepared.")),
}

class NotificationInput(BaseModel):
    to_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    name: str = Field(min_length=1, max_length=80)
    template: str
    order_id: str | None = None

@dataclass
class Message:
    message_id: str
    to_email: str
    subject: str
    body: str

class DemoSender:
    def __init__(self):
        self.sent: list[Message] = []

    def send(self, message: Message) -> None:
        # Later: replace this class with an SMTP or provider-specific adapter.
        self.sent.append(message)

def create_app(sender: DemoSender | None = None) -> FastAPI:
    api = FastAPI(title="Email Notification Example")
    mailer = sender if sender is not None else DemoSender()
    api.state.mailer = mailer

    @api.post("/notifications", status_code=202)
    def queue_notification(payload: NotificationInput, background: BackgroundTasks):
        if payload.template not in TEMPLATES:
            raise HTTPException(422, "Unknown template")
        if payload.template == "order" and not payload.order_id:
            raise HTTPException(422, "order_id is required for the order template")
        subject, text = TEMPLATES[payload.template]
        body = text.substitute(name=payload.name, order_id=payload.order_id or "")
        message = Message(uuid4().hex, payload.to_email, subject, body)
        # Sending occurs after the response in normal ASGI execution.
        background.add_task(mailer.send, message)
        return {"message_id": message.message_id, "status": "queued", "delivery": "demo-only"}

    @api.get("/demo-outbox")
    def outbox():
        # This development-only endpoint should not be exposed on a public service.
        return [{"message_id": m.message_id, "to_email": m.to_email, "subject": m.subject, "body": m.body}
                for m in mailer.sent]

    return api

app = create_app()
