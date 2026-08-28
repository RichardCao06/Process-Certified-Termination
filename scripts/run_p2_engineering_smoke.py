#!/usr/bin/env python3
"""Run at most two D19 engineering-only DSH trajectories behind a secret-isolating proxy."""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import queue
import re
import secrets
import socket
import subprocess
import tempfile
import threading
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DSH_COMMIT = "b150a551b8d465e31e418e1b2eaf5e79bbb7d28e"
FORBIDDEN_SECRET_PATTERN = re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}")
SECRET_ENV_TERMS = ("TOKEN", "SECRET", "API_KEY", "APIKEY", "PASSWORD", "COOKIE", "CREDENTIAL")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_digest(value: dict, field: str) -> str:
    material = deepcopy(value)
    material.pop(field, None)
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def workspace_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir() or relative.startswith((".sessions/", ".dsh/")):
            continue
        h.update(relative.encode("utf-8")); h.update(b"\0")
        h.update(path.read_bytes()); h.update(b"\0")
    return h.hexdigest()


def token_total(usage: dict[str, int]) -> int:
    return sum(int(usage.get(key, 0) or 0) for key in ("inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens"))


def estimate_cost(usage: dict[str, int], caps: dict) -> dict:
    price = caps["monetary_guard"]["pricing"]
    usd = (
        usage.get("inputTokens", 0) * price["input_cache_miss"]
        + usage.get("outputTokens", 0) * price["output"]
        + usage.get("cacheReadTokens", 0) * price["cache_read"]
        + usage.get("cacheWriteTokens", 0) * price["cache_write"]
    ) / 1_000_000
    cny_guard = usd * caps["monetary_guard"]["policy_exchange_ceiling_cny_per_usd"]
    return {"estimated_usd": round(usd, 8), "cny_policy_guard": round(cny_guard, 8)}


def sanitize_child_environment(source: dict[str, str], local_proxy_token: str, proxy_url: str, dsh_base: Path, dsh_home: Path) -> dict[str, str]:
    child: dict[str, str] = {}
    for key, value in source.items():
        upper = key.upper()
        if any(term in upper for term in SECRET_ENV_TERMS):
            continue
        child[key] = value
    child.update({
        "DEEPSEEK_API_KEY": local_proxy_token,
        "DEEPSEEK_BASE_URL": proxy_url,
        "PCT_DSH_BASE_CONFIG": str(dsh_base),
        "DSH_HOME": str(dsh_home),
        "DSH_SNAPSHOT": "record",
        "DSH_TELEMETRY_DISABLED": "1",
    })
    return child


def extract_wire_tool_names(payload: dict) -> list[str]:
    names: list[str] = []
    for item in payload.get("tools") or []:
        if not isinstance(item, dict):
            continue
        function = item.get("function") if isinstance(item.get("function"), dict) else item
        name = function.get("name") if isinstance(function, dict) else None
        if isinstance(name, str) and name:
            names.append(name)
    return sorted(names)


def extract_request_header_tool_sets(events: list[dict]) -> list[list[str]]:
    sets: list[list[str]] = []
    for envelope in events:
        event = envelope.get("event") or {}
        if event.get("type") != "request/header":
            continue
        data = event.get("data") or {}
        header = data.get("header") or {}
        names = sorted(
            tool.get("name")
            for tool in (header.get("tools") or [])
            if isinstance(tool, dict) and isinstance(tool.get("name"), str)
        )
        if names and names not in sets:
            sets.append(names)
    return sets


def validate_artifact(workspace: Path, validator: dict) -> tuple[bool, str]:
    path = workspace / validator["path"]
    if not path.is_file():
        return False, "MISSING_OUTPUT"
    if validator["type"] == "EXACT_TEXT":
        return path.read_text(encoding="utf-8") == validator["expected"], "EXACT_TEXT"
    if validator["type"] == "JSON_OBJECT_EXACT":
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False, "INVALID_JSON"
        return value == validator["expected"], "JSON_OBJECT_EXACT"
    return False, "UNKNOWN_VALIDATOR"


def read_exact_proposal(workspace: Path, expected: dict) -> tuple[dict | None, str]:
    path = workspace / ".pct/candidate-stop-proposal.json"
    if not path.is_file():
        return None, "MISSING_PROPOSAL"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, "INVALID_PROPOSAL_JSON"
    if not isinstance(value, dict) or value != expected:
        return None, "PROPOSAL_MISMATCH"
    return value, "EXACT"


