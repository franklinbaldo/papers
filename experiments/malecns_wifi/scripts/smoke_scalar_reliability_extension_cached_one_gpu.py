from __future__ import annotations
import json, sys
from pathlib import Path
import semantic_embedding_cache as cachelib
import smoke_concept_flavour_gpu as base
import smoke_scalar_reliability_extension_one_gpu as scalar

_CACHE=None
_MANIFEST=None

def _pop(name):
    i=sys.argv.index(name); v=sys.argv[i+1]; del sys.argv[i:i+2]; return v

def _cached_prepare(model_names, examples, scales, device):
    del device
    global _MANIFEST
    encoders,_MANIFEST=cachelib.load_cache(model_names=model_names, examples=examples, scales=scales, cache=_CACHE)
    return encoders

def main():
    global _CACHE
    _CACHE=Path(_pop('--embedding-cache'))
    base._prepare_encoders=_cached_prepare
    scalar.main()
    out=Path(sys.argv[sys.argv.index('--output')+1])
    p=json.loads(out.read_text())
    p['embedding_cache']={'fingerprint':_MANIFEST['fingerprint'],'backend':_MANIFEST['backend'],'device':_MANIFEST['device']}
    p['encoder_forward_during_training']=False
    out.write_text(json.dumps(p,indent=2)+'\n')
if __name__=='__main__': main()
