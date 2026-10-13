from pathlib import Path
from collections import Counter, deque
import hashlib, json, random, sys, time

ROOT=Path(__file__).resolve().parent
REPORT=ROOT/'NEKOMICHI_TARGET_STRUCTURE_BENCHMARK_V228.json'
CANDIDATES=ROOT/'NEKOMICHI_TARGET_STRUCTURE_CANDIDATES_V228.json'
SUMMARY=ROOT/'NEKOMICHI_TARGET_STRUCTURE_BENCHMARK_V228.txt'
SIZES=(11,12)
SECONDS_PER_SIZE=20.0
GLOBAL_SECONDS=45.0
PROGRESS_SECONDS=5.0
SEED=22820261014
PROFILES=((0,2),(1,2),(0,1),(1,1))

def neighbors4(r,c,n):
 for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
  if 0<=rr<n and 0<=cc<n:yield rr,cc

def make_solution(n,rng):
 for _ in range(10000):
  cols=list(range(n));rng.shuffle(cols)
  if all(abs(cols[r]-cols[r-1])>1 for r in range(1,n)):return cols
 return None

def anchors(solution,single_count,double_count,rng):
 ids=list(range(len(solution)));rng.shuffle(ids);chosen=[]
 for rid in ids:
  r,c=rid,solution[rid]
  if all(abs(r-pr)>1 or abs(c-pc)>1 for pr,pc,_ in chosen):chosen.append((r,c,rid))
  if len(chosen)>=single_count+double_count:break
 if len(chosen)<single_count+double_count:chosen=[(i,solution[i],i) for i in ids[:single_count+double_count]]
 return ({x[2] for x in chosen[:single_count]},{x[2] for x in chosen[single_count:single_count+double_count]})

def build_board(solution,profile,rng):
 n=len(solution);board=[[-1]*n for _ in range(n)];cells=[set() for _ in range(n)]
 single_count,double_count=PROFILES[profile];singles,doubles=anchors(solution,single_count,double_count,rng);protected=singles|doubles
 for r,c in enumerate(solution):board[r][c]=r;cells[r].add((r,c))
 occupied={(r,solution[r]) for r in range(n)}
 for rid in doubles:
  seed=(rid,solution[rid]);options=[p for p in neighbors4(*seed,n) if p not in occupied];rng.shuffle(options)
  if not options:return None
  p=options[0];board[p[0]][p[1]]=rid;cells[rid].add(p);occupied.add(p)
 active=[i for i in range(n) if i not in protected]
 remaining=n*n-len(occupied);soft_cap=(n*n-single_count-2*double_count+len(active)-1)//max(1,len(active))+6
 while remaining:
  choices=[]
  for rid in active:
   frontier=set()
   for r,c in cells[rid]:frontier.update(p for p in neighbors4(r,c,n) if board[p[0]][p[1]]==-1)
   if frontier:choices.append((max(0,len(cells[rid])-soft_cap),len(cells[rid]),rid,list(frontier)))
  if not choices:return None
  choices.sort(key=lambda x:(x[0],x[1]));_,_,rid,frontier=rng.choice(choices[:min(5,len(choices))]);p=rng.choice(frontier)
  board[p[0]][p[1]]=rid;cells[rid].add(p);remaining-=1
 return board

def connected(board):
 n=len(board)
 for rid in range(n):
  target={(r,c) for r in range(n) for c in range(n) if board[r][c]==rid}
  if not target:return False
  start=next(iter(target));seen={start};q=deque([start])
  while q:
   r,c=q.popleft()
   for p in neighbors4(r,c,n):
    if p in target and p not in seen:seen.add(p);q.append(p)
  if seen!=target:return False
 return True

def stats(board):
 n=len(board);counts=Counter(v for row in board for v in row);sizes=[counts[i] for i in range(n)]
 return {'sizes':sizes,'minimum':min(sizes),'maximum':max(sizes),'singletons':sum(v==1 for v in sizes),'twoCells':sum(v==2 for v in sizes)}

def count_solutions(board,limit=2,node_limit=300000):
 n=len(board);rows=[None]*n;used_c=set();used_g=set();total=0;first=None;nodes=0;aborted=False
 def dfs(r):
  nonlocal total,first,nodes,aborted
  if total>=limit or aborted:return
  nodes+=1
  if nodes>node_limit:aborted=True;return
  if r==n:
   total+=1
   if first is None:first=rows[:]
   return
  options=[]
  for c in range(n):
   g=board[r][c]
   if c in used_c or g in used_g:continue
   if r and rows[r-1] is not None and abs(rows[r-1]-c)<=1:continue
   options.append(c)
  options.sort(key=lambda c:sum(1 for rr in range(r+1,n) if board[rr][c]==board[r][c]))
  for c in options:
   g=board[r][c];rows[r]=c;used_c.add(c);used_g.add(g);dfs(r+1);used_g.remove(g);used_c.remove(c);rows[r]=None
   if total>=limit or aborted:return
 dfs(0);return total,first,nodes,aborted

