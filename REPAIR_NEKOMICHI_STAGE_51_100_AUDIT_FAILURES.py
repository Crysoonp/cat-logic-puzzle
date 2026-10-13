from pathlib import Path
import json, random, hashlib, sys

SRC=Path('NEKOMICHI_STAGE_51_100_CANDIDATES.json')
OUT=Path('NEKOMICHI_STAGE_51_100_CANDIDATES_REVISED.json')
AUDIT=Path('NEKOMICHI_STAGE_51_100_REVISED_AUDIT.json')
TARGETS=[52,53,55,59]

def count_solutions(regions,n,limit=2):
 total=0
 def rec(r,uc,ug,prev):
  nonlocal total
  if total>=limit:return
  if r==n:total+=1;return
  for c in range(n):
   g=regions[r][c]
   if c in uc or g in ug or (prev is not None and abs(c-prev)<=1):continue
   rec(r+1,uc|{c},ug|{g},c)
 rec(0,set(),set(),None);return total

def logic(regions,n):
 poss={(r,c) for r in range(n) for c in range(n)};cats=set();direct=locked=0
 while len(cats)<n:
  units=[]
  for r in range(n):units.append(('r',r,{x for x in poss if x[0]==r}))
  for c in range(n):units.append(('c',c,{x for x in poss if x[1]==c}))
  for g in range(n):units.append(('g',g,{x for x in poss if regions[x[0]][x[1]]==g}))
  hit=None
  for typ,k,s in units:
   done=(typ=='r' and any(r==k for r,c in cats))or(typ=='c' and any(c==k for r,c in cats))or(typ=='g' and any(regions[r][c]==k for r,c in cats))
   if not done and len(s)==1:hit=next(iter(s));break
  if hit:
   r,c=hit;cats.add(hit);poss.discard(hit)
   poss={x for x in poss if x[0]!=r and x[1]!=c and regions[x[0]][x[1]]!=regions[r][c] and not(abs(x[0]-r)<=1 and abs(x[1]-c)<=1)}
   direct+=1;continue
  changed=False
  for typ,k,s in units:
   if len(s)<2:continue
   rows={r for r,c in s};cols={c for r,c in s};rem=set()
   if typ=='g' and len(rows)==1:
    rr=next(iter(rows));rem={x for x in poss if x[0]==rr and x not in s}
   elif typ=='g' and len(cols)==1:
    cc=next(iter(cols));rem={x for x in poss if x[1]==cc and x not in s}
   elif typ in ('r','c'):
    gs={regions[r][c] for r,c in s}
    if len(gs)==1:
     g=next(iter(gs));rem={x for x in poss if regions[x[0]][x[1]]==g and x not in s}
   if rem:poss-=rem;locked+=1;changed=True;break
  if not changed:return False,direct,locked
 return True,direct,locked

def connected(regions,n):
 for g in range(n):
  cells={(r,c) for r in range(n) for c in range(n) if regions[r][c]==g}
  if not cells:return False
  seen={next(iter(cells))};stack=list(seen)
  while stack:
   r,c=stack.pop()
   for q in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
    if q in cells and q not in seen:seen.add(q);stack.append(q)
  if seen!=cells:return False
 return True

