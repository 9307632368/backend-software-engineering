"""Interview practice 06: local SQLite-backed job retry and dead-letter flow.

A deliberately single-worker training example, not a distributed task queue.
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class JobIn(BaseModel):
    task: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


def create_app(db_path: str = 'jobs.sqlite3',
               handler: Callable[[str, dict], None] | None = None,
               max_attempts: int = 3) -> FastAPI:
    if max_attempts < 1:
        raise ValueError('max_attempts must be >= 1')
    app = FastAPI(title='Interview 06 - Retry and Dead Letter Jobs')
    db_path = str(Path(db_path))
    handler = handler or (lambda task, payload: None)
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, payload TEXT NOT NULL,
          state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, error TEXT NOT NULL DEFAULT '')''')
        conn.commit()

    @app.post('/jobs', status_code=201)
    def enqueue(job: JobIn):
        with closing(sqlite3.connect(db_path)) as conn:
            job_id = conn.execute('INSERT INTO jobs(task,payload,state) VALUES(?,?,?)',
                                  (job.task, json.dumps(job.payload), 'pending')).lastrowid
            conn.commit()
        return {'job_id': job_id, 'state': 'pending'}

    @app.post('/worker/run-once')
    def run_once():
        # A single synchronous demo worker, intentionally not multi-worker safe.
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM jobs WHERE state='pending' ORDER BY id LIMIT 1").fetchone()
            if row is None:
                return {'processed': False}
            attempts = row['attempts'] + 1
            try:
                handler(row['task'], json.loads(row['payload']))
                state, error = 'completed', ''
            except Exception as exc:
                state = 'dead_letter' if attempts >= max_attempts else 'pending'
                error = str(exc)[:200]
            conn.execute('UPDATE jobs SET attempts=?,state=?,error=? WHERE id=?',
                         (attempts, state, error, row['id']))
            conn.commit()
            return {'processed': True, 'job_id': row['id'], 'state': state, 'attempts': attempts}

    @app.get('/jobs/{job_id}')
    def get_job(job_id: int):
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT id,task,state,attempts,error FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Unknown job')
        return dict(row)

    return app


app = create_app()
