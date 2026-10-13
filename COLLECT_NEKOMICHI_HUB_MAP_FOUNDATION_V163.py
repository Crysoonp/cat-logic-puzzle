from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path.cwd()
OUTPUT = ROOT / 'NEKOMICHI_HUB_MAP_FOUNDATION_V163.txt'
MAX_TEXT_BYTES = 4_000_000

CORE_NAMES = {
    'index.html', 'game.js', 'style.css', 'stages.js', 'app-config.js',
    'foundation-manifest.json', 'manifest.json', 'package.json',
    'service-worker.js', 'sw.js', 'README.md', 'STORY_BIBLE.md',
    'STORY_BIBLE_FAMILY_UPDATE.md'
}
TEXT_EXTENSIONS = {
    '.html', '.htm', '.js', '.mjs', '.cjs', '.css', '.json', '.md',
    '.txt', '.yaml', '.yml', '.xml'
}
EXCLUDED_DIRS = {
    '.git', 'node_modules', '.nekomichi-backups', 'dist', 'build',
    'android', '.gradle', '.idea', '.vscode', '__pycache__'
}
RELEVANT_WORDS = (
    'stage', 'screen', 'view', 'route', 'nav', 'save', 'storage', 'state',
    'hint', 'dialog', 'modal', 'chapter', 'story', 'character', 'profile',
    'map', 'hub', 'plaza', 'service-worker', 'serviceworker', 'cache',
    '森の広場', '仲間', 'ヒント', 'ステージ', '画面', '保存', '物語'
)


def is_excluded(path):
    blocked = {name.lower() for name in EXCLUDED_DIRS}
    return any(part.lower() in blocked for part in path.parts)


def decode(path):
    raw = path.read_bytes()
    for encoding in ('utf-8-sig', 'utf-8', 'cp932', 'shift_jis'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(command):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        'command': ' '.join(command),
        'exitCode': result.returncode,
        'stdout': result.stdout.strip(),
        'stderr': result.stderr.strip(),
    }


def select_files():
    selected = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or is_excluded(path):
            continue
        rel = path.relative_to(ROOT)
        rel_lower = str(rel).lower()
        name_lower = path.name.lower()
        if path.name in CORE_NAMES or name_lower in {n.lower() for n in CORE_NAMES}:
            selected.append(path)
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(word.lower() in rel_lower for word in RELEVANT_WORDS):
            selected.append(path)
    return sorted(set(selected), key=lambda p: str(p).lower())


def main():
    required = ['index.html', 'game.js', 'style.css', 'stages.js']
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError('missing project files: ' + ', '.join(missing))

    files = select_files()
    if not files:
        raise RuntimeError('no relevant project files found')

    metadata = []
    included = []
    listed_only = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        size = path.stat().st_size
        item = {
            'path': rel,
            'size': size,
            'sha256': sha256(path),
        }
        metadata.append(item)
        if size <= MAX_TEXT_BYTES:
            included.append((rel, decode(path)))
        else:
            listed_only.append((rel, size, 'over 4 MB'))

    syntax_checks = []
    for path in files:
        if path.suffix.lower() == '.js' and path.stat().st_size <= MAX_TEXT_BYTES:
            syntax_checks.append(command_output(['node', '--check', str(path.relative_to(ROOT))]))

    git_info = []
    if (ROOT / '.git').exists():
        git_info.extend([
            command_output(['git', 'status', '--short']),
            command_output(['git', 'branch', '--show-current']),
            command_output(['git', 'log', '-1', '--oneline']),
        ])

    version_hits = []
    version_pattern = re.compile(r'Ver\.\d+(?:\.\d+){1,3}|\b\d+\.\d+\.\d+\b')
    for rel, content in included:
        hits = sorted(set(version_pattern.findall(content)))
        if hits:
            version_hits.append({'path': rel, 'values': hits[:30]})

    lines = [
        'NEKOMICHI HUB AND MAP FOUNDATION COLLECTION V163',
        '=' * 80,
        'Purpose: pre-implementation audit for Forest Plaza, cat records, map,',
        '         return-to-plaza navigation, companion selection and save compatibility.',
        'Project root: ' + str(ROOT),
        'Selected files: ' + str(len(files)),
        'Included text files: ' + str(len(included)),
        'Listed only: ' + str(len(listed_only)),
        '',
        'IMPORTANT',
        '-' * 80,
        'This collector does not modify the game.',
        'It gathers the current implementation before the first feature update.',
        '',
        'FILE METADATA',
        '-' * 80,
        json.dumps(metadata, ensure_ascii=False, indent=2),
        '',
        'VERSION HITS',
        '-' * 80,
        json.dumps(version_hits, ensure_ascii=False, indent=2),
        '',
        'GIT INFORMATION',
        '-' * 80,
        json.dumps(git_info, ensure_ascii=False, indent=2),
        '',
        'JAVASCRIPT SYNTAX CHECKS',
        '-' * 80,
        json.dumps(syntax_checks, ensure_ascii=False, indent=2),
    ]

    if listed_only:
        lines.extend([
            '', 'LISTED ONLY', '-' * 80,
            json.dumps(listed_only, ensure_ascii=False, indent=2),
        ])

    for rel, content in included:
        lines.extend([
            '', '=' * 80,
            'FILE: ' + rel,
            '=' * 80,
            content,
        ])

    OUTPUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    failed_syntax = [x for x in syntax_checks if x['exitCode'] != 0]
    print('OK: hub/map foundation collection completed.')
    print('FILES:', len(files))
    print('INCLUDED:', len(included))
    print('LISTED ONLY:', len(listed_only))
    print('JS CHECKS:', len(syntax_checks))
    print('JS FAILURES:', len(failed_syntax))
    print('OUTPUT:', OUTPUT.name)
    print('SEND: Upload only ' + OUTPUT.name + ' to Copilot.')
    if failed_syntax:
        print('WARNING: Existing JavaScript syntax failures were recorded in the report.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc)
        sys.exit(1)
