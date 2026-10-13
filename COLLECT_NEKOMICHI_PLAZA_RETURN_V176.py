from pathlib import Path
import sys, time

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_PLAZA_RETURN_BEFORE_V176.txt'
FILES = [
    'index.html',
    'game.js',
    'screen-service.js',
    'style.css',
    'app-config.js',
    'foundation-manifest.json',
]
TOKENS = {
    'index.html': ['plazaBtn', 'plazaDlg', 'plazaReturnDlg', 'fieldMapDlg'],
    'game.js': ['requestPlazaReturn', 'confirmPlazaReturn', 'openPlaza', 'closePlaza', 'installPlazaReturnEvents', 'plazaClose', 'saveBoard'],
    'screen-service.js': ['plazaReturn', 'fieldMap', 'openDialog', 'closeDialog'],
    'style.css': ['plaza-return-dialog', 'plaza-shell', 'field-map'],
    'app-config.js': ['VERSION'],
    'foundation-manifest.json': ['foundationVersion', 'puzzleToPlazaConfirmationV0868', 'nextSafeWork'],
}

def excerpt(text, token, radius=1800):
    index = text.find(token)
    if index < 0:
        return '[NOT FOUND] ' + token + '\n'
    start = max(0, index - radius)
    end = min(len(text), index + len(token) + radius)
    return '--- ' + token + ' @ ' + str(index) + ' ---\n' + text[start:end] + '\n'

def main():
    if not (ROOT / '.git').exists():
        print('ERROR: Run from cat-logic-puzzle project root')
        return 1
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        print('ERROR: Missing files: ' + ', '.join(missing))
        return 1

    parts = [
        'NEKOMICHI PLAZA RETURN AUDIT BEFORE V176',
        'Generated: ' + time.strftime('%Y-%m-%d %H:%M:%S'),
        'Project: ' + str(ROOT),
        '',
    ]
    for name in FILES:
        text = (ROOT / name).read_text(encoding='utf-8', errors='replace')
        parts.extend(['=' * 80, name, '=' * 80])
        for token in TOKENS[name]:
            parts.append(excerpt(text, token))

    content = '\n'.join(parts)
    OUT.write_text(content, encoding='utf-8-sig')
    size = OUT.stat().st_size
    if size < 5000:
        print('ERROR: Output is unexpectedly small: ' + str(size) + ' bytes')
        return 1

    print('OK: Nekomichi plaza return audit V176 collected.')
    print('OK: Output size: ' + str(size) + ' bytes')
    print('OUTPUT: ' + str(OUT))
    print('SEND: NEKOMICHI_PLAZA_RETURN_BEFORE_V176.txt')
    return 0

if __name__ == '__main__':
    sys.exit(main())