def build_binding_report(payload: object, bindings: dict, observed_at: str) -> dict:
    if not isinstance(payload, dict) or payload.get("object") != "list" or not isinstance(payload.get("data"), list):
        raise ValueError("model-list response shape mismatch")
    models = []
    for item in payload["data"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("invalid model-list item")
        models.append({"id": item["id"], "object": item.get("object"), "owned_by": item.get("owned_by")})
    models.sort(key=lambda item: item["id"])
    matched = next((item for item in models if item["id"] == "deepseek-v4-pro"), None)
    report = {
        "schema_version": "0.2",
        "record_type": "PCT_P2_DEEPSEEK_PROVIDER_INTROSPECTION",
        "report_id": "PCT-P2-DEEPSEEK-PROVIDER-INTROSPECTION-v0.2",
        "status": "PASS" if matched is not None else "FAIL_MODEL_NOT_LISTED",
        "observed_at": observed_at,
        "supersedes_for_active_binding": "reports/p2/deepseek-provider-introspection-v0.1.json",
        "preserves_history": True,
        "request": {
            "method": "GET", "base_url": "https://api.deepseek.com", "endpoint_path": "/models",
            "requested_model_identifier": "deepseek-v4-pro", "task_generation": False,
            "chat_completion_calls": 0, "worker_trajectory_calls": 0,
        },
        "response": {
            "http_status": 200, "object": "list", "requested_model_found": matched is not None,
            "returned_model_identifier": matched["id"] if matched else None,
            "returned_model_owner": matched.get("owned_by") if matched else None,
            "available_model_ids": [item["id"] for item in models],
        },
        "model_revision_or_snapshot": "NOT_EXPOSED_BY_PROVIDER",
        "frozen_input_artifacts": bindings,
        "credential_handling": {
            "credential_source": "GITHUB_ACTIONS_ENVIRONMENT_SECRET",
            "environment": "p2-natural-pilot", "secret_name": "DEEPSEEK_API_KEY",
            "secret_value_recorded": False, "secret_hash_recorded": False,
            "authorization_header_recorded": False, "secret_available_to_worker_process": False,
        },
        "binding_policy": {
            "historical_report_profile_binding_verified": True,
            "fresh_binding_required_before_generation": True,
        },
        "research_boundaries": {
            "natural_primary_task_worker_calls": 0, "semantic_auditor_calls": 0,
            "reference_packets_opened": 0, "applied_to_runtime": False,
            "online_intervention": False,
        },
    }
    report["report_digest"] = canonical_digest(report, "report_digest")
    return report


def current_binding_material() -> dict:
    return {
        "operational_profile_path": "config/p2/deepseek-v4-pro-operational-profile-v0.2.json",
        "operational_profile_sha256": sha_file(ROOT / "config/p2/deepseek-v4-pro-operational-profile-v0.2.json"),
        "system_prompt_path": "config/p2/natural-pilot-system-prompt-v0.1.txt",
        "system_prompt_sha256": sha_file(ROOT / "config/p2/natural-pilot-system-prompt-v0.1.txt"),
        "intended_capability_catalog_path": "config/p2/natural-pilot-tool-catalog-v0.1.json",
        "intended_capability_catalog_sha256": sha_file(ROOT / "config/p2/natural-pilot-tool-catalog-v0.1.json"),
        "runtime_tool_catalog_path": "config/p2/d19-runtime-tool-catalog-v0.1.json",
        "runtime_tool_catalog_sha256": sha_file(ROOT / "config/p2/d19-runtime-tool-catalog-v0.1.json"),
        "runtime_config_path": "config/p2/dsh-engineering-smoke.cordis.yml",
        "runtime_config_sha256": sha_file(ROOT / "config/p2/dsh-engineering-smoke.cordis.yml"),
    }


def write_binding_placeholder(status: str, failure: dict | None = None) -> dict:
    report = {
        "schema_version": "0.2",
        "record_type": "PCT_P2_DEEPSEEK_PROVIDER_INTROSPECTION",
        "report_id": "PCT-P2-DEEPSEEK-PROVIDER-INTROSPECTION-v0.2",
        "status": status,
        "observed_at": now(),
        "supersedes_for_active_binding": "reports/p2/deepseek-provider-introspection-v0.1.json",
        "preserves_history": True,
        "request": {
            "method": "GET", "base_url": "https://api.deepseek.com", "endpoint_path": "/models",
            "requested_model_identifier": "deepseek-v4-pro", "task_generation": False,
            "chat_completion_calls": 0, "worker_trajectory_calls": 0, "request_performed": False,
        },
        "response": {
            "http_status": None, "object": None, "requested_model_found": False,
            "returned_model_identifier": None, "returned_model_owner": None, "available_model_ids": [],
        },
        "model_revision_or_snapshot": "NOT_EXPOSED_BY_PROVIDER",
        "frozen_input_artifacts": current_binding_material(),
        "credential_handling": {
            "credential_source": "GITHUB_ACTIONS_ENVIRONMENT_SECRET",
            "environment": "p2-natural-pilot", "secret_name": "DEEPSEEK_API_KEY",
            "secret_value_recorded": False, "secret_hash_recorded": False,
            "authorization_header_recorded": False, "secret_available_to_worker_process": False,
        },
        "binding_policy": {
            "historical_report_profile_binding_verified": True,
            "fresh_binding_required_before_generation": True,
        },
        "research_boundaries": {
            "natural_primary_task_worker_calls": 0, "semantic_auditor_calls": 0,
            "reference_packets_opened": 0, "applied_to_runtime": False,
            "online_intervention": False,
        },
    }
    if failure is not None:
        report["failure"] = failure
    report["report_digest"] = canonical_digest(report, "report_digest")
    output = ROOT / "reports/p2/deepseek-provider-introspection-v0.2.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "status": status, "report_path": output.relative_to(ROOT).as_posix(),
        "report_sha256": sha_file(output), "returned_model_identifier": None,
    }


