from pathlib import Path
import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
OUTPUT = ROOT / 'NEKOMICHI_CHARACTER_REFERENCE_V161.txt'
ROOT_NAMES = {
    'character_reference', 'character-reference', 'character reference',
    'キャラクターリファレンス'
}
TEXT_EXTENSIONS = {'.txt','.md','.json','.js','.css','.html','.htm','.csv','.tsv','.yaml','.yml'}
OFFICE_EXTENSIONS = {'.docx','.xlsx','.pptx'}
PDF_EXTENSIONS = {'.pdf'}
EXCLUDED_DIRS = {'.git','node_modules','.nekomichi-backups','dist','build','android','.gradle','.idea','.vscode'}
MAX_FILE_BYTES = 10_000_000


def excluded(path):
    blocked = {x.lower() for x in EXCLUDED_DIRS}
    return any(part.lower() in blocked for part in path.parts)


def normalized_name(path):
    return path.name.strip().lower().replace(' ', '_').replace('-', '_')


def find_root():
    exact = []
    broad = []
    for path in ROOT.rglob('*'):
        if not path.is_dir() or excluded(path):
            continue
        name = normalized_name(path)
        if name == 'character_reference' or path.name == 'キャラクターリファレンス':
            exact.append(path)
        elif 'character' in name or 'キャラクター' in path.name:
            broad.append(path)
    choices = exact or broad
    if not choices:
        raise RuntimeError('character_reference folder was not found under the project root')
    choices.sort(key=lambda p: (len(p.relative_to(ROOT).parts), str(p).lower()))
    return choices[0]


def decode_bytes(raw):
    for enc in ('utf-8-sig','utf-8','cp932','shift_jis'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')


def xml_text(raw):
    root = ET.fromstring(raw)
    chunks = []
    for elem in root.iter():
        tag = elem.tag.rsplit('}',1)[-1]
        if tag in {'t','v'} and elem.text:
            chunks.append(elem.text)
        elif tag in {'p','tr'}:
            chunks.append('\n')
        elif tag in {'tab','tc'}:
            chunks.append('\t')
    return ''.join(chunks).strip()


def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        names = ['word/document.xml']
        names += sorted(n for n in z.namelist() if n.startswith('word/header') and n.endswith('.xml'))
        names += sorted(n for n in z.namelist() if n.startswith('word/footer') and n.endswith('.xml'))
        parts = [xml_text(z.read(n)) for n in names if n in z.namelist()]
    return '\n\n'.join(x for x in parts if x)


def extract_xlsx(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root:
                shared.append(''.join(t.text or '' for t in si.iter() if t.tag.rsplit('}',1)[-1]=='t'))
        rows = []
        for name in sorted(n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')):
            root = ET.fromstring(z.read(name))
            rows.append('[' + name + ']')
            for row in root.iter():
                if row.tag.rsplit('}',1)[-1] != 'row':
                    continue
                values = []
                for cell in row:
                    if cell.tag.rsplit('}',1)[-1] != 'c':
                        continue
                    typ = cell.attrib.get('t')
                    value = next((x.text for x in cell.iter() if x.tag.rsplit('}',1)[-1]=='v'), '') or ''
                    if typ == 's' and value.isdigit() and int(value) < len(shared):
                        value = shared[int(value)]
                    inline = ''.join(x.text or '' for x in cell.iter() if x.tag.rsplit('}',1)[-1]=='t')
                    values.append(inline or value)
                if values:
                    rows.append('\t'.join(values))
    return '\n'.join(rows)


def extract_pptx(path):
    with zipfile.ZipFile(path) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=lambda n:int(re.search(r'\d+',n).group()))
        parts = []
        for name in names:
            parts.append('[' + name + ']\n' + xml_text(z.read(name)))
    return '\n\n'.join(parts)


def extract_pdf(path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return '\n\n'.join((page.extract_text() or '') for page in reader.pages).strip()
    except Exception as exc:
        return '[PDF text extraction unavailable: ' + str(exc) + ']'


def extract(path):
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return decode_bytes(path.read_bytes())
    if ext == '.docx':
        return extract_docx(path)
    if ext == '.xlsx':
        return extract_xlsx(path)
    if ext == '.pptx':
        return extract_pptx(path)
    if ext == '.pdf':
        return extract_pdf(path)
    return None


def main():
    target = find_root()
    all_files = [p for p in target.rglob('*') if p.is_file() and not excluded(p)]
    if not all_files:
        raise RuntimeError('No files were found under: ' + str(target.relative_to(ROOT)))

    collected = []
    listed_only = []
    errors = []
    for path in sorted(all_files, key=lambda p: str(p).lower()):
        rel = path.relative_to(ROOT)
        if path.stat().st_size > MAX_FILE_BYTES:
            listed_only.append((str(rel), 'over 10 MB'))
            continue
        try:
            content = extract(path)
            if content is None:
                listed_only.append((str(rel), 'binary/image or unsupported extension'))
            else:
                collected.append((str(rel), content if content.strip() else '[No extractable text]'))
        except Exception as exc:
            errors.append((str(rel), str(exc)))

    lines = [
        'NEKOMICHI CHARACTER REFERENCE COLLECTION V161',
        '=' * 72,
        'Project root: ' + str(ROOT),
        'Collected root: ' + str(target.relative_to(ROOT)),
        'All files: ' + str(len(all_files)),
        'Text extracted: ' + str(len(collected)),
        'Listed only: ' + str(len(listed_only)),
        'Errors: ' + str(len(errors)),
        '', 'DIRECTORY FILE LIST', '-' * 72,
    ]
    lines.extend(str(p.relative_to(ROOT)) for p in sorted(all_files, key=lambda p: str(p).lower()))

    if listed_only:
        lines.extend(['', 'LISTED ONLY', '-' * 72])
        lines.extend(name + ' | ' + reason for name, reason in listed_only)
    if errors:
        lines.extend(['', 'EXTRACTION ERRORS', '-' * 72])
        lines.extend(name + ' | ' + reason for name, reason in errors)
    for name, content in collected:
        lines.extend(['', '=' * 72, 'FILE: ' + name, '=' * 72, content])

    OUTPUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('OK: Character Reference materials were collected.')
    print('ROOT:', target.relative_to(ROOT))
    print('ALL FILES:', len(all_files))
    print('TEXT EXTRACTED:', len(collected))
    print('LISTED ONLY:', len(listed_only))
    print('ERRORS:', len(errors))
    print('OUTPUT:', OUTPUT.name)
    print('SEND: Upload only ' + OUTPUT.name + ' to Copilot.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc)
        sys.exit(1)
