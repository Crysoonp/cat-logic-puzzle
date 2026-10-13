from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path.cwd()
OUTPUT = ROOT / "NEKOMICHI_STAGE_QUALITY_AUDIT_INPUT.txt"

EXACT_FILES = [
    "app-config.js",
    "foundation-manifest.json",
    "repository-housekeeping-plan.json",
    "stages.js",
    "game.js",
    "index.html",
    "storage-service.js",
    "game-state.js",
    "scripts/run-foundation-checks.js",
]

SEARCH_TERMS = [
    "hint", "solve", "solver", "unique", "difficulty", "difficult",
    "logic", "candidate", "region", "adjacent", "stage", "boss",
    "猫", "ヒント", "難易度", "唯一", "候補", "隣接", "エリア",
]

TEXT_SUFFIXES = {".js", ".json", ".html", ".md", ".txt"}
EXCLUDE_PARTS = {".git", ".nekomichi-backups", "node_modules", "__pycache__"}


def run(command):
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=240)
        return result.returncode, (result.stdout + result.stderr).strip()
    except Exception as exc:
        return 126, f"{type(exc).__name__}: {exc}"


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def safe_rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


missing = [name for name in EXACT_FILES if not (ROOT / name).is_file()]
if missing:
    print("ERROR: required files missing: " + ", ".join(missing))
    sys.exit(1)

version_text = read(ROOT / "app-config.js")
version_match = re.search(r"const\s+VERSION\s*=\s*['\"]([^'\"]+)['\"]", version_text)
version = version_match.group(1) if version_match else "NOT_FOUND"

candidate_files = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        continue
    if path.name.startswith("update_nekomichi_") or path.name.startswith("AUDIT_NEKOMICHI_"):
        continue
    candidate_files.append(path)

matched_files = []
for path in sorted(candidate_files, key=lambda p: safe_rel(p).lower()):
    text = read(path)
    lower = text.lower()
    hits = [term for term in SEARCH_TERMS if term.lower() in lower]
    if hits:
        matched_files.append((path, hits))

report = [
    "NEKOMICHI STAGE QUALITY AUDIT INPUT",
    f"Collected: {datetime.now().isoformat(timespec='seconds')}",
    f"Root: {ROOT}",
    f"Version: {version}",
    "",
    "=== PURPOSE ===",
    "Build automated audits for Stage 1-50 difficulty, uniqueness, human-logical solvability, and current hint behavior.",
    "This collector performs no source modification, deletion, Git staging, commit, or push.",
    "",
    "=== FOUNDATION CHECK ===",
]

rc, output = run(["node", "scripts/run-foundation-checks.js"])
report.extend([f"exit={rc}", output or "(no output)", ""])

report.append("=== GIT STATUS ===")
for command in (["git", "status", "--short"], ["git", "rev-parse", "HEAD"]):
    rc, output = run(command)
    report.extend(["$ " + " ".join(command) + f" | exit={rc}", output or "(no output)"])
report.append("")

report.append("=== EXACT FILE INDEX ===")
for name in EXACT_FILES:
    path = ROOT / name
    report.append(f"{name}\t{path.stat().st_size} bytes\tSHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
report.append("")

report.append("=== SEARCH-MATCHED FILE INDEX ===")
for path, hits in matched_files:
    report.append(f"{safe_rel(path)}\tterms={hits}\tbytes={path.stat().st_size}")
report.append("")

included = []
for name in EXACT_FILES:
    path = ROOT / name
    included.append(path)
for path, _hits in matched_files:
    if path not in included:
        included.append(path)

report.append("=== FULL FILE CONTENTS ===")
for path in included:
    rel = safe_rel(path)
    text = read(path)
    report.extend([
        "=" * 100,
        f"FILE: {rel}",
        f"SIZE: {path.stat().st_size}",
        f"SHA256: {hashlib.sha256(path.read_bytes()).hexdigest()}",
        "--- BEGIN ---",
        text,
        "--- END ---",
        "",
    ])

report.append("=== COLLECTION SUMMARY ===")
report.append(f"exact_files={len(EXACT_FILES)}")
report.append(f"search_matched_files={len(matched_files)}")
report.append(f"full_files_included={len(included)}")

OUTPUT.write_text("\n".join(report) + "\n", encoding="utf-8")
print("OK: Nekomichi stage quality audit input collected.")
print(f"FILES: {len(included)}")
print("OUTPUT: " + OUTPUT.name)
print("SEND: Upload only NEKOMICHI_STAGE_QUALITY_AUDIT_INPUT.txt to Copilot.")