def fresh_binding_check(api_key: str) -> dict:
    bindings = current_binding_material()
    freeze = json.loads((ROOT / "governance/p2-worker-profile-freeze-v0.2.json").read_text(encoding="utf-8"))
    frozen = freeze["artifact_bindings"]
    comparisons = {
        "operational_profile_sha256": frozen["operational_profile_sha256"] == bindings["operational_profile_sha256"],
        "system_prompt_sha256": frozen["system_prompt_sha256"] == bindings["system_prompt_sha256"],
        "intended_capability_catalog_sha256": frozen["intended_capability_catalog_sha256"] == bindings["intended_capability_catalog_sha256"],
        "runtime_tool_catalog_sha256": frozen["runtime_tool_catalog_sha256"] == bindings["runtime_tool_catalog_sha256"],
        "runtime_config_sha256": frozen["engineering_runtime_config_sha256"] == bindings["runtime_config_sha256"],
    }
    if not all(comparisons.values()):
        result = write_binding_placeholder("FAIL_LOCAL_BINDING", {"stage": "LOCAL_BINDING", "comparisons": comparisons})
        result["comparisons"] = comparisons
        return result
    request = Request(
        "https://api.deepseek.com/models", method="GET",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json", "User-Agent": "PCT-P2-D19-fresh-binding/0.2"},
    )
    with urlopen(request, timeout=30) as response:
        http_status = int(getattr(response, "status", 200))
        payload = json.loads(response.read().decode("utf-8"))
    if http_status != 200:
        raise RuntimeError(f"model-list returned HTTP {http_status}")
    report = build_binding_report(payload, bindings, now())
    output = ROOT / "reports/p2/deepseek-provider-introspection-v0.2.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "PASS" if report["status"] == "PASS" else "FAIL_MODEL_NOT_LISTED",
        "comparisons": comparisons,
        "report_path": output.relative_to(ROOT).as_posix(),
        "report_sha256": sha_file(output),
        "returned_model_identifier": report["response"]["returned_model_identifier"],
    }


