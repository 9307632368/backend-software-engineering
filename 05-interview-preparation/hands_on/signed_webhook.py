"""Interview practice 05: verify HMAC signatures and reject replayed webhook IDs."""
import hashlib
import hmac
import json
import time
from threading import Lock
from typing import Callable

from fastapi import FastAPI, Header, HTTPException, Request


def signature(secret: str, timestamp: int, raw_body: bytes) -> str:
    message = str(timestamp).encode() + b'.' + raw_body
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def create_app(secret: str = 'change-me-locally', clock: Callable[[], float] = time.time,
               max_skew_seconds: int = 300) -> FastAPI:
    app = FastAPI(title='Interview 05 - Signed Webhooks')
    seen_ids: set[str] = set()  # demo only: a persistent store is required in production
    lock = Lock()

    @app.post('/webhook')
    async def webhook(request: Request, x_webhook_timestamp: str = Header(),
                      x_webhook_signature: str = Header()):
        try:
            ts = int(x_webhook_timestamp)
        except ValueError:
            raise HTTPException(400, 'Timestamp must be an integer')
        if abs(clock() - ts) > max_skew_seconds:
            raise HTTPException(401, 'Webhook timestamp is outside the allowed window')
        body = await request.body()
        expected = signature(secret, ts, body)
        if not hmac.compare_digest(x_webhook_signature, expected):
            raise HTTPException(401, 'Bad signature')
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(400, 'Body must be JSON')
        if not isinstance(payload, dict) or not isinstance(payload.get('event_id'), str) or not payload['event_id']:
            raise HTTPException(422, 'Non-empty event_id required')
        with lock:
            if payload['event_id'] in seen_ids:
                return {'status': 'duplicate', 'event_id': payload['event_id']}
            seen_ids.add(payload['event_id'])
        return {'status': 'accepted', 'event_id': payload['event_id']}

    return app


app = create_app()