def make_candidate(rng,n=8):
 while True:
  solution=list(range(n));rng.shuffle(solution)
  if not all(abs(solution[i]-solution[i-1])>1 for i in range(1,n)):continue
  regions=[[-1]*n for _ in range(n)]
  locks=set(rng.sample(range(n),rng.choice([3,4,5])))
  for i,c in enumerate(solution):regions[i][c]=i
  changed=True
  while changed:
   changed=False;cells=[(r,c) for r in range(n) for c in range(n) if regions[r][c]>=0 and regions[r][c] not in locks];rng.shuffle(cells)
   for r,c in cells:
    empty=[q for q in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=q[0]<n and 0<=q[1]<n and regions[q[0]][q[1]]<0]
    if empty:
     rr,cc=rng.choice(empty);regions[rr][cc]=regions[r][c];changed=True
  while any(-1 in row for row in regions):
   progress=False
   for r in range(n):
    for c in range(n):
     if regions[r][c]>=0:continue
     vals=[regions[rr][cc] for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<n and 0<=cc<n and regions[rr][cc]>=0]
     vals=[v for v in vals if v not in locks] or vals
     if vals:regions[r][c]=rng.choice(vals);progress=True
   if not progress:raise RuntimeError('region growth stalled')
  if not connected(regions,n) or count_solutions(regions,n)!=1:continue
  solved,direct,locked=logic(regions,n)
  singleton=sum(1 for g in range(n) if sum(v==g for row in regions for v in row)==1)
  if solved and singleton<=5:return solution,regions,direct,locked,singleton

try:
 if not SRC.is_file():raise RuntimeError('place '+SRC.name+' in the project root')
 data=json.loads(SRC.read_text(encoding='utf-8-sig'));stages=data.get('stages',[])
 if [s.get('stage') for s in stages]!=list(range(51,101)):raise RuntimeError('source must contain Stage 51-100 in order')
 rng=random.Random(5210059);replacements={}
 for no in TARGETS:
  solution,regions,direct,locked,singleton=make_candidate(rng)
  old=next(s for s in stages if s['stage']==no)
  old.update({'size':8,'regions':regions,'solution':solution,'difficulty':'EASY','logicLevel':2,'sourcePuzzleStage':'regenerated-after-independent-audit-v1'})
  old['quality'].update({'uniqueSolution':True,'solutionCount':1,'logicOnly':True,'highestRuleLevel':2,'difficultyStars':2,'logicalStepCount':direct+locked,'assumptionRequired':False,'initialCats':0,'independentAuditRepair':True})
  replacements[str(no)]={'direct':direct,'locked':locked,'singletonRegions':singleton}
 data['repair']={'reason':'Independent level-2 solver stalled','replacedStages':TARGETS,'details':replacements}
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 reports=[];failures=[];fps={}
 for s in stages:
  no=s['stage'];n=s['size'];regions=s['regions'];solution=s['solution'];errors=[]
  if not connected(regions,n):errors.append('disconnected region')
  solutions=count_solutions(regions,n)
  if solutions!=1:errors.append('solution count '+str(solutions))
  solved,direct,locked=logic(regions,n)
  if not solved:errors.append('level-2 logic stalled')
  if sorted(solution)!=list(range(n)) or any(abs(solution[i]-solution[i-1])<=1 for i in range(1,n)):errors.append('invalid solution permutation')
  if sorted(regions[r][solution[r]] for r in range(n))!=list(range(n)):errors.append('solution region mismatch')
  fp=hashlib.sha256(json.dumps({'n':n,'r':regions,'s':solution},sort_keys=True).encode()).hexdigest()
  if fp in fps:errors.append('duplicate of '+str(fps[fp]))
  else:fps[fp]=no
  if errors:failures.append(no)
  reports.append({'stage':no,'size':n,'solutionCount':solutions,'logicSolved':solved,'direct':direct,'locked':locked,'errors':errors})
 result={'title':'NEKOMICHI STAGE 51-100 REVISED AUDIT','summary':{'passed':not failures,'failureStages':failures,'replacedStages':TARGETS},'stages':reports}
 AUDIT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('OK: Stage 52, 53, 55 and 59 were regenerated after the independent audit.')
 print('OK: revised Stage 51-100 full audit completed.')
 print('PASS: '+str(not failures))
 print('FAILURES: '+(','.join(map(str,failures)) if failures else 'none'))
 print('OUTPUT: '+OUT.name)
 print('AUDIT: '+AUDIT.name)
 print('SEND: Upload only '+OUT.name+' and '+AUDIT.name+' to Copilot.')
except Exception as e:
 print('ERROR: '+str(e));sys.exit(1)