@dataclass
class ProxyState:
    caps: dict
    upstream_api_key: str = field(repr=False)
    expected_tool_names: list[str] = field(default_factory=list)
    upstream_base: str = "https://api.deepseek.com"
    local_proxy_token: str = field(default_factory=lambda: secrets.token_urlsafe(32), repr=False)
    logical_requests: int = 0
    upstream_attempts: int = 0
    usage: dict[str, int] = field(default_factory=lambda: {
        "inputTokens": 0, "outputTokens": 0, "cacheReadTokens": 0,
        "cacheWriteTokens": 0, "reasoningTokens": 0,
    })
    records: list[dict] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add_usage(self, raw: dict) -> None:
        with self.lock:
            if "prompt_cache_miss_tokens" in raw:
                self.usage["inputTokens"] += int(raw.get("prompt_cache_miss_tokens") or 0)
            else:
                self.usage["inputTokens"] += int(raw.get("prompt_tokens") or 0)
            self.usage["outputTokens"] += int(raw.get("completion_tokens") or 0)
            self.usage["cacheReadTokens"] += int(raw.get("prompt_cache_hit_tokens") or 0)
            details = raw.get("completion_tokens_details") or {}
            self.usage["reasoningTokens"] += int(details.get("reasoning_tokens") or raw.get("reasoning_tokens") or 0)


class GuardedProxy:
    def __init__(self, state: ProxyState):
        self.state = state
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_: Any) -> None:
                return

            def do_POST(self) -> None:
                if self.path.rstrip("/") not in ("/chat/completions", "/v1/chat/completions"):
                    self.send_error(404); return
                auth = self.headers.get("Authorization", "")
                if auth != f"Bearer {outer.state.local_proxy_token}":
                    outer.state.violations.append("LOCAL_PROXY_AUTH_MISMATCH"); self.send_error(401); return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    body = self.rfile.read(length)
                    payload = json.loads(body)
                except Exception:
                    outer.state.violations.append("INVALID_REQUEST_JSON"); self.send_error(400); return
                if payload.get("model") != "deepseek-v4-pro":
                    outer.state.violations.append("MODEL_ID_MISMATCH"); self.send_error(400); return
                wire_tool_names = extract_wire_tool_names(payload)
                if wire_tool_names != outer.state.expected_tool_names:
                    outer.state.violations.append("RUNTIME_TOOL_CATALOG_MISMATCH")
                    outer.state.records.append({"wire_tool_names": wire_tool_names, "forwarded_upstream": False})
                    self.send_error(400); return
                with outer.state.lock:
                    outer.state.logical_requests += 1
                    logical = outer.state.logical_requests
                    used = token_total(outer.state.usage)
                limits = outer.state.caps["per_trajectory_caps"]
                if logical > limits["model_requests"]:
                    outer.state.violations.append("MODEL_REQUEST_CAP"); self.send_error(429); return
                input_upper = len(body)
                remaining = limits["cumulative_tokens"] - used
                requested_output = int(payload.get("max_tokens") or limits["max_output_tokens_per_request"])
                allowed_output = min(
                    requested_output,
                    limits["max_output_tokens_per_request"],
                    remaining - input_upper,
                    limits["context_window_tokens"] - input_upper,
                )
                if allowed_output < 1:
                    outer.state.violations.append("TOKEN_OR_CONTEXT_CAP"); self.send_error(429); return
                payload["max_tokens"] = allowed_output
                forward_body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                response = None
                status = None
                failure = None
                attempts_used = 0
                for attempt, delay in enumerate((0, 2, 8), start=1):
                    attempts_used = attempt
                    if delay:
                        time.sleep(delay)
                    with outer.state.lock:
                        outer.state.upstream_attempts += 1
                    request = Request(
                        outer.state.upstream_base.rstrip("/") + "/chat/completions",
                        data=forward_body,
                        method="POST",
                        headers={
                            "Authorization": f"Bearer {outer.state.upstream_api_key}",
                            "Content-Type": "application/json",
                            "Accept": "text/event-stream",
                            "User-Agent": "PCT-P2-D19-secret-isolating-proxy/0.2",
                        },
                    )
                    try:
                        response = urlopen(request, timeout=360)
                        status = int(getattr(response, "status", 200)); failure = None; break
                    except HTTPError as exc:
                        status = int(exc.code); failure = f"HTTP_{exc.code}"
                        if not (exc.code == 429 or 500 <= exc.code <= 599) or attempt == 3:
                            break
                    except (URLError, TimeoutError, socket.timeout) as exc:
                        failure = type(exc).__name__
                        if attempt == 3:
                            break
                if response is None:
                    outer.state.records.append({
                        "logical_request": logical, "status": status, "failure": failure,
                        "attempts_used": attempts_used, "wire_tool_names": wire_tool_names,
                        "forwarded_upstream": attempts_used > 0,
                    })
                    self.send_error(status or 502); return
                self.send_response(status or 200)
                self.send_header("Content-Type", response.headers.get("Content-Type", "text/event-stream"))
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                buffer = b""
                usage_seen = None
                try:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk); self.wfile.flush(); buffer += chunk
                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            if not line.startswith(b"data:"):
                                continue
                            data = line[5:].strip()
                            if not data or data == b"[DONE]":
                                continue
                            try:
                                item = json.loads(data)
                            except Exception:
                                continue
                            if isinstance(item.get("usage"), dict):
                                usage_seen = item["usage"]
                finally:
                    response.close(); self.close_connection = True
                if usage_seen is None:
                    outer.state.violations.append("MISSING_USAGE")
                else:
                    outer.state.add_usage(usage_seen)
                cost = estimate_cost(outer.state.usage, outer.state.caps)
                if token_total(outer.state.usage) > limits["cumulative_tokens"]:
                    outer.state.violations.append("TOKEN_CAP_POST_RESPONSE")
                if cost["cny_policy_guard"] > limits["monetary_cap"]:
                    outer.state.violations.append("MONETARY_CAP")
                outer.state.records.append({
                    "logical_request": logical, "model": "deepseek-v4-pro",
                    "max_tokens_sent": allowed_output, "usage_observed": usage_seen is not None,
                    "attempts_used": attempts_used, "wire_tool_names": wire_tool_names,
                    "forwarded_upstream": True,
                })

        class Server(http.server.ThreadingHTTPServer):
            daemon_threads = True

        self.server = Server(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self.thread.start(); return self

    def __exit__(self, *_: object) -> None:
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)


