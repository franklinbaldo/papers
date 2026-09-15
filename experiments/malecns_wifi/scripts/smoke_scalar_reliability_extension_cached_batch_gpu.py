"""Run preregistered scalar-reliability extension on six new seeds."""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

SEEDS=(20260920,20260921,20260922,20260923,20260924,20260925)

def _final(run, arm):
    curve = run['independent']['curve'] if arm=='independent' else run['coupled'][arm]['curve']
    return curve[-1]['validation']['all_direct']

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--graph',type=Path,required=True); p.add_argument('--embedding-cache',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); p.add_argument('--epochs',type=int,default=3)
    p.add_argument('--lr',type=float,default=5e-4); p.add_argument('--anchor-lambda',type=float,default=0.05)
    p.add_argument('--readout-width',type=int,default=128)
    a=p.parse_args(); here=Path(__file__).resolve().parent; runs={}; timings={}
    for seed in SEEDS:
        out=a.output.parent/f'scalar-extension-seed-{seed}.json'
        cmd=[sys.executable,str(here/'smoke_scalar_reliability_extension_cached_one_gpu.py'),'--graph',str(a.graph),'--embedding-cache',str(a.embedding_cache),'--output',str(out),'--epochs',str(a.epochs),'--lr',str(a.lr),'--peer-lambda','0.5','--anchor-lambda',str(a.anchor_lambda),'--readout-width',str(a.readout_width),'--seed',str(seed)]
        t=time.perf_counter(); subprocess.check_call(cmd); timings[str(seed)]=time.perf_counter()-t
        runs[str(seed)]=json.loads(out.read_text())
    rows=[]
    for seed in SEEDS:
        r=runs[str(seed)]; ind=_final(r,'independent'); sc=_final(r,'reliability_0.50')
        rows.append({'seed':seed,'independent_all':ind['all'],'independent_unseen':ind['unseen_generalization'],'scalar_all':sc['all'],'scalar_unseen':sc['unseen_generalization'],'scalar_minus_independent_unseen':sc['unseen_generalization']-ind['unseen_generalization'],'scalar_minus_independent_all':sc['all']-ind['all'],'seconds':timings[str(seed)]})
    mean_u=sum(x['scalar_minus_independent_unseen'] for x in rows)/len(rows)
    mean_a=sum(x['scalar_minus_independent_all'] for x in rows)/len(rows)
    wins=sum(x['scalar_minus_independent_unseen']>0 for x in rows)
    checks={'positive_unseen_on_at_least_4_of_6':wins>=4,'mean_unseen_gain_ge_0.05':mean_u>=0.05,'mean_all_delta_ge_minus_0.02':mean_a>=-0.02}
    checks['extension_supports_scalar_reliability']=all(checks.values())
    payload={'schema':'papers/malecns-scalar-reliability-extension-batch-v1','claim_status':'preregistered scalar reliability extension; not Stage A/B','preregistration':'preregistered-scalar-reliability-extension-2026-09-15.md','seeds':list(SEEDS),'lambda':0.50,'comparisons':rows,'positive_seed_count':wins,'mean_scalar_minus_independent_unseen':mean_u,'mean_scalar_minus_independent_all':mean_a,'preregistered_checks':checks,'embedding_cache_fingerprint':runs[str(SEEDS[0])].get('embedding_cache',{}).get('fingerprint'),'runs':runs}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'event':'scalar_reliability_extension_batch_complete','summary':{'comparisons':rows,'preregistered_checks':checks}}),flush=True)
if __name__=='__main__': main()
