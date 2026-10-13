from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'NEKOMICHI_GENERATOR_GATE_BEFORE_V226.txt'
FILES=[
 'stage-generator.js','logic-engine.js','quality-engine.js','difficulty-manager.js',
 'generator_config.json','package.json'
]

def main():
 lines=['NEKOMICHI GENERATOR GATE BEFORE V226','']
 p=subprocess.run(['git','status','--short','--branch'],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
 lines += ['=== GIT STATUS ===',(p.stdout+p.stderr).strip(),'']
 found=0
 for name in FILES:
  path=ROOT/name
  lines += ['='*80,f'FILE: {name}','='*80]
  if not path.is_file():
   lines += ['[MISSING]',''];continue
  text=path.read_text(encoding='utf-8',errors='replace')
  lines += [text,''];found+=1
 lines += ['=== TARGETED SEARCH ===']
 for path in ROOT.rglob('*.js'):
  if any(x in path.parts for x in ('.git','node_modules','dist','build')):continue
  text=path.read_text(encoding='utf-8',errors='replace')
  hits=[]
  for i,line in enumerate(text.splitlines(),1):
   lower=line.lower()
   if any(k in lower for k in ('function evaluate(','highdifficultycandidate','targetrange(','advanceddifficulty')):
    hits.append(f'{i}: {line}')
  if hits:
   lines += [f'FILE: {path.relative_to(ROOT)}',*hits,'']
 OUT.write_text('\n'.join(lines),encoding='utf-8')
 print(f'SUCCESS: {OUT.name}')
 print(f'Included core files: {found}')
 return 0
if __name__=='__main__':raise SystemExit(main())
