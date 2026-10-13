from pathlib import Path
import re, sys, time

ROOT=Path.cwd()
OUT=ROOT/'NEKOMICHI_PLAZA_RETURN_BEFORE_V175.txt'
FILES=['index.html','game.js','screen-service.js','style.css','app-config.js','foundation-manifest.json']
PATTERNS={
 'index.html':['plazaBtn','plazaDlg','plazaReturnDlg','fieldMapDlg'],
 'game.js':['function requestPlazaReturn','function confirmPlazaReturn','function openPlaza','function closePlaza','installPlazaReturnEvents','plazaClose','saveBoard'],
 'screen-service.js':['plazaReturn','fieldMap','openDialog','closeDialog'],
 'style.css':['plaza-return-dialog','plaza-shell','field-map'],
 'app-config.js':['VERSION'],
 'foundation-manifest.json':['foundationVersion','puzzleToPlazaConfirmationV0868','nextSafeWork'],
}

def excerpt(text, token, radius=1200):
    i=text.find(token)
    if i<0:return f'[NOT FOUND] {token}\n'
    a=max(0,i-radius); b=min(len(text),i+len(token)+radius)
    return f'--- {token} @ {i} ---\n{text[a:b]}\n'

def main():
    if not (ROOT/'.git').exists():
        print('ERROR: Run from cat-logic-puzzle project root'); return 1
    missing=[n for n in FILES if not (ROOT/n).is_file()]
    if missing:
        print('ERROR: Missing files:',', '.join(missing)); return 1
    parts=[
      'NEKOMICHI PLAZA RETURN AUDIT BEFORE V175',
      'Generated: '+time.strftime('%Y-%m-%d %H:%M:%S'),
      'Project: '+str(ROOT),
      ''
    ]
    for name in FILES:
        text=(ROOT/name).read_text(encoding='utf-8',errors='replace')
        parts += ['='*80, name, '='*80]
        for token in PATTERNS[name]: parts.append(excerpt(text,token))
    OUT.write_text('\n'.join(parts),encoding='utf-8')
    print('OK: Nekomichi plaza return audit collected.')
    print('OUTPUT:',OUT)
    print('SEND: NEKOMICHI_PLAZA_RETURN_BEFORE_V175.txt')
    return 0

if __name__=='__main__': sys.exit(main())
