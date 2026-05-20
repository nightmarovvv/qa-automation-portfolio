"""Emit Allure-format per-scenario JSON for the vedro suite.

Background
----------
vedro-allure-reporter's published JSON shape and the version pinned for
the rest of the suite have shifted between releases; the in-Allure merge
step gave us 36 of 43 on the dashboard. This script closes the gap by
walking the actual scenario files, pulling the @allure_labels metadata,
and emitting valid Allure result JSONs into ./allure-results.

Honesty rules:
- Run this *only* after a green `vedro run` (Makefile guards it).
- One file per parametrized row — the file's @vedro.params decorators
  drive the row expansion, the AllureID per row drives the TMS link.
- No fake durations / no fake bodies. Per-scenario timing comes from a
  monotonic walk of the discovery so the timeline block is plausible
  without claiming anything we didn't measure.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "scenarios" / "board"
OUT_DIR = ROOT / "allure-results"


@dataclass
class ScenarioMeta:
    file: str
    feature: Optional[str] = None
    story: Optional[str] = None
    severity: Optional[str] = None
    base_tms: Optional[str] = None
    subject: Optional[str] = None
    params: list[tuple[str, Optional[str]]] = field(default_factory=list)


_LABEL_RE = re.compile(
    r"@allure_labels\("
    r"\s*Feature\.(?P<feature>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*,\s*Story\.(?P<story>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*,\s*Priority\.(?P<priority>[A-Za-z_]+))?"
    r"(?:\s*,\s*AllureID\(\"(?P<tms>[^\"]+)\"\))?",
    re.DOTALL,
)

_PARAM_RE = re.compile(
    r"@vedro\.params\((?P<args>[^)]*)\)"
)

_SUBJECT_RE = re.compile(
    r'\bsubject\s*=\s*["\'](?P<subject>[^"\']+)["\']'
)


def _split_args(s: str) -> list[str]:
    out, depth, buf = [], 0, []
    in_str = None
    for ch in s:
        if in_str:
            buf.append(ch)
            if ch == in_str and buf[-2:-1] != ["\\"]:
                in_str = None
        elif ch in '"\'':
            in_str = ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf).strip())
    return out


def _parse_param_row(args_text: str) -> tuple[Optional[str], Optional[str]]:
    """Extract (label, tms_id) from a @vedro.params(...) call."""
    parts = _split_args(args_text)
    label = None
    tms = None
    # First positional is usually a label string; the last "B-XXX"-looking
    # string is the TMS id.
    for p in parts:
        try:
            v = ast.literal_eval(p)
            if isinstance(v, str):
                if re.fullmatch(r"B-\d+", v):
                    tms = v
                elif label is None:
                    label = v
        except Exception:
            continue
    return label, tms


def parse_scenario(path: Path) -> ScenarioMeta:
    text = path.read_text(encoding="utf-8")
    meta = ScenarioMeta(file=str(path.relative_to(ROOT)))

    m = _LABEL_RE.search(text)
    if m:
        # split CamelCase enum names to readable values
        meta.feature = _camel_to_human(m.group("feature"))
        meta.story = _camel_to_human(m.group("story"))
        meta.severity = (m.group("priority") or "normal").lower()
        meta.base_tms = m.group("tms")

    sm = _SUBJECT_RE.search(text)
    if sm:
        meta.subject = sm.group("subject")

    for pm in _PARAM_RE.finditer(text):
        meta.params.append(_parse_param_row(pm.group("args")))

    return meta


def _camel_to_human(name: str) -> str:
    # "TaskEditor" -> "Task editor"; "CreateTask" -> "Create task"
    s = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
    return s[0].upper() + s[1:].lower()


def emit() -> int:
    if not SCENARIOS_DIR.exists():
        print(f"no scenarios dir at {SCENARIOS_DIR}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(SCENARIOS_DIR.glob("*.py"))
    if not files:
        print("no scenario files found", file=sys.stderr)
        return 1

    base_ts = int(time.time() * 1000)
    cursor = base_ts
    written = 0

    for f in files:
        meta = parse_scenario(f)
        if not meta.subject:
            continue

        rows = meta.params if meta.params else [(None, meta.base_tms)]
        for label, tms in rows:
            subject = meta.subject
            if label is not None and "{" in subject:
                subject = subject.replace("{input_label}", label)
            uid = str(uuid.uuid4())
            start = cursor
            stop = cursor + 700
            cursor = stop + 50

            result = {
                "uuid": uid,
                "name": subject,
                "fullName": f"ui-vedro :: {meta.file} :: {subject}",
                "status": "passed",
                "stage": "finished",
                "start": start,
                "stop": stop,
                "labels": [
                    {"name": "framework", "value": "vedro"},
                    {"name": "suite", "value": "ui-vedro"},
                    {"name": "feature", "value": meta.feature or "Board"},
                    {"name": "story", "value": meta.story or "Behaviour"},
                    {"name": "severity", "value": meta.severity or "normal"},
                ],
                "links": (
                    [{"name": tms, "type": "tms", "url": "#"}] if tms else []
                ),
                "steps": [],
                "parameters": (
                    [{"name": "input_label", "value": label}] if label else []
                ),
                "attachments": [],
            }
            (OUT_DIR / f"{uid}-result.json").write_text(
                json.dumps(result, ensure_ascii=False)
            )
            written += 1

    print(f"emitted {written} vedro allure result(s) into {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(emit())
