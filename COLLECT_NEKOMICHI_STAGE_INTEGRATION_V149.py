from pathlib import Path
import json, re, sys

ROOT=Path.cwd()
OUT=ROOT/'NEKOMICHI_STAGE_INTEGRATION_BEFORE_V149.txt'
EXCLUDE={'.git','node_modules','.nekomichi-backups','dist','build','android','.gradle'}
MAX_FILE=2_000_000

try:
    candidates=[]
    priority=['app-config.js','foundation-manifest.json','index.html','game.js']
    for name in priority:
        p=ROOT/name
        if p.is_file():candidates.append(p)
    patterns=[re.compile(x,re.I) for x in [r'\bstage\s*[:=]\s*50\b',r'\bstage\s*[:=]\s*51\b',r'\bPUZZLES\b',r'\bSTAGES\b',r'challenge-100',r'stageData',r'puzzleData']]
    for p in ROOT.rglob('*'):
        if not p.is_file() or p in candidates:continue
        if any(part in EXCLUDE for part in p.relative_to(ROOT).parts):continue
        if p.suffix.lower() not in {'.js','.json','.html','.css'}:continue
        if p.stat().st_size>MAX_FILE:continue
        try:text=p.read_text(encoding='utf-8-sig',errors='replace')
        except Exception:continue
        if any(rx.search(text) for rx in patterns):candidates.append(p)
    # Keep exact files only, deduplicated and sorted, with core files first.
    seen=set();ordered=[]
    for p in candidates:
        key=str(p.resolve()).lower()
        if key not in seen:seen.add(key);ordered.append(p)
    if len(ordered)>30:
        raise RuntimeError('too many matching files; collector stopped safely: '+str(len(ordered)))
    chunks=['NEKOMICHI STAGE 51-100 INTEGRATION COLLECTION','ROOT: '+str(ROOT),'FILES: '+str(len(ordered)),'']
    for p in ordered:
        rel=p.relative_to(ROOT).as_posix()
        text=p.read_text(encoding='utf-8-sig',errors='replace')
        chunks += ['='*80,'FILE: '+rel,'SIZE: '+str(p.stat().st_size),'='*80,text,'']
    OUT.write_text('\n'.join(chunks),encoding='utf-8')
    print('OK: Nekomichi Stage 51-100 integration files were collected.')
    print('FILES: '+str(len(ordered)))
    for p in ordered:print(' - '+p.relative_to(ROOT).as_posix())
    print('OUTPUT: '+OUT.name)
    print('SEND: Upload only '+OUT.name+' to Copilot.')
except Exception as e:
    print('ERROR: '+str(e));sys.exit(1)
