#!/usr/bin/env python3
"""Headless Bot2 worker for Project Brain allocation cycles.

Reachability is observational only. A runtime PASS requires exact allocation
lineage plus a real input artifact whose bytes match the allocated SHA-256.
Missing execution prerequisites are HOLD, never PASS.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.request,threading
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

REPO=os.getenv('COORDINATION_REPO','xsmbv23/Project_Brain_AI')
BRANCH=os.getenv('COORDINATION_BRANCH','main')
POLL=int(os.getenv('POLL_SECONDS','60'))
PORT=int(os.getenv('PORT','10000'))
ARTIFACT_ROOT=Path(os.getenv('ARTIFACT_ROOT','runtime/artifacts')).resolve()
LAST={"status":"STARTING"}
RESULT={"status":"STARTING"}

def get(path):
    u=f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}'
    r=urllib.request.Request(u,headers={'User-Agent':'bot2-quant-headless/lineage-v2'})
    return urllib.request.urlopen(r,timeout=20).read().decode()

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def poll():
    global LAST,RESULT
    try:
        raw=get('coordination/worker_allocation_v2.json')
        allocation_sha=hashlib.sha256(raw.encode()).hexdigest()
        outer=json.loads(raw)
        alloc=json.loads(outer['content']) if isinstance(outer.get('content'),str) else outer
        task=alloc.get('workers',{}).get('BOT2_QUANT',{})
        nxt=json.loads(get('state/next_action.json'))
        if isinstance(nxt.get('content'),str):
            nxt=json.loads(nxt['content'])

        execution={
            'allocation_id':alloc.get('allocation_id'),
            'cycle_id':alloc.get('cycle_id'),
            'task_id':task.get('task_id'),
            'task_type':task.get('task_type'),
            'worker_id':'BOT2_QUANT',
            'input_artifact':task.get('input_artifact'),
            'input_sha256':task.get('input_sha256'),
            'model_version':task.get('model_version'),
        }
        missing=[k for k,v in execution.items() if not v]
        artifact_ok=False
        artifact_error=None
        if not missing:
            candidate=(ARTIFACT_ROOT / str(execution['input_artifact'])).resolve()
            if candidate != ARTIFACT_ROOT and ARTIFACT_ROOT not in candidate.parents:
                artifact_error='INPUT_ARTIFACT_PATH_ESCAPE'
            elif not candidate.is_file():
                artifact_error='INPUT_ARTIFACT_MISSING'
            elif sha256(candidate).lower()!=str(execution['input_sha256']).lower():
                artifact_error='INPUT_SHA256_MISMATCH'
            else:
                artifact_ok=True

        LAST={
            'status':'ALLOCATION_OBSERVED',
            'worker':'BOT2_QUANT',
            'allocation_id':alloc.get('allocation_id'),
            'cycle_id':alloc.get('cycle_id'),
            'task':task.get('action',''),
            'allocation_sha256':allocation_sha,
            'authority':'BOT1_ONLY',
            'promotion':'DENY',
            'canonical_mutation':'FORBIDDEN',
            'observed_at':datetime.now(timezone.utc).isoformat(),
        }
        RESULT={
            'schema':'worker-runtime-receipt/v2',
            'receipt_type':'WORKER_RUNTIME_RECEIPT',
            **execution,
            'allocation_sha256':allocation_sha,
            'checks':{
                'allocation_present':bool(alloc.get('allocation_id')),
                'cycle_present':bool(alloc.get('cycle_id')),
                'canonical_next_action_present':bool(nxt),
                'execution_lineage_complete':not missing,
                'input_artifact_integrity':artifact_ok,
            },
            'status':'PASS' if not missing and artifact_ok and bool(nxt) else 'HOLD',
            'promotion':'DENY',
            'canonical_mutation':'FORBIDDEN',
            'observed_at':datetime.now(timezone.utc).isoformat(),
        }
        if missing: RESULT['missing_fields']=missing
        if artifact_error: RESULT['error_code']=artifact_error
        print(json.dumps(RESULT,sort_keys=True),flush=True)
    except Exception as e:
        RESULT={'schema':'worker-runtime-receipt/v2','receipt_type':'WORKER_RUNTIME_RECEIPT','worker_id':'BOT2_QUANT','status':'HOLD','error_code':type(e).__name__,'promotion':'DENY','canonical_mutation':'FORBIDDEN','observed_at':datetime.now(timezone.utc).isoformat()}
        print(json.dumps(RESULT,sort_keys=True),flush=True)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/health','/healthz','/') or self.path=='/result':
            payload=RESULT if self.path=='/result' else LAST
            b=json.dumps(payload,separators=(',',':')).encode()
            self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_response(404); self.end_headers()
    def log_message(self,*a): pass

if __name__=='__main__':
    s=ThreadingHTTPServer(('0.0.0.0',PORT),H)
    def loop():
        while True:
            poll(); time.sleep(POLL)
    threading.Thread(target=loop,daemon=True).start()
    print(json.dumps({'status':'HTTP_READY','worker':'BOT2_QUANT','port':PORT}),flush=True)
    s.serve_forever()
