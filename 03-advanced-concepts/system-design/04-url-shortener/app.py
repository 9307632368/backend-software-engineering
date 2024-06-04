"""Small link-shortening API. Deliberately excludes public internet deployment."""
import secrets
import sqlite3
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyHttpUrl, Field

class NewLink(BaseModel):
    url: AnyHttpUrl
    ttl_seconds: int = Field(default=86400, ge=1, le=2592000)

def create_app(db_path='links.sqlite3', clock=None, token_generator=None):
    api = FastAPI(title='URL Shortener Design Exercise')
    clock = clock or time.time
    token_generator = token_generator or (lambda: secrets.token_urlsafe(6))
    def connect():
        db = sqlite3.connect(str(db_path), timeout=5)
        db.row_factory = sqlite3.Row
        return db
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS links (
            code TEXT PRIMARY KEY, url TEXT NOT NULL,
            expires_at REAL NOT NULL, hits INTEGER NOT NULL DEFAULT 0)""")

    @api.post('/links', status_code=201)
    def new_link(body: NewLink):
        # Collision-safe: SQLite enforces uniqueness even if two writers race.
        for _ in range(5):
            code = token_generator()
            try:
                with connect() as db:
                    db.execute('INSERT INTO links (code, url, expires_at) VALUES (?, ?, ?)',
                               (code, str(body.url), clock() + body.ttl_seconds))
                return {'code': code, 'short_path': f'/r/{code}'}
            except sqlite3.IntegrityError:
                continue
        raise HTTPException(503, 'Could not allocate a unique short code')

    @api.get('/r/{code}')
    def redirect(code: str):
        with connect() as db:
            row = db.execute('SELECT url, expires_at FROM links WHERE code = ?', (code,)).fetchone()
            if row is None:
                raise HTTPException(404, 'Unknown code')
            if clock() >= row['expires_at']:
                raise HTTPException(410, 'Link expired')
            db.execute('UPDATE links SET hits=hits+1 WHERE code=?', (code,))
        return RedirectResponse(row['url'], status_code=307)

    @api.get('/links/{code}/stats')
    def stats(code: str):
        with connect() as db:
            row = db.execute('SELECT code, expires_at, hits FROM links WHERE code=?', (code,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Unknown code')
        return dict(row)

    return api

app = create_app()
