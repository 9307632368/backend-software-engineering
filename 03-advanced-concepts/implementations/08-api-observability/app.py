"""Middleware for request IDs and small in-memory metrics, with JSON logs."""
import json
import logging
import threading
import time
import uuid
from collections import Counter
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

log = logging.getLogger('backend.lab')
if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)
    log.setLevel(logging.INFO)

def create_app(clock=None):
    api = FastAPI(title='API Observability Lab')
    clock = clock or time.monotonic
    counts = Counter()
    durations_ms = []
    lock = threading.Lock()

    @api.middleware('http')
    async def observe(request: Request, call_next):
        request_id = uuid.uuid4().hex  # never accept an unvalidated client-supplied ID
        started = clock()
        try:
            response = await call_next(request)
        except Exception:
            log.exception(json.dumps({'event':'unhandled_error','request_id':request_id}))
            response = JSONResponse(status_code=500,content={'detail':'Internal server error'})
        duration = max(0, clock()-started)*1000
        response.headers['X-Request-ID'] = request_id
        # Route template in metrics is safer than literal paths with high-cardinality IDs.
        route = request.scope.get('route')
        path_label = getattr(route,'path','unknown')
        with lock:
            counts[(request.method,path_label,response.status_code)] += 1
            durations_ms.append(duration)
        log.info(json.dumps({'event':'request_finished','request_id':request_id,
                             'method':request.method,'route':path_label,
                             'status':response.status_code,'duration_ms':round(duration,2)}))
        return response

    @api.get('/health/live')
    def live():
        return {'status':'alive'}

    @api.get('/health/ready')
    def ready():
        # Only reports process readiness in this demo (no external dependencies).
        return {'status':'ready'}

    @api.get('/work/{item_id}')
    def work(item_id: int):
        if item_id <= 0:
            raise HTTPException(404,'No such item')
        return {'item_id':item_id,'result':'processed'}

    @api.get('/metrics')
    def metrics():
        with lock:
            items=[{'method':method,'route':route,'status':status,'count':count}
                   for (method,route,status),count in counts.items()]
            total=len(durations_ms)
            avg=round(sum(durations_ms)/total,2) if total else 0
        return {'requests':items,'observed_requests':total,'average_duration_ms':avg}

    return api

app = create_app()
