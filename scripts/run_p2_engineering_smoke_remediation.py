#!/usr/bin/env python3
"""D20 append-only remediation runner for the same two D19 engineering fixtures."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, queue, subprocess, sys, tempfile, threading, time
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/'scripts/run_p2_engineering_smoke.py'
DSH_COMMIT='b150a551b8d465e31e418e1b2eaf5e79bbb7d28e'
FIRST_FAILURE_DIGEST='53f3779c64fe225790cc2c7117241b1d04c2d922d1a87c2477590af40278cef8'
FIXTURE_IDS=['PCT-P2-SMOKE-ENG-001','PCT-P2-SMOKE-ENG-002']
def load_base():
    spec=importlib.util.spec_from_file_location('pct_d19_base',BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError('unable to load D19 base runner')
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module
def canonical_digest(value,field):
    item=deepcopy(value); item.pop(field,None); return hashlib.sha256(json.dumps(item,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build_source_mode_child_environment(base,source,local_proxy_token,proxy_url,dsh,workspace):
    env=base.sanitize_child_environment(source,local_proxy_token,proxy_url,dsh/'examples/headless-agent/cordis.yml',workspace/'.dsh')
    env.update({'TSX_TSCONFIG_PATH':str(dsh/'tsconfig.json'),'DSH_AGENTS_HOME':str(workspace/'.agents')}); return env
def classify_stderr(text):
    lower=text.lower(); rules=[('SOURCE_MODULE_RESOLUTION_FAILURE',['err_module_not_found','cannot find module','cannot find package']),('TYPESCRIPT_CONFIG_RESOLUTION_FAILURE',['tsx_tsconfig_path','tsconfig','paths map']),('INVALID_CREDENTIAL',['invalid_credential']),('MISSING_CREDENTIAL',['missing_credential']),('CORDIS_CONFIG_LOAD_FAILURE',['cordis','config','plugin']),('DUPLICATE_ADAPTER',['duplicate_adapter']),('UNSUPPORTED_REASONING_EFFORT',['unsupported_reasoning_effort']),('PLUGIN_PENDING_OR_SERVICE_MISSING',['pending','required service is missing'])]
    for label,markers in rules:
        if any(m in lower for m in markers): return {'class':label,'matched_marker_count':sum(m in lower for m in markers),'raw_stderr_persisted':False}
    return {'class':'UNCLASSIFIED_PROCESS_START_OR_RUNTIME_FAILURE' if text else 'NONE','matched_marker_count':0,'raw_stderr_persisted':False}
def run_driver(base,dsh,config,workspace,task,proxy,limits,real_api_key):
    loader=dsh/'node_modules/tsx/dist/esm/index.mjs'; driver=dsh/'examples/headless-agent/tests/fixtures/headless-driver.ts'; tsconfig=dsh/'tsconfig.json'
    if not loader.is_file() or not driver.is_file() or not tsconfig.is_file(): raise FileNotFoundError('DSH source-mode loader, driver, or tsconfig missing')
    child_env=build_source_mode_child_environment(base,dict(os.environ),proxy.state.local_proxy_token,proxy.url,dsh,workspace)
    if child_env.get('DEEPSEEK_API_KEY')==real_api_key or real_api_key in child_env.values(): raise RuntimeError('real DeepSeek key reached Worker subprocess environment')
    process=subprocess.Popen(['node','--import',loader.as_uri(),str(driver),str(config),task],cwd=workspace,env=child_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    q=queue.Queue()
    def pump(name,stream):
        for line in iter(stream.readline,''): q.put((name,line))
        q.put((name,None))
    threading.Thread(target=pump,args=('stdout',process.stdout),daemon=True).start(); threading.Thread(target=pump,args=('stderr',process.stderr),daemon=True).start()
    events=[]; stderr=[]; other=[]; done=set(); started=time.monotonic(); cap=None; secret=False
    while len(done)<2 or process.poll() is None:
        if time.monotonic()-started>limits['wall_clock_seconds']: cap='WALL_CLOCK_CAP'; process.kill(); break
        try: name,line=q.get(timeout=.2)
        except queue.Empty: continue
        if line is None: done.add(name); continue
        if real_api_key and real_api_key in line: secret=True; cap='REAL_SECRET_OUTPUT'; process.kill(); continue
        if base.FORBIDDEN_SECRET_PATTERN.search(line): secret=True; cap='SECRET_LIKE_OUTPUT'; process.kill(); continue
        if name=='stderr': stderr.append(line[-1000:]); continue
        try: item=json.loads(line)
        except Exception: other.append(line[-1000:]); continue
        if item.get('type')=='session_event':
            events.append(item); tools=sum(1 for e in events if (e.get('event') or {}).get('type')=='tool/call'); stops=sum(1 for e in events if (e.get('event') or {}).get('type')=='agent/turn-stopping')
            if tools>limits['tool_calls']: cap='TOOL_CALL_CAP'; process.kill()
            if stops>limits['candidate_stops']: cap='CANDIDATE_STOP_CAP'; process.kill()
        else: other.append(json.dumps(item,sort_keys=True)[-2000:])
    try: exit_code=process.wait(timeout=10)
    except subprocess.TimeoutExpired: process.kill(); exit_code=process.wait()
    stderr_text=''.join(stderr); types=[(e.get('event') or {}).get('type') for e in events]
    return {'exit_code':exit_code,'elapsed_seconds':round(time.monotonic()-started,3),'events':events,'event_type_counts':{n:types.count(n) for n in sorted(set(types)) if n},'request_header_tool_sets':base.extract_request_header_tool_sets(events),'stderr_tail_hash':base.sha_text(stderr_text),'stderr_classification':classify_stderr(stderr_text),'other_output_hash':base.sha_text(''.join(other)),'cap_violation':cap,'secret_output_detected':secret,'source_mode_bindings':{'tsx_tsconfig_path_set':child_env.get('TSX_TSCONFIG_PATH')==str(tsconfig),'dsh_agents_home_isolated':child_env.get('DSH_AGENTS_HOME')==str(workspace/'.agents')}}
def write_provider_placeholder(base,status,failure):
    report={'schema_version':'0.2','record_type':'PCT_P2_DEEPSEEK_PROVIDER_INTROSPECTION','report_id':'PCT-P2-DEEPSEEK-PROVIDER-INTROSPECTION-v0.3','status':status,'observed_at':base.now(),'supersedes_for_active_binding':'reports/p2/deepseek-provider-introspection-v0.2.json','preserves_history':True,'remediation_decision':'PCT-P2-D20-A','request':{'method':'GET','base_url':'https://api.deepseek.com','endpoint_path':'/models','requested_model_identifier':'deepseek-v4-pro','task_generation':False,'chat_completion_calls':0,'worker_trajectory_calls':0,'request_performed':False},'response':{'http_status':None,'object':None,'requested_model_found':False,'returned_model_identifier':None,'returned_model_owner':None,'available_model_ids':[]},'model_revision_or_snapshot':'NOT_EXPOSED_BY_PROVIDER','frozen_input_artifacts':base.current_binding_material(),'credential_handling':{'credential_source':'GITHUB_ACTIONS_ENVIRONMENT_SECRET','environment':'p2-natural-pilot','secret_name':'DEEPSEEK_API_KEY','secret_value_recorded':False,'secret_hash_recorded':False,'authorization_header_recorded':False,'secret_available_to_worker_process':False},'failure':failure,'research_boundaries':{'natural_primary_task_worker_calls':0,'semantic_auditor_calls':0,'reference_packets_opened':0,'applied_to_runtime':False,'online_intervention':False}}
    report['report_digest']=canonical_digest(report,'report_digest'); path=ROOT/'reports/p2/deepseek-provider-introspection-v0.3.json'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); return {'status':status,'report_path':path.relative_to(ROOT).as_posix(),'report_sha256':base.sha_file(path),'returned_model_identifier':None}
def fresh_binding(base,api_key):
    bindings=base.current_binding_material(); freeze=json.loads((ROOT/'governance/p2-worker-profile-freeze-v0.2.json').read_text()); frozen=freeze['artifact_bindings']; comparisons={'operational_profile_sha256':frozen['operational_profile_sha256']==bindings['operational_profile_sha256'],'system_prompt_sha256':frozen['system_prompt_sha256']==bindings['system_prompt_sha256'],'intended_capability_catalog_sha256':frozen['intended_capability_catalog_sha256']==bindings['intended_capability_catalog_sha256'],'runtime_tool_catalog_sha256':frozen['runtime_tool_catalog_sha256']==bindings['runtime_tool_catalog_sha256'],'runtime_config_sha256':frozen['engineering_runtime_config_sha256']==bindings['runtime_config_sha256']}
    if not all(comparisons.values()):
        r=write_provider_placeholder(base,'FAIL_LOCAL_BINDING',{'stage':'LOCAL_BINDING','comparisons':comparisons}); r['comparisons']=comparisons; return r
    req=Request('https://api.deepseek.com/models',method='GET',headers={'Authorization':f'Bearer {api_key}','Accept':'application/json','User-Agent':'PCT-P2-D20-fresh-binding/0.1'})
    with urlopen(req,timeout=30) as response: payload=json.loads(response.read().decode()); http_status=int(getattr(response,'status',200))
    report=base.build_binding_report(payload,bindings,base.now()); report['report_id']='PCT-P2-DEEPSEEK-PROVIDER-INTROSPECTION-v0.3'; report['supersedes_for_active_binding']='reports/p2/deepseek-provider-introspection-v0.2.json'; report['remediation_decision']='PCT-P2-D20-A'; report['request']['http_status_observed']=http_status; report['report_digest']=canonical_digest(report,'report_digest'); path=ROOT/'reports/p2/deepseek-provider-introspection-v0.3.json'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); return {'status':'PASS' if report['status']=='PASS' else report['status'],'comparisons':comparisons,'report_path':path.relative_to(ROOT).as_posix(),'report_sha256':base.sha_file(path),'returned_model_identifier':report['response']['returned_model_identifier']}
def write_outputs(base,report):
    report['completed_at']=base.now(); report['report_digest']=canonical_digest(report,'report_digest'); p=ROOT/'reports/p2/engineering-smoke-remediation-run-v0.3.json'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    binding={'schema_version':'0.2','record_type':'PCT_P2_PRE_SMOKE_BINDING_VERIFICATION','verification_id':'PCT-P2-D20-PRE-SMOKE-BINDING-v0.2','created_at':base.now(),'status':'PASS_POST_RESULT_PR_CI_PENDING' if report.get('profile_binding',{}).get('status')=='PASS' else 'FAIL_FRESH_BINDING','fresh_binding':report.get('profile_binding',{}),'engineering_smoke_remediation_report_status':report['status'],'first_failure_preserved':{'path':'reports/p2/engineering-smoke-run-v0.2.json','report_digest':FIRST_FAILURE_DIGEST},'remaining_closure_requirement':'Persist v0.3 append-only evidence and pass full repository validation before D21.'}; binding['verification_digest']=canonical_digest(binding,'verification_digest'); (ROOT/'governance/p2-pre-smoke-binding-verification-v0.2.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
    runs=report.get('runs',[]); passed=sum(i.get('pass') is True for i in runs); (ROOT/'reports/p2/engineering-smoke-remediation-summary-v0.3.md').write_text(f"# P2 D20 工程 Smoke Remediation 摘要 v0.3\n\n状态：**{report['status']}**\n\n同两条 Fixture 重跑：{len(runs)}；通过：{passed}。\n\nD19 首次 v0.2 失败保持不变；正式 60 条轨迹仍未授权。\n")
    gate=ROOT/'docs/p2/p2-human-decision-pack-d21-v0.1.md'; gate.parent.mkdir(parents=True,exist_ok=True); gate.write_text(("# PCT-P2-D21：冻结的 60 条自然任务 Shadow Pilot 执行授权\n\nD20 同两条工程 Fixture 的追加式重跑已通过。\n\n```text\nPCT-P2-D21: A\n\nAdditional constraints or amendments:\n```\n" if report['status']=='PASS' else f"# PCT-P2-D21：D20 工程 Remediation 未通过的处置\n\n追加式重跑状态为 `{report['status']}`，不得授权 60 条自然任务。\n\n```text\nPCT-P2-D21: A\n\nAdditional constraints or amendments:\n```\n"))
    result={'schema_version':'0.1','record_type':'PCT_P2_ENGINEERING_SMOKE_REMEDIATION_RESULT','result_id':'PCT-P2-D20-REMEDIATION-RESULT-v0.1','decision_id':'PCT-P2-D20','status':report['status'],'report_path':'reports/p2/engineering-smoke-remediation-run-v0.3.json','report_digest':report['report_digest'],'trajectory_count':len(runs),'passed_trajectory_count':passed,'fixture_ids':[i.get('fixture_id') for i in runs],'primary_schedule_runs':0,'next_human_gate':'PCT-P2-D21','append_only':True}; result['result_digest']=canonical_digest(result,'result_digest'); (ROOT/'governance/p2-engineering-smoke-remediation-result-v0.1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    active={'project_id':'PCT','phase':'P2','work_order':'PCT-P2-001','record_type':'PCT_P2_ACTIVE_STATUS','version':'0.6','status':'D20_REMEDIATION_PASS_D21_PENDING' if report['status']=='PASS' else 'D20_REMEDIATION_NOT_PASS_D21_PENDING','supersedes_for_active_state':'governance/p2-status-v0.5.json','approved_decision_ids':[f'PCT-P2-D{i:02d}' for i in range(1,21)],'open_normative_gate_ids':['PCT-P2-D21'],'active_decision_register':'governance/p2-decision-register-v0.5.json','remediation_result':'governance/p2-engineering-smoke-remediation-result-v0.1.json','engineering_remediation_runs_completed':len(runs),'engineering_remediation_passed':report['status']=='PASS','natural_task_shadow_measurement_authorized':False,'live_primary_worker_model_calls_authorized':False,'semantic_audit_agent_authorized':False,'reference_evaluator_opening_authorized':False,'online_intervention_authorized':False,'worker_behavior_change_authorized':False,'effectiveness_claim_allowed':False,'next_action':'Human review of PCT-P2-D21; no primary run before explicit approval.'}; active['status_digest']=canonical_digest(active,'status_digest'); (ROOT/'governance/p2-status-v0.6.json').write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--dsh-source',required=True); args=parser.parse_args(); base=load_base(); report={'schema_version':'0.2','record_type':'PCT_P2_ENGINEERING_SMOKE_REPORT','report_id':'PCT-P2-D20-ENGINEERING-SMOKE-REMEDIATION-v0.3','started_at':base.now(),'status':'BLOCKED_PREFLIGHT','remediation':{'decision':'PCT-P2-D20-A','approval_comment_id':5434319705,'first_failure_path':'reports/p2/engineering-smoke-run-v0.2.json','first_failure_report_digest':FIRST_FAILURE_DIGEST,'same_fixture_ids':FIXTURE_IDS},'profile_binding':{'status':'NOT_RUN'},'execution_context':{'github_run_id':os.environ.get('GITHUB_RUN_ID'),'github_run_attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),'github_event_name':os.environ.get('GITHUB_EVENT_NAME'),'source_head_sha':os.environ.get('GITHUB_SHA')},'runs':[],'research_boundaries':{'maximum_trajectories':2,'primary_schedule_runs':0,'reference_packets_opened':0,'semantic_auditor_calls':0,'applied_to_runtime':False,'online_intervention':False,'raw_model_or_tool_content_persisted':False}}
    code=1; real_key=os.environ.get('DEEPSEEK_API_KEY','')
    try:
        if not real_key: report['status']='BLOCKED_SECRET'; report['failure']={'stage':'CREDENTIAL','class':'MissingCredential'}; report['profile_binding']=write_provider_placeholder(base,'BLOCKED_SECRET',report['failure']); code=2
        else:
            report['profile_binding']=fresh_binding(base,real_key)
            if report['profile_binding'].get('status')!='PASS': report['status']='BLOCKED_PREFLIGHT'; code=3
            else:
                os.environ.pop('DEEPSEEK_API_KEY',None); dsh=Path(args.dsh_source).resolve(); head=subprocess.run(['git','-C',str(dsh),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
                if head!=DSH_COMMIT: raise RuntimeError('frozen DSH commit mismatch')
                first=json.loads((ROOT/'reports/p2/engineering-smoke-run-v0.2.json').read_text())
                if first.get('report_digest')!=FIRST_FAILURE_DIGEST or first.get('status')!='FAIL': raise RuntimeError('first D19 failure is not preserved exactly')
                caps=json.loads((ROOT/'governance/p2-operational-caps-v0.1.json').read_text()); catalog=json.loads((ROOT/'data/p2/engineering-smoke/fixture-catalog-v0.1.json').read_text()); fixtures=[i for i in catalog['fixtures'] if i['fixture_id'] in FIXTURE_IDS]
                if [i['fixture_id'] for i in fixtures]!=FIXTURE_IDS: raise RuntimeError('remediation fixture set/order changed')
                runtime=json.loads((ROOT/'config/p2/d19-runtime-tool-catalog-v0.1.json').read_text()); expected=runtime['model_facing_tool_names']; limits=caps['per_trajectory_caps']; config=ROOT/'config/p2/dsh-engineering-smoke.cordis.yml'
                with tempfile.TemporaryDirectory(prefix='pct-p2-d20-') as temp:
                    for fixture in fixtures:
                        workspace=Path(temp)/fixture['fixture_id']; workspace.mkdir(parents=True)
                        for rel,content in fixture['initial_files'].items(): target=workspace/rel; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(content)
                        state=base.ProxyState(caps=caps,upstream_api_key=real_key,expected_tool_names=expected)
                        with base.GuardedProxy(state) as proxy: driver=run_driver(base,dsh,config,workspace,fixture['task'],proxy,limits,real_key)
                        events=driver.pop('events'); headers=driver['request_header_tool_sets']; header_exact=bool(headers) and all(i==expected for i in headers)
                        if not header_exact: state.violations.append('REQUEST_HEADER_TOOL_CATALOG_MISMATCH')
                        artifact_pass,detail=base.validate_artifact(workspace,fixture['validator']); sidecar=base.bind_sidecar(fixture,events,workspace); cost=base.estimate_cost(state.usage,caps)
                        item={'fixture_id':fixture['fixture_id'],'goal_id':fixture['goal_id'],'excluded_from_primary_schedule':True,'driver':driver,'proxy':{'logical_model_requests':state.logical_requests,'upstream_attempts':state.upstream_attempts,'usage':state.usage,'cumulative_tokens':base.token_total(state.usage),'cost_guard':cost,'violations':sorted(set(state.violations)),'request_records':state.records},'runtime_tool_catalog':{'expected':expected,'request_header_sets':headers,'request_header_exact':header_exact},'validator':{'pass':artifact_pass,'detail':detail},'candidate_stop_binding':sidecar,'workspace_digest':'sha256:'+base.workspace_digest(workspace)}
                        item['pass']=driver['exit_code']==0 and driver['cap_violation'] is None and not driver['secret_output_detected'] and not state.violations and state.logical_requests>=1 and artifact_pass and sidecar['status']=='BOUND_EXACT' and header_exact and base.token_total(state.usage)<=limits['cumulative_tokens'] and cost['cny_policy_guard']<=limits['monetary_cap'] and driver['source_mode_bindings']['tsx_tsconfig_path_set'] and driver['source_mode_bindings']['dsh_agents_home_isolated']; report['runs'].append(item)
                report['status']='PASS' if len(report['runs'])==2 and all(i['pass'] for i in report['runs']) else 'FAIL'; code=0 if report['status']=='PASS' else 1
    except Exception as exc: report['status']='ERROR_PRESERVED'; report['failure']={'stage':'D20_REMEDIATION_RUNNER','class':type(exc).__name__,'message_sha256':hashlib.sha256(str(exc).encode()).hexdigest()}; code=1
    finally:
        os.environ.pop('DEEPSEEK_API_KEY',None)
        if not (ROOT/'reports/p2/deepseek-provider-introspection-v0.3.json').is_file(): report['profile_binding']=write_provider_placeholder(base,'ERROR_PRESERVED',{'stage':'D20_REMEDIATION_BINDING','class':report.get('failure',{}).get('class','UnknownFailure')})
        write_outputs(base,report)
    return code
if __name__=='__main__': raise SystemExit(main())
