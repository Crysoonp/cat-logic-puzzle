from pathlib import Path
from datetime import datetime
import subprocess

ROOT = Path(__file__).resolve().parent
COMMIT_MESSAGE = "Save V235 constraint-chain design foundation"
REPORT = ROOT / "NEKOMICHI_GIT_SAVE_V235.txt"


def run(args, check=True):
    p = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    output = (p.stdout + p.stderr).strip()
    if output:
        print(output)
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(args)}")
    return p.returncode, output


def main():
    if not (ROOT / ".git").exists():
        print("ERROR: Run this file from the cat-logic-puzzle project root.")
        return 1

    report = [
        "NEKOMICHI GIT SAVE V235",
        f"Started: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    _, before = run(["git", "status", "--short", "--branch"])
    report += ["=== STATUS BEFORE ===", before or "(clean)", ""]

    # Keep local/generated caches out of the commit when present.
    excluded = [
        "node_modules",
        "dist",
        "build",
        ".gradle",
        "android/.gradle",
        "__pycache__",
    ]
    run(["git", "add", "-A"])
    for name in excluded:
        run(["git", "reset", "--", name], check=False)

    _, staged = run(["git", "diff", "--cached", "--name-status"])
    report += ["=== STAGED FILES ===", staged or "(none)", ""]

    if not staged:
        report += ["No changes to commit."]
        print("No changes to commit.")
    else:
        run(["git", "commit", "-m", COMMIT_MESSAGE])
        report += [f"Commit message: {COMMIT_MESSAGE}", ""]

    _, branch = run(["git", "branch", "--show-current"])
    _, remote = run(["git", "remote", "get-url", "origin"], check=False)
    report += ["=== REPOSITORY ===", f"Branch: {branch}", f"Origin: {remote or '(none)'}", ""]

    pushed = False
    if remote:
        code, push_output = run(["git", "push", "origin", branch], check=False)
        report += ["=== PUSH ===", push_output or f"exit {code}", ""]
        if code != 0:
            REPORT.write_text("\n".join(report), encoding="utf-8")
            print("ERROR: Git commit succeeded, but GitHub push failed.")
            print(f"WROTE: {REPORT.name}")
            return code
        pushed = True

    _, head = run(["git", "log", "-1", "--oneline", "--decorate"])
    _, after = run(["git", "status", "--short", "--branch"])
    report += [
        "=== SAVED HEAD ===",
        head,
        "",
        "=== STATUS AFTER ===",
        after or "(clean)",
        "",
        f"GitHub push: {'SUCCESS' if pushed else 'SKIPPED (no origin)'}",
        "SUCCESS: V235 state saved to Git",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"WROTE: {REPORT.name}")
    print("SUCCESS: V235 state saved to Git")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
