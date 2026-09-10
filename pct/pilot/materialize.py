from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/p2/natural-pilot/public-task-catalog-v0.1.json"


def load_catalog(path: str | Path = CATALOG) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("task catalog must be a JSON object")
    return value


def materialize_task(task_id: str, destination: str | Path, *, overwrite: bool = False) -> Path:
    catalog = load_catalog()
    matches = [item for item in catalog["tasks"] if item["task_id"] == task_id]
    if len(matches) != 1:
        raise KeyError(f"unknown or duplicate task_id: {task_id}")
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    for relative, content in matches[0]["input_files"].items():
        path = target / relative
        if path.exists() and not overwrite:
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return target
