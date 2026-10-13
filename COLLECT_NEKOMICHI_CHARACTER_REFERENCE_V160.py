from pathlib import Path
import json
import sys

ROOT = Path.cwd()
OUTPUT = ROOT / 'NEKOMICHI_CHARACTER_REFERENCE_V160.txt'
TARGET_WORDS = [
    'character reference', 'character-reference', 'character_reference',
    'キャラクターリファレンス', 'キャラクター', '仲間候補', '仲間広報'
]
TEXT_EXTENSIONS = {
    '.txt', '.md', '.json', '.js', '.css', '.html', '.htm',
    '.csv', '.tsv', '.yaml', '.yml'
}
EXCLUDED_DIRS = {
    '.git', 'node_modules', '.nekomichi-backups', 'dist', 'build',
    'android', '.gradle', '.idea', '.vscode'
}
MAX_FILE_BYTES = 2_000_000


def is_excluded(path):
    return any(part.lower() in {name.lower() for name in EXCLUDED_DIRS} for part in path.parts)


def score(path):
    value = str(path).lower()
    return sum(1 for word in TARGET_WORDS if word.lower() in value)


def find_target_dirs():
    candidates = []
    for path in ROOT.rglob('*'):
        if not path.is_dir() or is_excluded(path):
            continue
        points = score(path.relative_to(ROOT))
        if points:
            candidates.append((points, len(path.parts), path))
    candidates.sort(key=lambda item: (-item[0], item[1], str(item[2]).lower()))
    return [path for _, _, path in candidates]


def read_text(path):
    raw = path.read_bytes()
    for encoding in ('utf-8-sig', 'utf-8', 'cp932'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode('utf-8', errors='replace')


def main():
    target_dirs = find_target_dirs()
    if not target_dirs:
        raise RuntimeError(
            'Character Reference folder was not found under the project root. '
            'Expected a folder name containing キャラクターリファレンス, キャラクター, 仲間候補, or 仲間広報.'
        )

    # Keep the highest-ranked root and include all matching subfolders beneath it.
    target_root = target_dirs[0]
    files = []
    skipped = []
    for path in sorted(target_root.rglob('*'), key=lambda p: str(p).lower()):
        if not path.is_file() or is_excluded(path):
            continue
        rel = path.relative_to(ROOT)
        if path.stat().st_size > MAX_FILE_BYTES:
            skipped.append((str(rel), 'over 2 MB'))
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            skipped.append((str(rel), 'non-text extension'))
            continue
        files.append(path)

    if not files:
        raise RuntimeError('No readable text files were found in: ' + str(target_root.relative_to(ROOT)))

    lines = [
        'NEKOMICHI CHARACTER REFERENCE COLLECTION V160',
        '=' * 72,
        'Project root: ' + str(ROOT),
        'Collected root: ' + str(target_root.relative_to(ROOT)),
        'Collected files: ' + str(len(files)),
        'Skipped files: ' + str(len(skipped)),
        '',
        'DIRECTORY TREE',
        '-' * 72,
    ]
    for path in files:
        lines.append(str(path.relative_to(ROOT)))

    if skipped:
        lines.extend(['', 'SKIPPED FILES', '-' * 72])
        for name, reason in skipped:
            lines.append(f'{name} | {reason}')

    for path in files:
        rel = path.relative_to(ROOT)
        lines.extend([
            '',
            '=' * 72,
            'FILE: ' + str(rel),
            '=' * 72,
            read_text(path),
        ])

    OUTPUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('OK: Character Reference materials were collected.')
    print('ROOT:', target_root.relative_to(ROOT))
    print('FILES:', len(files))
    print('SKIPPED:', len(skipped))
    print('OUTPUT:', OUTPUT.name)
    print('SEND: Upload only ' + OUTPUT.name + ' to Copilot.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc)
        sys.exit(1)
