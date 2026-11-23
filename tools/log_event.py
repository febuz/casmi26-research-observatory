#!/usr/bin/env python3
"""Log a structured, public-safe run event. Never accepts arbitrary log text."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,re,uuid,fcntl
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--component',required=True);ap.add_argument('--run-id',required=True)
ap.add_argument('--status',choices=['started','completed','failed','rejected','blocked'],required=True)
ap.add_argument('--metric',choices=['public_mrr25','dev_mrr25','stress_mrr25','fingerprint_rmse','reward_rmse','top1_accuracy','runtime_seconds'])
ap.add_argument('--value',type=float);ap.add_argument('--baseline',type=float)
a=ap.parse_args()
allowed={c['id'] for c in json.loads((root/'docs/snapshot.json').read_text())['components']}
if a.component not in allowed:ap.error('Unknown component ID')
if not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',a.run_id):ap.error('Run ID must be a public-safe slug, max 80 characters')
if (a.metric is None)!=(a.value is None):ap.error('metric and value must be supplied together')
import math
if any(v is not None and not math.isfinite(v) for v in [a.value,a.baseline]):ap.error('Metric must be finite')
commit=subprocess.check_output(['git','-C','/Users/develuse/Documents/CASMI2026','rev-parse','HEAD'],text=True).strip()
e={'event_id':str(uuid.uuid4()),'time':datetime.now(timezone.utc).isoformat(),'type':'run_'+a.status,'component_ids':[a.component],'commit':commit,'run_id':a.run_id,'metric':a.metric,'value':a.value,'baseline':a.baseline,'message':'Gestructureerde runmelding: '+a.status+'. Resultaatbereik volgt uit het metriekveld; dit is geen onafhankelijke review.'}
p=root/'.local/process_events.jsonl';p.parent.mkdir(exist_ok=True)
with p.open('a') as f:
 fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps(e)+'\n')
print(e['event_id'])
