"""A small durable job queue with worker leases and bounded retries."""
import secrets
import sqlite3
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class NewJob(BaseModel):
    task: str = Field(min_length=1, max_length=80)
    data: str = Field(default='', max_length=500)

class Receipt(BaseModel):
    lease_token: str = Field(min_length=1)

class Failure(Receipt):
    reason: str = Field(min_length=1, max_length=120)

def create_app(db_path='jobs.sqlite3', clock=None, max_attempts=3, lease_seconds=30):
    if max_attempts < 1 or lease_seconds <= 0:
        raise ValueError('Invalid queue settings')
    api = FastAPI(title='SQLite Leased Job Queue')
    clock = clock or time.time

    def connect():
        db = sqlite3.connect(str(db_path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, task TEXT NOT NULL, data TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
            lease_token TEXT, leased_until REAL, last_error TEXT, created_at REAL NOT NULL)""")

    @api.post('/jobs', status_code=201)
    def submit(job: NewJob):
        identifier = str(uuid.uuid4())
        with connect() as db:
            db.execute('INSERT INTO jobs (id,task,data,created_at) VALUES (?,?,?,?)',
                       (identifier,job.task,job.data,clock()))
        return {'id':identifier,'status':'pending'}

    @api.get('/jobs/{job_id}')
    def detail(job_id: str):
        with connect() as db:
            row=db.execute("""SELECT id,task,data,status,attempts,leased_until,last_error
                              FROM jobs WHERE id=?""",(job_id,)).fetchone()
        if row is None:
            raise HTTPException(404,'Job not found')
        return dict(row)  # lease token is intentionally never returned here

    @api.post('/worker/claim')
    def claim():
        now = clock()
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')  # serialize claims from separate workers
            # Failed workers may leave a timed-out lease.
            db.execute("""UPDATE jobs SET status='dead',lease_token=NULL,leased_until=NULL,
                         last_error='Lease expired after final attempt'
                         WHERE status='processing' AND leased_until<=? AND attempts>=?""",
                       (now,max_attempts))
            db.execute("""UPDATE jobs SET status='pending',lease_token=NULL,leased_until=NULL
                         WHERE status='processing' AND leased_until<=? AND attempts<?""",
                       (now,max_attempts))
            job = db.execute("""SELECT * FROM jobs WHERE status='pending'
                                ORDER BY created_at ASC, rowid ASC LIMIT 1""").fetchone()
            if job is None:
                return {'job':None}
            token = secrets.token_urlsafe(24)
            db.execute("""UPDATE jobs SET status='processing',attempts=attempts+1,
                         lease_token=?,leased_until=? WHERE id=?""",
                       (token,now+lease_seconds,job['id']))
            return {'job': {'id':job['id'], 'task':job['task'], 'data':job['data'],
                            'attempts':job['attempts']+1,'lease_token':token,
                            'leased_until':now+lease_seconds}}

    def validate_lease(db, job_id, token):
        row = db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
        if row is None:
            raise HTTPException(404,'Job not found')
        if row['status']!='processing' or row['lease_token']!=token or row['leased_until']<=clock():
            raise HTTPException(409,'Lease missing, expired or no longer held')
        return row

    @api.post('/worker/{job_id}/complete')
    def complete(job_id: str, body: Receipt):
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            validate_lease(db,job_id,body.lease_token)
            db.execute("""UPDATE jobs SET status='done',lease_token=NULL,leased_until=NULL
                         WHERE id=?""",(job_id,))
        return {'id':job_id,'status':'done'}

    @api.post('/worker/{job_id}/fail')
    def fail(job_id: str, body: Failure):
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = validate_lease(db,job_id,body.lease_token)
            new_status = 'dead' if row['attempts']>=max_attempts else 'pending'
            db.execute("""UPDATE jobs SET status=?,lease_token=NULL,
                         leased_until=NULL,last_error=? WHERE id=?""",
                       (new_status,body.reason,job_id))
        return {'id':job_id,'status':new_status}

    return api

app=create_app()
