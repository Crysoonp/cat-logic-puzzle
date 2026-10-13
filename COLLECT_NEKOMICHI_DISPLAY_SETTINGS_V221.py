from pathlib import Path
import sys

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_DISPLAY_SETTINGS_INPUT_V221.txt'
REQUIRED = ['index.html', 'game.js', 'style.css']
OPTIONAL_NAMES = [
    'app-config.js', 'service-worker.js', 'service_worker.js', 'sw.js',
    'manifest.json', 'foundation-manifest.json'
]
TEXT_SUFFIXES = {'.js', '.css', '.html', '.json', '.md', '.txt'}


def read_text(path):
    for enc in ('utf-8', 'utf-8-sig', 'cp932'):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
    return path.read_text(encoding='utf-8', errors='replace')


def find_version_and_worker_files():
    found = []
    seen = set()
    for name in OPTIONAL_NAMES:
        p = ROOT / name
        if p.is_file():
            found.append(p)
            seen.add(p.resolve())
    for p in ROOT.iterdir():
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        low = p.name.lower()
        if any(token in low for token in ('version', 'config', 'worker', 'manifest')):
            rp = p.resolve()
            if rp not in seen:
                found.append(p)
                seen.add(rp)
    return found


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        print('ERROR: Missing required files:', ', '.join(missing))
        return 1

    files = [ROOT / name for name in REQUIRED]
    files.extend(find_version_and_worker_files())

    parts = [
        'NEKOMICHI DISPLAY SETTINGS COLLECTION V221',
        f'ROOT: {ROOT}',
        'NOTE: sw.js is optional. The collector records the actual service-worker/version files found.',
        'FILES: ' + ', '.join(p.name for p in files),
        ''
    ]
    for path in files:
        text = read_text(path)
        parts.append(f'===== FILE: {path.name} =====')
        parts.append(text)
        parts.append(f'===== END FILE: {path.name} =====')
        parts.append('')

    OUT.write_text('\n'.join(parts), encoding='utf-8')
    size = OUT.stat().st_size
    if size < 5000:
        print(f'ERROR: Output unexpectedly small: {size} bytes')
        return 1

    print('OK: Collected current display-settings implementation files.')
    print('OK: sw.js was treated as optional; actual worker/version files were auto-detected.')
    print(f'OK: Output size: {size} bytes')
    print('OUTPUT:', OUT)
    print('SEND: Upload only NEKOMICHI_DISPLAY_SETTINGS_INPUT_V221.txt to Copilot.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
