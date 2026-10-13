from pathlib import Path
import sys

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_DISPLAY_SETTINGS_INPUT_V220.txt'
FILES = ['index.html', 'game.js', 'style.css', 'sw.js']

def main():
    missing = [name for name in FILES if not (ROOT / name).exists()]
    if missing:
        print('ERROR: Missing:', ', '.join(missing))
        return 1
    parts = []
    for name in FILES:
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        parts.append(f'===== FILE: {name} =====\n{text}\n===== END FILE: {name} =====\n')
    OUT.write_text('\n'.join(parts), encoding='utf-8')
    print('OK: Collected current display-settings implementation files.')
    print('OUTPUT:', OUT)
    print('SEND: NEKOMICHI_DISPLAY_SETTINGS_INPUT_V220.txt')
    return 0

if __name__ == '__main__':
    sys.exit(main())
