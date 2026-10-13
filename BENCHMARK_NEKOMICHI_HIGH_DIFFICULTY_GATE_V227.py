from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'NEKOMICHI_HIGH_DIFFICULTY_GATE_BENCHMARK_V227.txt'
SCRIPTS=[
 'BENCHMARK_NEKOMICHI_LARGE_BOARD_GENERATOR_V207.py',
 'BENCHMARK_NEKOMICHI_12X12_GENERATOR_V208.py',
 'BENCHMARK_NEKOMICHI_12X12_UNIQUENESS_V209.py',
 'AUDIT_NEKOMICHI_12X12_LOGIC_V212.py'
]

def run(cmd,timeout=90):
 try:
  p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace',timeout=timeout)
  return p.returncode,(p.stdout+p.stderr).strip()
 except subprocess.TimeoutExpired as exc:
  text=((exc.stdout or '')+(exc.stderr or '')) if isinstance(exc.stdout,str) else ''
  return 124,(text+'\n[TIMEOUT]').strip()

def main():
 lines=['NEKOMICHI HIGH DIFFICULTY GATE BENCHMARK V227','']
 required=['logic-engine.js','stage-generator.js']
 for name in required:
  if not (ROOT/name).is_file():
   print(f'ERROR: {name} not found');return 1
 code,out=run(['node','--check','logic-engine.js']);lines += ['=== logic-engine syntax ===',out or f'exit {code}','']
 if code:return code
 code,out=run(['node','--check','stage-generator.js']);lines += ['=== stage-generator syntax ===',out or f'exit {code}','']
 if code:return code
 test=ROOT/'tests/foundation/v226-generator-high-difficulty-gate-check.js'
 if test.is_file():
  code,out=run(['node',str(test.relative_to(ROOT))]);lines += ['=== V226 gate regression ===',out,'']
  if code:return code
 found=0
 for name in SCRIPTS:
  path=ROOT/name
  lines += ['='*80,f'SCRIPT: {name}']
  if not path.is_file():lines += ['[MISSING]',''];continue
  found+=1
  lines += [path.read_text(encoding='utf-8',errors='replace'),'']
 # Search generated benchmark JSON/TXT for current large-board measurements.
 lines += ['='*80,'EXISTING LARGE-BOARD RESULTS']
 for path in sorted(ROOT.glob('NEKOMICHI_*')):
  low=path.name.lower()
  if path.is_file() and path.suffix.lower() in ('.json','.txt') and any(k in low for k in ('12x12','large_board','large-board')) and path.stat().st_size<=2_000_000:
   lines += [f'FILE: {path.name}',path.read_text(encoding='utf-8',errors='replace'),'']
 lines += ['=== SUMMARY ===',f'Benchmark scripts found: {found}','SUCCESS: V227 benchmark source collection completed']
 OUT.write_text('\n'.join(lines),encoding='utf-8')
 print(f'Benchmark scripts found: {found}')
 print(f'WROTE: {OUT.name}')
 print('SUCCESS: V227 benchmark source collection completed')
 return 0
if __name__=='__main__':raise SystemExit(main())
