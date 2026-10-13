from pathlib import Path
from datetime import datetime
import subprocess

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "NEKOMICHI_HIGH_DIFFICULTY_EVALUATOR_BEFORE_V224.txt"

EXCLUDED_DIRS = {
    ".git", "node_modules", "dist", "build", ".idea", ".vscode",
    "coverage", ".pytest_cache", "__pycache__", ".gradle", "android"
}
EXCLUDED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp3", ".wav", ".ogg",
    ".mp4", ".zip", ".apk", ".aab", ".pdf", ".docx", ".xlsx", ".lock"
}
TARGET_SUFFIXES = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".html", ".css", ".py", ".md", ".txt"}
KEYWORDS = (
    "stage", "generator", "generate", "difficulty", "evaluate", "evaluator",
    "solver", "logic", "puzzle", "board", "region", "candidate", "score",
    "rating", "level", "nekomichi", "nekoumichi", "cat-logic"
)
ALWAYS_INCLUDE = {
    "package.json", "vite.config.js", "vite.config.ts", "index.html",
    "README.md", "README.txt"
}
MAX_FILE_BYTES = 500_000
MAX_TOTAL_BYTES = 8_000_000


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return any(part in EXCLUDED_DIRS for part in rel.parts) or path.suffix.lower() in EXCLUDED_SUFFIXES


def is_target(path: Path) -> bool:
    if not path.is_file() or is_excluded(path):
        return False
    if path.name in ALWAYS_INCLUDE:
        return True
    if path.suffix.lower() not in TARGET_SUFFIXES:
        return False
    lower = str(path.relative_to(ROOT)).lower()
    return any(word in lower for word in KEYWORDS)


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, capture_output=True,
            encoding="utf-8", errors="replace", timeout=20
        )
        text = (result.stdout + result.stderr).strip()
        return text or "(no output)"
    except Exception as exc:
        return f"(git command unavailable: {exc})"


def safe_text(path: Path) -> str:
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        return f"[SKIPPED: file too large ({size} bytes)]"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    sensitive_markers = ("private_key", "client_secret", "api_key=", "password=", "authorization: bearer")
    if any(marker in lowered for marker in sensitive_markers):
        return "[SKIPPED: possible credential or secret detected]"
    return text


def main() -> int:
    files = sorted((p for p in ROOT.rglob("*") if is_target(p)), key=lambda p: str(p).lower())
    lines = []
    lines.append("NEKOMICHI HIGH DIFFICULTY EVALUATOR AUDIT BEFORE V224")
    lines.append(f"Collected: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Project root: {ROOT}")
    lines.append("")
    lines.append("=== GIT STATUS ===")
    lines.append(run_git("status", "--short", "--branch"))
    lines.append("")
    lines.append("=== RECENT COMMITS ===")
    lines.append(run_git("log", "-n", "8", "--oneline", "--decorate"))
    lines.append("")
    lines.append("=== PROJECT TREE (selected, plus top-level) ===")
    top_level = sorted(p.name + ("/" if p.is_dir() else "") for p in ROOT.iterdir() if p.name not in EXCLUDED_DIRS)
    lines.extend(top_level)
    lines.append("")
    lines.append("=== SELECTED FILES ===")
    lines.extend(str(p.relative_to(ROOT)) for p in files)
    lines.append("")

    total = 0
    included = 0
    for path in files:
        rel = path.relative_to(ROOT)
        header = f"\n{'=' * 80}\nFILE: {rel}\n{'=' * 80}\n"
        content = safe_text(path)
        block_size = len((header + content).encode("utf-8", errors="replace"))
        if total + block_size > MAX_TOTAL_BYTES:
            lines.append(f"\n[STOPPED: collection reached {MAX_TOTAL_BYTES} bytes before {rel}]")
            break
        lines.append(header)
        lines.append(content)
        total += block_size
        included += 1

    lines.append("\n=== COLLECTION SUMMARY ===")
    lines.append(f"Matched files: {len(files)}")
    lines.append(f"Included files: {included}")
    lines.append(f"Approximate content bytes: {total}")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"SUCCESS: {OUTPUT.name}")
    print(f"Included files: {included}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
