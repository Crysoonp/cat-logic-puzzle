from pathlib import Path
from datetime import datetime
import subprocess

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/'NEKOMICHI_EVALUATOR_CORE_BEFORE_V224.txt'
FILES=[
 'logic-engine.js','difficulty-manager.js','analysis-engine.js','assumption-engine.js',
 'quality-engine.js','stage-generator.js','generator_config.json','stages.js',
 'BENCHMARK_NEKOMICHI_STAGE_GENERATOR_V206.py',
 'BENCHMARK_NEKOMICHI_LARGE_BOARD_GENERATOR_V207.py',
 'BENCHMARK_NEKOMICHI_12X12_GENERATOR_V208.py',
 'BENCHMARK_NEKOMICHI_12X12_UNIQUENESS_V209.py',
 'AUDIT_NEKOMICHI_12X12_LOGIC_V212.py',
 'NEKOMICHI_12X12_LOGIC_AUDIT_V212.json',
 'NEKOMICHI_LARGE_BOARD_BENCHMARK_V207.json',
 'NEKOMICHI_STAGE_GENERATOR_FOUNDATION_BEFORE_V204.txt',
 'NEKOMICHI_DIFFICULTY_CALIBRATION_V115.txt',
 'NEKOMICHI_LOGIC_ENGINE_V118.txt',
 'NEKOMICHI_PRODUCTION_LOGIC_V120.txt',
 'NEKOMICHI_CONTRADICTION_RULE_V122.txt'
]
MAX_FILE=5_000_000

def git(*args):
 try:
  p=subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace',timeout=20)
  return (p.stdout+p.stderr).strip() or '(no output)'
 except Exception as e:return f'(git unavailable: {e})'

def main():
 lines=['NEKOMICHI EVALUATOR CORE AUDIT BEFORE V224',f'Collected: {datetime.now().isoformat(timespec="seconds")}',f'Root: {ROOT}','','=== GIT STATUS ===',git('status','--short','--branch'),'']
 included=[]; missing=[]
 for name in FILES:
  p=ROOT/name
  if not p.is_file():missing.append(name);continue
  size=p.stat().st_size
  if size>MAX_FILE:
   lines += ['='*80,f'FILE: {name}',f'[SKIPPED: {size} bytes exceeds limit]']
   continue
  text=p.read_text(encoding='utf-8',errors='replace')
  lines += ['='*80,f'FILE: {name}',f'SIZE: {size} bytes','='*80,text,'']
  included.append(name)
 lines += ['=== SUMMARY ===',f'Included: {len(included)}',*included,f'Missing: {len(missing)}',*missing]
 OUTPUT.write_text('\n'.join(lines),encoding='utf-8')
 print(f'SUCCESS: {OUTPUT.name}')
 print(f'Included files: {len(included)}')
 print(f'Missing files: {len(missing)}')
 return 0
if __name__=='__main__':raise SystemExit(main())
