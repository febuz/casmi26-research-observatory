#!/usr/bin/env python3
"""Allowlisted public research snapshot; never copy raw logs, tokens or data rows."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,argparse,time
ROOT=Path(__file__).resolve().parents[1];SRC=Path('/Users/develuse/Documents/CASMI2026')
STATE=ROOT/'.local';STATE.mkdir(exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git','-C',str(SRC),*args],text=True).strip()
def read(p):return json.loads((SRC/p).read_text())
COMPONENTS=[
 ('SRC-01','Bronnen en catalogi','data','SourceVersion · DatasetVersion · Asset','Bronrechten, NIST-herkomst en versies afzonderlijk beoordelen.','experiments/final_notebook/source_registry.json'),
 ('SPC-01','Spectra en query','data','MolecularIdentity · Spectrum · Query','Ruwe pieken behouden; identiteit niet uit voorspelling invullen.','docs/monografie_20261119/hoofdstukken/102_datamodel_en_datagovernance.md'),
 ('TRF-01','Piekcuratie en ionvorm','transform','TransformVersion · TransformExecution','Parserfouten en niet-ondersteunde adducts expliciet loggen.','experiments/final_notebook/casmi_final.py'),
 ('CAT-01','Kandidaatgeneratie','transform','CandidateSetVersion · CandidateOrigin','Deduplicatie mag bronrelaties niet verwijderen.','experiments/final_notebook/casmi_final.py'),
 ('ML-01','Encoder en fingerprint','model','ModelVersion · Checkpoint · ExposureEvent','Train- en selectieblootstelling bepalen evaluatiegeschiktheid.','experiments/final_notebook/fp_score.py'),
 ('ML-02','Ensemble en rangschikking','model','EnsembleMember · CandidateFeature · RankedPrediction','Gewichten en normalisatiegroepen versieerbaar bewaren.','experiments/final_notebook/casmi_final.py'),
 ('POL-01','Contextueel routebeleid','model','PolicyVersion · Action · Reward','Alleen diagnostiek; geërfd panelprobleem blokkeert promotie.','experiments/context_policy_20261123/policy.py'),
 ('VAL-01','Evaluatie en attributie','evidence','PanelVersion · EffectComparison · MetricValue','MRR, RMSE en top-1 hebben verschillende betekenissen.','reports/context_policy_20261123/out/context_policy.json'),
 ('SUB-01','Officiële inzending','evidence','Submission · SubmissionScore · ClaimEvidence','Publiek totaalcontrast is geen geïsoleerd causaal effect.','reports/transformation_lineage_20261123/lineage.json'),
 ('GOV-01','Governance en herkomst','governance','SourceReview · EligibilityAssessment · Incident','Logische integratie deels ontwerp; geen volledige runtimehandhaving.','experiments/final_notebook/source_policy.py')]
def build():
 line=read('reports/transformation_lineage_20261123/lineage.json');policy=read('reports/context_policy_20261123/out/context_policy.json')
 commit=git('rev-parse','HEAD');previous=json.loads((STATE/'state.json').read_text()) if (STATE/'state.json').exists() else {}
 observed={}
 for label,path in [('lineage','reports/transformation_lineage_20261123/lineage.json'),('policy','reports/context_policy_20261123/out/context_policy.json'),('source_guard','experiments/final_notebook/source_registry.json')]:
  observed[label]=hashlib.sha256((SRC/path).read_bytes()).hexdigest()
 payload={'observed':observed,'git':commit}
 fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
 events=previous.get('events',[])
 if previous.get('fingerprint')!=fingerprint:
  changed=[k for k,v in observed.items() if previous.get('observed',{}).get(k)!=v]
  event={'time':now(),'type':'baseline_registered' if not events else 'artifact_change_observed','component_ids':(['SUB-01'] if 'lineage' in changed else [])+(['POL-01','VAL-01'] if 'policy' in changed else [])+(['GOV-01'] if 'source_guard' in changed else []),'commit':commit,'hashes':observed,'message':'Momentopname geregistreerd; dit is geen nieuw trainingsresultaat.' if not events else 'Wijziging in aangesloten bewijsbestanden of Git HEAD waargenomen; inhoudelijke effectmeting afzonderlijk bekijken.'}
  events.append(event)
 components=[dict(id=i,name=n,kind=k,entities=e,rule=r,code_path=p) for i,n,k,e,r,p in COMPONENTS]
 versions=[{'id':v,'mrr':r['public_mrr25'],'reference':r['official_reference']} for v,r in line['versions'].items()]
 trans=[{'id':x['transformation_id'],'baseline':x['baseline'],'candidate':x['candidate'],'delta':x['delta'],'kernel':x['kernel'],'kernel_version':x['kernel_version'],'receipt_sha256':x['receipt_sha256'],'operation':x['operation'],'causal_status':x['causal_status']} for x in line['transformations']]
 report={'snapshot_at':now() if previous.get('fingerprint')!=fingerprint else previous.get('snapshot_at',now()),'source_snapshot_at':line['created_utc'],'code_commit':commit,'components':components,'versions':versions,'transformations':trans,'policy':{'clean_delta':policy['metrics']['gain_min_proxy']['clean'],'stress_delta':policy['metrics']['gain_min_proxy']['perturbed'],'reward_rmse':[x['reward_prediction_rmse'] for x in policy['diagnostics']],'top1_delta':policy['top1_delta'],'promotion_eligible':False,'status':'rejected_no_gain','limitation':'Hergebruikt NP DEV-panel met gemeld catalogusmetadata-lek. Geen onafhankelijke bevestiging.','notebook':'https://www.kaggle.com/code/develuse/casmi26-context-policy-diagnostic'},'events':events[-100:],'glossary':read('reports/paper_revision_20261123/business_glossary_v1.json')['terms'],'limits':line['limits'],'public_scope':'Gecontroleerde momentopname; geen ruwe datasets, secrets, privélogs of testlabels. Geen live Kaggle-accountkoppeling.'}
 # Actual historical source commits, reviewed public fields only: SHA and snapshot metrics.
 history=[]
 for sha in git('log','-20','--format=%H').splitlines():
  try:
   rows=json.loads(git('show',sha+':VERSIONS.json'))
   scores=[{'version':r.get('version'),'public_mrr':r.get('public_lb_score')} for r in rows if r.get('public_lb_score') is not None]
   history.append({'sha':sha,'scores':scores})
  except (subprocess.CalledProcessError,json.JSONDecodeError):continue
 report['git_snapshots']=history
 encoded=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
 target=ROOT/'docs/snapshot.json';changed=not target.exists() or target.read_text()!=encoded
 target.write_text(encoded)
 (STATE/'state.json').write_text(json.dumps({'fingerprint':fingerprint,'observed':observed,'events':events,'snapshot_at':report['snapshot_at']}))
 return changed

def publish():
 subprocess.run(['git','-C',str(ROOT),'add','docs/snapshot.json'],check=True)
 if subprocess.run(['git','-C',str(ROOT),'diff','--cached','--quiet']).returncode:
  subprocess.run(['git','-C',str(ROOT),'commit','-m','Update observed research evidence snapshot'],check=True)
  subprocess.run(['git','-C',str(ROOT),'push','origin','main'],check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');ap.add_argument('--publish',action='store_true');a=ap.parse_args()
 while True:
  try:
   changed=build()
   if changed and a.publish:publish()
   print(now(),'snapshot changed' if changed else 'no change',flush=True)
  except Exception as e:print(now(),type(e).__name__,str(e),flush=True)
  if not a.watch:break
  time.sleep(60)
