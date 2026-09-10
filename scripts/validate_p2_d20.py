#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FIRST="53f3779c64fe225790cc2c7117241b1d04c2d922d1a87c2477590af40278cef8"; FIX=["PCT-P2-SMOKE-ENG-001","PCT-P2-SMOKE-ENG-002"]
def dig(v,f):
 x=deepcopy(v); x.pop(f,None); return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text())
def main():
 e=[]; a=load("governance/p2-human-approval-d20-v0.1.json")
 if a.get("approved_options")!={"PCT-P2-D20":"A"}: e.append("D20-A approval missing")
 if a.get("approval_source",{}).get("comment_id")!=5434319705: e.append("approval source mismatch")
 if a.get("approval_digest")!=dig(a,"approval_digest"): e.append("approval digest mismatch")
 first=load("reports/p2/engineering-smoke-run-v0.2.json")
 if first.get("status")!="FAIL" or first.get("report_digest")!=FIRST: e.append("first D19 failure changed")
 auth=load("governance/p2-engineering-smoke-remediation-authorization-v0.1.json")
 if auth.get("rerun_scope",{}).get("fixture_ids")!=FIX: e.append("fixture scope changed")
 if auth.get("authorization_digest")!=dig(auth,"authorization_digest"): e.append("authorization digest mismatch")
 status=load("governance/p2-status-v0.5.json")
 if status.get("natural_task_shadow_measurement_authorized") is not False: e.append("primary pilot authorized")
 runner=(ROOT/"scripts/run_p2_engineering_smoke_remediation.py").read_text()
 for token in ("TSX_TSCONFIG_PATH","DSH_AGENTS_HOME","engineering-smoke-remediation-run-v0.3.json","p2-human-decision-pack-d21-v0.1.md"):
  if token not in runner: e.append("runner missing "+token)
 rp=ROOT/"reports/p2/engineering-smoke-remediation-run-v0.3.json"
 if rp.is_file():
  r=json.loads(rp.read_text())
  if r.get("report_id")!="PCT-P2-D20-ENGINEERING-SMOKE-REMEDIATION-v0.3": e.append("report identity")
  if r.get("report_digest")!=dig(r,"report_digest"): e.append("report digest")
  runs=r.get("runs",[])
  if [i.get("fixture_id") for i in runs]!=FIX: e.append("not exact fixtures")
  for i in runs:
   if i.get("excluded_from_primary_schedule") is not True: e.append("entered primary")
   if i.get("driver",{}).get("secret_output_detected") is not False: e.append("secret output")
   if i.get("driver",{}).get("stderr_classification",{}).get("raw_stderr_persisted") is not False: e.append("raw stderr")
  result=load("governance/p2-engineering-smoke-remediation-result-v0.1.json")
  if result.get("report_digest")!=r.get("report_digest") or result.get("result_digest")!=dig(result,"result_digest"): e.append("result mismatch")
  active=load("governance/p2-status-v0.6.json")
  if active.get("open_normative_gate_ids")!="PCT-P2-D21" and active.get("open_normative_gate_ids")!=["PCT-P2-D21"]: e.append("D21 not open")
  if active.get("natural_task_shadow_measurement_authorized") is not False or active.get("status_digest")!=dig(active,"status_digest"): e.append("active status invalid")
 if e:
  print("P2 D20 validation failed:",file=sys.stderr); [print(" - "+x,file=sys.stderr) for x in e]; return 1
 print("P2 D20 validation passed: D20-A frozen; first failure immutable; only same two fixtures may rerun; primary pilot unauthorized."); return 0
if __name__=="__main__": raise SystemExit(main())