def bind_sidecar(fixture: dict, events: list[dict], workspace: Path) -> dict:
    stopping = next((item for item in events if (item.get("event") or {}).get("type") == "agent/turn-stopping"), None)
    if stopping is None:
        return {"status": "MISSING_TURN_STOPPING_EVENT"}
    expected = fixture["expected_candidate_stop_proposal"]
    proposal, proposal_status = read_exact_proposal(workspace, expected)
    if proposal is None:
        return {"status": proposal_status}
    session_id = str(stopping.get("sessionId") or stopping.get("session_id") or "unknown-session")
    data = (stopping.get("event") or {}).get("data") or {}
    raw_turn = data.get("turn", 1)
    turn = raw_turn if isinstance(raw_turn, int) else int((raw_turn or {}).get("number", 1))
    snapshot_id = "sha256:" + workspace_digest(workspace)
    from pct.shadow.sidecar import CandidateStopSidecar, ReadOnlyCandidateStopObserver
    created_at = now()
    sidecar = CandidateStopSidecar(
        sidecar_id=f"{fixture['fixture_id']}-sidecar", source="TASK_ADAPTER",
        session_id=session_id, turn=turn, goal_id=fixture["goal_id"], goal_revision=1,
        snapshot_id=snapshot_id, stop_scope=proposal["stop_scope"],
        recovery_authority=proposal["recovery_authority"], worker_claim=proposal["worker_claim"],
        claims_goal_complete=proposal["claims_goal_complete"], created_at=created_at,
    )
    event, candidate, bound = ReadOnlyCandidateStopObserver().observe_turn_stopping(
        sequence=len(events) + 1, session_id=session_id, turn=turn,
        goal_id=fixture["goal_id"], goal_revision=1, snapshot_id=snapshot_id,
        created_at=created_at, sidecar=sidecar,
    )
    return {
        "status": "BOUND_EXACT" if bound else "MISSING_METADATA",
        "candidate_stop": candidate,
        "sidecar_digest": bound.get("sidecar_digest") if bound else None,
        "pct_event_id": event.event_id,
        "proposal_status": proposal_status,
    }


