"""Few-NERD byte-level NER smoke for MaleCNS positional tagging."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def canonical_byte_axis(tokens, tags):
    if len(tokens) != len(tags):
        raise RuntimeError("token/tag mismatch")
    parts=[]; spans=[]; byte_tags=[]; cursor=0
    for i,(token,tag) in enumerate(zip(tokens,tags,strict=True)):
        token=str(token); tag=int(tag)
        if i:
            parts.append(" "); byte_tags.append(0); cursor+=1
        raw=token.encode("utf-8"); start=cursor; end=start+len(raw)
        parts.append(token); spans.append((start,end)); byte_tags.extend([tag]*len(raw)); cursor=end
    text="".join(parts); encoded=text.encode("utf-8")
    if len(encoded)!=len(byte_tags):
        raise RuntimeError("byte-axis length mismatch")
    for token,(start,end) in zip(tokens,spans,strict=True):
        if encoded[start:end] != str(token).encode("utf-8"):
            raise RuntimeError("token-byte roundtrip mismatch")
    return text,spans,byte_tags

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--split",default="train"); p.add_argument("--limit",type=int,default=64); a=p.parse_args()
    from datasets import load_dataset
    ds=load_dataset("DFKI-SLT/few-nerd","supervised",split=a.split)
    if a.limit: ds=ds.select(range(min(a.limit,len(ds))))
    tt=et=tb=eb=ut=0
    for sample in ds:
        tokens=list(sample["tokens"]); tags=[int(x) for x in sample["ner_tags"]]
        text,spans,byte_tags=canonical_byte_axis(tokens,tags)
        tt+=len(tokens); et+=sum(x!=0 for x in tags); tb+=len(byte_tags); eb+=sum(x!=0 for x in byte_tags); ut+=sum(len(str(t).encode("utf-8"))!=len(str(t)) for t in tokens)
    out={"schema":"papers/malecns-fewnerd-ner-byte-smoke-v1","claim_status":"pipeline smoke only; not benchmark evidence","dataset":"DFKI-SLT/few-nerd","config":"supervised","split":a.split,"samples":len(ds),"tokens":tt,"entity_tokens":et,"bytes":tb,"entity_bytes":eb,"unicode_tokens":ut,"task":"byte-level internal NER with exact entity-span/type evaluation","canonical_reconstruction":"official tokens joined by one ASCII space; separator bytes are outside label","roundtrip":"all token UTF-8 slices matched original token bytes","guardrail":"MaleCNS predictions live on bytes; token/span conversion only at benchmark boundary","preregistration_amendment":"preregistered-fewnerd-ner-byte-amendment-2026-09-15.md"}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"event":"fewnerd_byte_ner_smoke_ready",**out}),flush=True)
if __name__=="__main__": main()
