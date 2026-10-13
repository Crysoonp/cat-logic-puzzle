from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_CAT_PROFILE_STRUCTURE_BEFORE_V177.txt'

FILES = [
    'index.html',
    'game.js',
    'style.css',
    'screen-service.js',
    'storage-service.js',
    'event-service.js',
    'stories.js',
    'app-config.js',
    'foundation-manifest.json',
]

TOKENS = {
    'index.html': [
        'catsDlg', 'catsClose', 'catsList', 'catsBtn',
        'plazaTree', 'plazaDlg', 'plazaMessage'
    ],
    'game.js': [
        'function renderCats', 'function openCats', 'function closeCats',
        'catsList', 'catsClose', 'catsBtn', 'plazaTree',
        'clpTaijuJoined', 'taiju', 'nyanjii', 'teko',
        'window.CLPScreens.openDialog', 'window.CLPScreens.closeDialog'
    ],
    'style.css': [
        'cats-dialog', 'cats-list', 'cat-card', 'cats-lead',
        'plaza-tree', 'plaza-dialog'
    ],
    'screen-service.js': [
        "cats:'catsDlg'", 'catsDlg', 'openDialog', 'closeDialog', 'dialogMap'
    ],
    'storage-service.js': [
        'KEYS', 'history', 'taiju', 'setItem', 'getJSON'
    ],
    'event-service.js': [
        'bind', 'bindOnce', 'catsClose', 'catsBtn'
    ],
    'stories.js': [
        'taiju', 'nyanjii', 'teko', 'stage', 'story'
    ],
    'app-config.js': ['VERSION'],
    'foundation-manifest.json': [
        'foundationVersion', 'saveSchemaVersion', 'boardSaveVersion',
        'plazaCloseDestinationV0869', 'nextSafeWork'
    ],
}

REFERENCE_NAMES = [
    'STORY_BIBLE.md',
    'STORY_BIBLE_FAMILY_UPDATE.md',
    'NEKOMICHI_CHARACTER_REFERENCE_V161.txt',
]

REFERENCE_TOKENS = [
    'テコちゃん', 'ニャンじい', 'タイジュ',
    '出会った猫', '猫じゃらし', '森の広場'
]


def excerpt(text, token, radius=2200):
    positions = []
    start = 0
    while len(positions) < 3:
        index = text.find(token, start)
        if index < 0:
            break
        positions.append(index)
        start = index + max(1, len(token))
    if not positions:
        return f'[NOT FOUND] {token}\n'
    chunks = []
    for number, index in enumerate(positions, 1):
        left = max(0, index - radius)
        right = min(len(text), index + len(token) + radius)
        chunks.append(
            f'--- {token} occurrence {number} @ {index} ---\n'
            + text[left:right]
            + '\n'
        )
    return '\n'.join(chunks)


def run_check(filename):
    result = subprocess.run(
        ['node', '--check', filename],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    return {
        'file': filename,
        'passed': result.returncode == 0,
        'stdout': result.stdout.strip(),
        'stderr': result.stderr.strip(),
    }


def main():
    if not (ROOT / '.git').exists():
        print('ERROR: Run this file from the cat-logic-puzzle project root.')
        return 1

    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        print('ERROR: Required files missing: ' + ', '.join(missing))
        return 1

    parts = [
        'NEKOMICHI CAT PROFILE STRUCTURE AUDIT BEFORE V177',
        'Generated: ' + time.strftime('%Y-%m-%d %H:%M:%S'),
        'Project: ' + str(ROOT),
        '',
        'PURPOSE',
        '- Inspect the current Cats list before splitting list and detail views.',
        '- Preserve Forest Plaza as the only normal entry point.',
        '- Do not change game files.',
        '',
    ]

    checks = []
    for name in FILES:
        path = ROOT / name
        text = path.read_text(encoding='utf-8', errors='replace')
        parts.extend(['=' * 90, 'FILE: ' + name, '=' * 90])
        for token in TOKENS[name]:
            parts.append(excerpt(text, token))
        if name.endswith('.js'):
            checks.append(run_check(name))

    found_references = []
    for name in REFERENCE_NAMES:
        candidates = [ROOT / name, Path('/mnt/data') / name]
        path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if path is None:
            continue
        found_references.append(str(path))
        text = path.read_text(encoding='utf-8', errors='replace')
        parts.extend(['=' * 90, 'REFERENCE: ' + str(path), '=' * 90])
        for token in REFERENCE_TOKENS:
            parts.append(excerpt(text, token, radius=1400))

    summary = {
        'syntaxChecks': checks,
        'referenceFilesFound': found_references,
        'requiredDesignConstraints': {
            'wireframeRole': 'structure reference only, not final visual design',
            'normalEntryPoint': 'Forest Plaza large tree only',
            'directPuzzleToCatsNavigation': False,
            'stageGridExistingContract': '1 row = 10 stages; do not modify in profile work',
            'unknownCatsVisible': False,
            'unknownFactsVisible': False,
            'firstDetailTargets': ['teko', 'nyanjii', 'taiju'],
            'saveTextBodies': False,
            'saveStableIdsOnly': True,
        },
    }
    parts.extend(['=' * 90, 'AUDIT SUMMARY', '=' * 90, json.dumps(summary, ensure_ascii=False, indent=2)])

    OUT.write_text('\n'.join(parts), encoding='utf-8-sig')
    size = OUT.stat().st_size
    js_failures = [item['file'] for item in checks if not item['passed']]
    if size < 15000:
        print(f'ERROR: Output unexpectedly small: {size} bytes')
        return 1
    if js_failures:
        print('ERROR: Existing JavaScript syntax failures: ' + ', '.join(js_failures))
        return 1

    print('OK: Nekomichi cat-profile structure audit collected.')
    print('OK: Existing JavaScript syntax checks passed.')
    print('OK: Output size: ' + str(size) + ' bytes')
    print('OUTPUT: ' + str(OUT))
    print('SEND: Upload only NEKOMICHI_CAT_PROFILE_STRUCTURE_BEFORE_V177.txt to Copilot.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