def run_driver(dsh: Path, config: Path, workspace: Path, task: str, proxy: GuardedProxy, limits: dict, real_api_key: str) -> dict:
    loader = dsh / "node_modules/tsx/dist/esm/index.mjs"
    driver = dsh / "examples/headless-agent/tests/fixtures/headless-driver.ts"
    if not loader.is_file() or not driver.is_file():
        raise FileNotFoundError("DSH dependencies or headless driver missing")
    child_env = sanitize_child_environment(
        dict(os.environ), proxy.state.local_proxy_token, proxy.url,
        dsh / "examples/headless-agent/cordis.yml", workspace / ".dsh",
    )
    if child_env.get("DEEPSEEK_API_KEY") == real_api_key or real_api_key in child_env.values():
        raise RuntimeError("real DeepSeek key reached Worker subprocess environment")
    command = ["node", "--import", loader.as_uri(), str(driver), str(config), task]
    process = subprocess.Popen(
        command, cwd=workspace, env=child_env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    output_queue: queue.Queue[tuple[str, str | None]] = queue.Queue()

    def pump(name: str, stream: Any) -> None:
        for line in iter(stream.readline, ""):
            output_queue.put((name, line))
        output_queue.put((name, None))

    threading.Thread(target=pump, args=("stdout", process.stdout), daemon=True).start()
    threading.Thread(target=pump, args=("stderr", process.stderr), daemon=True).start()
    events: list[dict] = []
    stderr_fragments: list[str] = []
    other_fragments: list[str] = []
    done: set[str] = set()
    started = time.monotonic()
    cap_violation = None
    secret_output_detected = False
    while len(done) < 2 or process.poll() is None:
        if time.monotonic() - started > limits["wall_clock_seconds"]:
            cap_violation = "WALL_CLOCK_CAP"; process.kill(); break
        try:
            name, line = output_queue.get(timeout=0.2)
        except queue.Empty:
            continue
        if line is None:
            done.add(name); continue
        if real_api_key and real_api_key in line:
            secret_output_detected = True; cap_violation = "REAL_SECRET_OUTPUT"; process.kill(); continue
        if FORBIDDEN_SECRET_PATTERN.search(line):
            secret_output_detected = True; cap_violation = "SECRET_LIKE_OUTPUT"; process.kill(); continue
        if name == "stderr":
            stderr_fragments.append(line[-1000:]); continue
        try:
            item = json.loads(line)
        except Exception:
            other_fragments.append(line[-1000:]); continue
        if item.get("type") == "session_event":
            events.append(item)
            event_type = (item.get("event") or {}).get("type")
            tool_calls = sum(1 for event in events if (event.get("event") or {}).get("type") == "tool/call")
            stops = sum(1 for event in events if (event.get("event") or {}).get("type") == "agent/turn-stopping")
            if tool_calls > limits["tool_calls"]:
                cap_violation = "TOOL_CALL_CAP"; process.kill()
            if stops > limits["candidate_stops"]:
                cap_violation = "CANDIDATE_STOP_CAP"; process.kill()
        else:
            other_fragments.append(json.dumps(item, sort_keys=True)[-2000:])
    try:
        exit_code = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill(); exit_code = process.wait()
    event_types = [(item.get("event") or {}).get("type") for item in events]
    return {
        "exit_code": exit_code,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "events": events,
        "event_type_counts": {name: event_types.count(name) for name in sorted(set(event_types)) if name},
        "request_header_tool_sets": extract_request_header_tool_sets(events),
        "stderr_tail_hash": sha_text("".join(stderr_fragments)),
        "other_output_hash": sha_text("".join(other_fragments)),
        "cap_violation": cap_violation,
        "secret_output_detected": secret_output_detected,
    }


def write_binding_verification(binding: dict, report_status: str) -> None:
    value = {
        "schema_version": "0.1",
        "record_type": "PCT_P2_PRE_SMOKE_BINDING_VERIFICATION",
        "verification_id": "PCT-P2-D19-PRE-SMOKE-BINDING-v0.1",
        "created_at": now(),
        "status": (
            "PASS_POST_RESULT_PR_CI_PENDING"
            if binding.get("status") == "PASS"
            else "FAIL_FRESH_BINDING"
        ),
        "fresh_binding": binding,
        "engineering_smoke_report_status": report_status,
        "historical_profile_binding": {
            "report_path": "reports/p2/deepseek-provider-introspection-v0.1.json",
            "candidate_profile_path": "config/p2/deepseek-v4-pro-profile-candidate-v0.1.json",
            "sha256_match": True,
        },
        "historical_action_required_run_preserved": {
            "run_id": 32946228591, "run_number": 184,
            "conclusion": "action_required", "jobs": 0,
        },
        "remaining_closure_requirement": "The protected D19 workflow must complete post-result full validation and persist the sanitized result commit; any separately required PR checks must also be approved before D20 authorization.",
    }
    value["verification_digest"] = canonical_digest(value, "verification_digest")
    path = ROOT / "governance/p2-pre-smoke-binding-verification-v0.1.json"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary_and_d20(report: dict) -> None:
    status = report["status"]
    runs = report.get("runs", [])
    passed = sum(1 for item in runs if item.get("pass") is True)
    summary = ROOT / "reports/p2/engineering-smoke-summary-v0.2.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        "# P2 D19 工程 Smoke 摘要 v0.2\n\n"
        f"状态：**{status}**\n\n"
        f"运行数：{len(runs)}；通过：{passed}。\n\n"
        "这些运行均为工程 Fixture，不属于冻结的 20 个任务或 60 条正式轨迹，不进入主要分析分母。\n"
        "原始模型文本、工具参数、工具结果和任何密钥均未进入本报告。\n",
        encoding="utf-8",
    )
    gate = ROOT / "docs/p2/p2-human-decision-pack-d20-v0.1.md"
    gate.parent.mkdir(parents=True, exist_ok=True)
    if status == "PASS":
        gate.write_text(
            "# PCT-P2-D20：冻结的 60 条自然任务 Shadow Pilot 执行授权\n\n"
            "D19 两条工程 Smoke 已通过。**但 D20 只能在受保护的 D19 工作流完成结果后全量验证、成功持久化结果 Commit，并满足 PR 仍要求的其他检查后批准。**\n\n"
            "## 建议 A\n\n"
            "授权按冻结顺序运行 60 条轨迹；按 10 条形成不可变检查点。批间只允许因密钥、安全、预算或基础设施 Hard Stop 暂停，"
            "不得根据中间效果修改任务、模型、Prompt、工具、指标、分母、Reference 规则或排除规则。\n\n"
            "```text\nPCT-P2-D20: A\n\nAdditional constraints or amendments:\n```\n",
            encoding="utf-8",
        )
    else:
        gate.write_text(
            "# PCT-P2-D20：工程 Smoke 未通过的处置\n\n"
            f"D19 状态为 `{status}`，不得授权 60 条自然任务。\n\n"
            "## 建议 A\n\n"
            "保留首次失败，只修复报告中已定位的工程缺陷，并在同一两条 Fixture 上重跑；不得修改正式任务、模型、主要指标或分母。\n\n"
            "```text\nPCT-P2-D20: A\n\nAdditional constraints or amendments:\n```\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsh-source", required=True)
    parser.add_argument("--output", default="reports/p2/engineering-smoke-run-v0.2.json")
    args = parser.parse_args()
    report = {
        "schema_version": "0.2",
        "record_type": "PCT_P2_ENGINEERING_SMOKE_REPORT",
        "report_id": "PCT-P2-D19-ENGINEERING-SMOKE-v0.2",
        "started_at": now(),
        "status": "BLOCKED_PREFLIGHT",
        "profile_binding": {"status": "NOT_RUN"},
        "execution_context": {
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "github_event_name": os.environ.get("GITHUB_EVENT_NAME"),
            "source_head_sha": os.environ.get("GITHUB_SHA"),
        },
        "runs": [],
        "research_boundaries": {
            "maximum_trajectories": 2, "primary_schedule_runs": 0,
            "reference_packets_opened": 0, "semantic_auditor_calls": 0,
            "applied_to_runtime": False, "online_intervention": False,
            "raw_model_or_tool_content_persisted": False,
        },
    }
    exit_code = 1
    real_api_key = ""
    try:
        real_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not real_api_key:
            report["status"] = "BLOCKED_SECRET"
            report["failure"] = {"stage": "CREDENTIAL", "class": "MissingCredential"}
            report["profile_binding"] = write_binding_placeholder("BLOCKED_SECRET", report["failure"])
            return_code = 2
        else:
            binding = fresh_binding_check(real_api_key)
            report["profile_binding"] = binding
            if binding.get("status") != "PASS":
                report["status"] = "BLOCKED_PREFLIGHT"
                return_code = 3
            else:
                # Remove the real key before creating any Worker subprocess.
                os.environ.pop("DEEPSEEK_API_KEY", None)
                dsh = Path(args.dsh_source).resolve()
                head = subprocess.run(["git", "-C", str(dsh), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
                if head != DSH_COMMIT:
                    raise RuntimeError("frozen DSH commit mismatch")
                caps = json.loads((ROOT / "governance/p2-operational-caps-v0.1.json").read_text(encoding="utf-8"))
                fixture_catalog = json.loads((ROOT / "data/p2/engineering-smoke/fixture-catalog-v0.1.json").read_text(encoding="utf-8"))
                runtime_catalog = json.loads((ROOT / "config/p2/d19-runtime-tool-catalog-v0.1.json").read_text(encoding="utf-8"))
                expected_tools = runtime_catalog["model_facing_tool_names"]
                config = ROOT / "config/p2/dsh-engineering-smoke.cordis.yml"
                limits = caps["per_trajectory_caps"]
                with tempfile.TemporaryDirectory(prefix="pct-p2-d19-") as temp:
                    for fixture in fixture_catalog["fixtures"][:2]:
                        workspace = Path(temp) / fixture["fixture_id"]
                        workspace.mkdir(parents=True)
                        for relative, content in fixture["initial_files"].items():
                            target = workspace / relative
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_text(content, encoding="utf-8")
                        state = ProxyState(caps=caps, upstream_api_key=real_api_key, expected_tool_names=expected_tools)
                        with GuardedProxy(state) as proxy:
                            driver = run_driver(dsh, config, workspace, fixture["task"], proxy, limits, real_api_key)
                        events = driver.pop("events")
                        header_sets = driver["request_header_tool_sets"]
                        header_tools_exact = bool(header_sets) and all(item == expected_tools for item in header_sets)
                        if not header_tools_exact:
                            state.violations.append("REQUEST_HEADER_TOOL_CATALOG_MISMATCH")
                        artifact_pass, artifact_detail = validate_artifact(workspace, fixture["validator"])
                        sidecar = bind_sidecar(fixture, events, workspace)
                        cost = estimate_cost(state.usage, caps)
                        run = {
                            "fixture_id": fixture["fixture_id"],
                            "goal_id": fixture["goal_id"],
                            "excluded_from_primary_schedule": True,
                            "driver": driver,
                            "proxy": {
                                "logical_model_requests": state.logical_requests,
                                "upstream_attempts": state.upstream_attempts,
                                "usage": state.usage,
                                "cumulative_tokens": token_total(state.usage),
                                "cost_guard": cost,
                                "violations": sorted(set(state.violations)),
                                "request_records": state.records,
                            },
                            "runtime_tool_catalog": {
                                "expected": expected_tools,
                                "request_header_sets": header_sets,
                                "request_header_exact": header_tools_exact,
                            },
                            "validator": {"pass": artifact_pass, "detail": artifact_detail},
                            "candidate_stop_binding": sidecar,
                            "workspace_digest": "sha256:" + workspace_digest(workspace),
                        }
                        run["pass"] = (
                            driver["exit_code"] == 0
                            and driver["cap_violation"] is None
                            and driver["secret_output_detected"] is False
                            and not state.violations
                            and state.logical_requests >= 1
                            and artifact_pass
                            and sidecar["status"] == "BOUND_EXACT"
                            and header_tools_exact
                            and token_total(state.usage) <= limits["cumulative_tokens"]
                            and cost["cny_policy_guard"] <= limits["monetary_cap"]
                        )
                        report["runs"].append(run)
                report["status"] = "PASS" if len(report["runs"]) == 2 and all(item["pass"] for item in report["runs"]) else "FAIL"
                return_code = 0 if report["status"] == "PASS" else 1
    except Exception as exc:
        report["status"] = "ERROR_PRESERVED"
        report["failure"] = {
            "stage": "D19_RUNNER",
            "class": type(exc).__name__,
            "message_sha256": sha_text(str(exc)),
        }
        return_code = 1
    finally:
        if real_api_key:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        binding_path = ROOT / "reports/p2/deepseek-provider-introspection-v0.2.json"
        if not binding_path.is_file():
            report["profile_binding"] = write_binding_placeholder(
                "ERROR_PRESERVED",
                {"stage": "FRESH_BINDING", "class": report.get("failure", {}).get("class", "UnknownFailure")},
            )
        report["completed_at"] = now()
        report["report_digest"] = canonical_digest(report, "report_digest")
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_binding_verification(report.get("profile_binding", {}), report["status"])
        write_summary_and_d20(report)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
