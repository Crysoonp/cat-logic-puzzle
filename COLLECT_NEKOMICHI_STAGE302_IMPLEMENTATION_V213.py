from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_STAGE302_IMPLEMENTATION_INPUT_V213.txt'
MAX_FILE_BYTES = 2_000_000
TEXT_EXTS = {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.json', '.html', '.css', '.md'}
SKIP_DIRS = {'.git', 'node_modules', 'dist', 'build', 'android', 'ios', '.gradle', '.idea', '.vscode', '__pycache__'}
KEYWORDS = (
    'stage', 'stages', 'puzzle', 'board', 'region', 'solution', 'level',
    'map', 'progress', 'hint', 'game', 'catalog', 'registry'
)
PRIORITY_NAMES = {
    'package.json', 'index.html', 'game.js', 'app.js', 'main.js', 'script.js',
    'stages.js', 'stages.json', 'levels.js', 'levels.json', 'puzzles.js',
    'puzzles.json', 'stage-data.js', 'stage-data.json', 'README.md'
}
REQUIRED_JSON = 'NEKOMICHI_12X12_REPAIRED_CANDIDATES_V211.json'

def allowed(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.suffix.lower() not in TEXT_EXTS:
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    return 0 < size <= MAX_FILE_BYTES

def score(path: Path) -> int:
    name = path.name.lower()
    rel = str(path.relative_to(ROOT)).lower()
    value = 0
    if path.name in PRIORITY_NAMES or name in {n.lower() for n in PRIORITY_NAMES}:
        value += 100
    value += sum(12 for k in KEYWORDS if k in name)
    value += sum(2 for k in KEYWORDS if k in rel)
    if name.startswith(('update_', 'audit_', 'collect_', 'repair_', 'benchmark_')):
        value -= 100
    return value

def main():
    files = [p for p in ROOT.rglob('*') if p.is_file() and allowed(p)]
    ranked = sorted(files, key=lambda p: (-score(p), str(p).lower()))
    selected = [p for p in ranked if score(p) > 0][:30]

    required = ROOT / REQUIRED_JSON
    if required.exists() and required not in selected:
        selected.insert(0, required)

    lines = [
        'NEKOMICHI STAGE 302 IMPLEMENTATION INPUT V213',
        f'Generated: {datetime.now().isoformat(timespec="seconds")}',
        f'Root: {ROOT}',
        f'Required candidate present: {required.exists()}',
        f'Selected files: {len(selected)}',
        '',
        'PURPOSE:',
        '- Implement the V211 repaired 12x12 unique-solution candidate as trial Stage 302.',
        '- Keep it uncommitted to final difficulty until user playtesting.',
        '- Preserve existing Stage 1-301 behavior, map flow, save compatibility, and hints.',
        '',
        'FILE INDEX:'
    ]
    for p in selected:
        lines.append(f'- {p.relative_to(ROOT)} ({p.stat().st_size} bytes, score={score(p)})')

    for p in selected:
        rel = p.relative_to(ROOT)
        lines += ['', '=' * 88, f'FILE: {rel}', '=' * 88]
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            text = p.read_text(encoding='utf-8', errors='replace')
        lines.append(text)

    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print('OK: Stage 302 implementation files collected.')
    print('OUTPUT:', OUT)
    print('SEND: Upload NEKOMICHI_STAGE302_IMPLEMENTATION_INPUT_V213.txt to Copilot.')
    if not required.exists():
        print('WARNING: Required V211 candidate JSON was not found in the project root.')

if __name__ == '__main__':
    main()
