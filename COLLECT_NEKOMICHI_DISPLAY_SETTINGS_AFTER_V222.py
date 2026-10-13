from pathlib import Path
import sys

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_DISPLAY_SETTINGS_AFTER_V222.txt'
REQUIRED = ['index.html', 'game.js', 'style.css', 'app-config.js', 'foundation-manifest.json']
OPTIONAL = ['stages.js', 'storage.js', 'screen-manager.js', 'event-manager.js']


def read_text(path):
    for enc in ('utf-8', 'utf-8-sig', 'cp932'):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
    return path.read_text(encoding='utf-8', errors='replace')


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        print('ERROR: Missing required files:', ', '.join(missing))
        return 1

    files = [ROOT / name for name in REQUIRED]
    files.extend(ROOT / name for name in OPTIONAL if (ROOT / name).is_file())

    parts = [
        'NEKOMICHI DISPLAY SETTINGS AFTER V222',
        f'ROOT: {ROOT}',
        'PURPOSE: diagnose the Settings button that stopped opening after V222.',
        'FILES: ' + ', '.join(path.name for path in files),
        ''
    ]
    for path in files:
        parts.append(f'===== FILE: {path.name} =====')
        parts.append(read_text(path))
        parts.append(f'===== END FILE: {path.name} =====')
        parts.append('')

    OUT.write_text('\n'.join(parts), encoding='utf-8')
    size = OUT.stat().st_size
    if size < 10000:
        print(f'ERROR: Output unexpectedly small: {size} bytes')
        return 1

    print('OK: Collected the V222 display-settings runtime structure.')
    print('OK: No game files were modified.')
    print(f'OK: Output size: {size} bytes')
    print('OUTPUT:', OUT)
    print('SEND: Upload only NEKOMICHI_DISPLAY_SETTINGS_AFTER_V222.txt to Copilot.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
