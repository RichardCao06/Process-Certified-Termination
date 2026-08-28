from __future__ import annotations
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
def load_runner():
 p=ROOT/"scripts/run_p2_engineering_smoke_remediation.py"; s=importlib.util.spec_from_file_location("d20_runner_test",p); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m
class D20Tests(unittest.TestCase):
 def test_static_validator(self):
  r=subprocess.run([sys.executable,"scripts/validate_p2_d20.py"],cwd=ROOT,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr)
 def test_first_failure(self):
  r=json.loads((ROOT/"reports/p2/engineering-smoke-run-v0.2.json").read_text()); self.assertEqual(r["report_digest"],"53f3779c64fe225790cc2c7117241b1d04c2d922d1a87c2477590af40278cef8")
 def test_scope(self):
  a=json.loads((ROOT/"governance/p2-engineering-smoke-remediation-authorization-v0.1.json").read_text()); self.assertEqual(a["rerun_scope"]["fixture_ids"],["PCT-P2-SMOKE-ENG-001","PCT-P2-SMOKE-ENG-002"]); self.assertEqual(a["rerun_scope"]["primary_schedule_runs"],0)
 def test_env(self):
  m=load_runner(); fake=SimpleNamespace(sanitize_child_environment=lambda *x:{"KEEP":"yes"})
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); env=m.build_source_mode_child_environment(fake,{},"dummy","http://127.0.0.1",root/"dsh",root/"workspace"); self.assertEqual(env["TSX_TSCONFIG_PATH"],str(root/"dsh/tsconfig.json")); self.assertEqual(env["DSH_AGENTS_HOME"],str(root/"workspace/.agents"))
 def test_classification(self):
  self.assertEqual(load_runner().classify_stderr("ERR_MODULE_NOT_FOUND Cannot find package")["class"],"SOURCE_MODULE_RESOLUTION_FAILURE")
 def test_authority_closed(self):
  s=json.loads((ROOT/"governance/p2-status-v0.5.json").read_text()); self.assertFalse(s["natural_task_shadow_measurement_authorized"]); self.assertFalse(s["online_intervention_authorized"])
if __name__=="__main__": unittest.main()