def canonical(board):
 n=len(board);variants=[];cur=board
 for _ in range(4):
  variants += [cur,[list(reversed(row)) for row in cur]]
  cur=[[cur[n-1-c][r] for c in range(n)] for r in range(n)]
 sigs=[]
 for grid in variants:
  remap={};nxt=0;norm=[]
  for row in grid:
   out=[]
   for v in row:
    if v not in remap:remap[v]=nxt;nxt+=1
    out.append(remap[v])
   norm.append(out)
  sigs.append(json.dumps(norm,separators=(',',':')))
 return hashlib.sha256(min(sigs).encode()).hexdigest()

def run_size(n,global_deadline):
 rng=random.Random(SEED+n*1009);started=time.perf_counter();deadline=min(started+SECONDS_PER_SIZE,global_deadline);next_progress=started+PROGRESS_SECONDS
 attempts=connected_count=structural_count=unique_checks=solver_aborts=0;candidate=None;best=None
 print(f'START: {n}x{n}, limit {deadline-started:.0f}s',flush=True)
 while time.perf_counter()<deadline:
  attempts+=1;solution=make_solution(n,rng)
  if solution is None:continue
  profile=(attempts-1)%len(PROFILES);board=build_board(solution,profile,rng)
  if board is None or not connected(board):continue
  connected_count+=1;area=stats(board)
  rank=(area['singletons']+area['twoCells'],area['maximum'])
  if best is None or rank<best['rank']:best={'rank':rank,'areaStats':area,'profile':profile}
  if area['singletons']>1 or area['twoCells']>2:continue
  structural_count+=1;unique_checks+=1;total,found,nodes,aborted=count_solutions(board)
  if aborted:solver_aborts+=1;continue
  if total==1:
   candidate={'size':n,'solution':found,'regions':board,'areaStats':area,'canonicalKey':canonical(board),'attempt':attempts,'profile':profile,'profileDefinition':PROFILES[profile],'qualityTier':'V225_STRUCTURE_PASSED_LOGIC_NOT_YET_AUDITED'};break
  now=time.perf_counter()
  if now>=next_progress:
   print(f'PROGRESS: {n}x{n} elapsed={now-started:.1f}s attempts={attempts} structural={structural_count} uniqueChecks={unique_checks} aborts={solver_aborts}',flush=True);next_progress=now+PROGRESS_SECONDS
 elapsed=time.perf_counter()-started;status='FOUND' if candidate else 'TIMEOUT'
 print(f'{status}: {n}x{n} elapsed={elapsed:.2f}s attempts={attempts} structural={structural_count} uniqueChecks={unique_checks}',flush=True)
 return {'size':n,'status':status,'elapsedSeconds':round(elapsed,3),'attempts':attempts,'connectedCandidates':connected_count,'structuralCandidates':structural_count,'uniqueChecks':unique_checks,'solverAborts':solver_aborts,'bestObserved':best,'candidate':candidate}

def main():
 if not (ROOT/'.git').exists():raise RuntimeError('Run from cat-logic-puzzle project root.')
 started=time.perf_counter();deadline=started+GLOBAL_SECONDS;results=[]
 for n in SIZES:
  if time.perf_counter()>=deadline:break
  results.append(run_size(n,deadline))
 candidates=[r['candidate'] for r in results if r.get('candidate')]
 report={'benchmarkVersion':'V228','purpose':'Measure 11x11/12x12 construction under V225 target structure.','profiles':[list(x) for x in PROFILES],'limits':{'singletonsMax':1,'twoCellsMax':2,'perSizeSeconds':SECONDS_PER_SIZE,'globalSeconds':GLOBAL_SECONDS,'solutionNodeLimit':300000},'totalElapsedSeconds':round(time.perf_counter()-started,3),'foundCount':len(candidates),'results':results,'decision':'READY_FOR_V226_LOGIC_GATE_AUDIT' if candidates else 'TARGET_STRUCTURE_UNIQUENESS_NEEDS_NEW_CONSTRUCTION','gameFilesModified':False,'notIntegrated':True}
 payload={'title':'NEKOMICHI TARGET STRUCTURE CANDIDATES V228','candidateOnly':True,'notIntegrated':True,'candidates':candidates}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');CANDIDATES.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['NEKOMICHI TARGET STRUCTURE BENCHMARK V228',f"Decision: {report['decision']}",f'Found: {len(candidates)}/{len(SIZES)}',f"Elapsed: {report['totalElapsedSeconds']}s",'']
 for r in results:lines.append(f"{r['size']}x{r['size']} | {r['status']} | {r['elapsedSeconds']}s | attempts {r['attempts']} | structural {r['structuralCandidates']} | unique checks {r['uniqueChecks']} | solver aborts {r['solverAborts']}")
 SUMMARY.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print('RESULT:',report['decision']);print('WROTE:',SUMMARY.name);print('WROTE:',REPORT.name);print('WROTE:',CANDIDATES.name);print('SUCCESS: V228 target-structure benchmark completed');return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except KeyboardInterrupt:print('CANCELLED: User stopped V228.',flush=True);raise SystemExit(130)
 except Exception as exc:print('ERROR:',exc,flush=True);raise SystemExit(1)
