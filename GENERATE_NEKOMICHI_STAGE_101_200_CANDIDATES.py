import random,time

def gen(N,count_needed,seed):
 rng=random.Random(seed);found=[]
 def sol():
  while 1:
   p=list(range(N));rng.shuffle(p)
   if all(abs(p[i]-p[i-1])>1 for i in range(1,N)):return p
 def regions(p):
  reg=[[-1]*N for _ in range(N)];front=[]
  locks=set(rng.sample(range(N),rng.choice([3,4,5])))
  for i,c in enumerate(p):reg[i][c]=i
  changed=True
  while changed:
   changed=False
   cells=[(r,c) for r in range(N) for c in range(N) if reg[r][c]>=0 and reg[r][c] not in locks]
   rng.shuffle(cells)
   for r,c in cells:
    ns=[(rr,cc) for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<N and 0<=cc<N and reg[rr][cc]<0]
    if ns:
     rr,cc=rng.choice(ns);reg[rr][cc]=reg[r][c];changed=True
  # assign leftovers adjacent iteratively, allowing locked only if otherwise impossible
  while any(-1 in row for row in reg):
   progress=False
   for r in range(N):
    for c in range(N):
     if reg[r][c]>=0:continue
     vals=[reg[rr][cc] for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<N and 0<=cc<N and reg[rr][cc]>=0]
     vals=[v for v in vals if v not in locks] or vals
     if vals:reg[r][c]=rng.choice(vals);progress=True
   if not progress:break
  return reg
 def count(reg,lim=2):
  n=0
  def rec(r,uc,ug,prev):
   nonlocal n
   if n>=lim:return
   if r==N:n+=1;return
   for c in range(N):
    g=reg[r][c]
    if c in uc or g in ug or (prev is not None and abs(c-prev)<=1):continue
    rec(r+1,uc|{c},ug|{g},c)
  rec(0,set(),set(),None);return n
 def logical(reg):
  poss={(r,c) for r in range(N) for c in range(N)};cats=set();steps=0
  while len(cats)<N:
   units=[]
   for r in range(N):units.append(('r',r,{x for x in poss if x[0]==r}))
   for c in range(N):units.append(('c',c,{x for x in poss if x[1]==c}))
   for g in range(N):units.append(('g',g,{x for x in poss if reg[x[0]][x[1]]==g}))
   hit=None
   for typ,k,s in units:
    done=(typ=='r' and any(r==k for r,c in cats))or(typ=='c' and any(c==k for r,c in cats))or(typ=='g' and any(reg[r][c]==k for r,c in cats))
    if not done and len(s)==1:hit=next(iter(s));break
   if hit:
    r,c=hit;cats.add(hit);poss.discard(hit);poss={x for x in poss if x[0]!=r and x[1]!=c and reg[x[0]][x[1]]!=reg[r][c] and not(abs(x[0]-r)<=1 and abs(x[1]-c)<=1)};steps+=1;continue
   changed=False
   for typ,k,s in units:
    if len(s)<2:continue
    rows={r for r,c in s};cols={c for r,c in s};rem=set()
    if typ=='g' and len(rows)==1:rr=next(iter(rows));rem={x for x in poss if x[0]==rr and x not in s}
    elif typ=='g' and len(cols)==1:cc=next(iter(cols));rem={x for x in poss if x[1]==cc and x not in s}
    elif typ in ('r','c'):
     gs={reg[r][c] for r,c in s}
     if len(gs)==1:g=next(iter(gs));rem={x for x in poss if reg[x[0]][x[1]]==g and x not in s}
    if rem:poss-=rem;steps+=1;changed=True;break
   if not changed:return False,steps
  return True,steps
 start=time.time()
 for i in range(100000):
  p=sol();r=regions(p)
  if count(r)!=1:continue
  ok,st=logical(r)
  if ok:found.append((p,r,st));print(N,len(found),i,st,time.time()-start,flush=True)
  if len(found)>=count_needed:return found
 return found

import json
from pathlib import Path

SOURCE = Path('NEKOMICHI_STAGE_51_100_CANDIDATES_REVISED.json')
OUTPUT = Path('NEKOMICHI_STAGE_101_200_CANDIDATES.json')
if not SOURCE.is_file():
    raise SystemExit('ERROR: place NEKOMICHI_STAGE_51_100_CANDIDATES_REVISED.json in the project root')
base = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
if [s.get('stage') for s in base.get('stages', [])] != list(range(51, 101)):
    raise SystemExit('ERROR: source JSON must contain Stage 51-100 in order')

print('GENERATE: 100 candidates for Stage 101-200 (10x10)', flush=True)
items = gen(10, 100, 10120010)
if len(items) != 100:
    raise SystemExit(f'ERROR: generated {len(items)}/100 candidates')

stages=[]
for index,(solution,regions,steps) in enumerate(items, start=101):
    stars = 4 if index in (150,200) else 3 if index >= 121 or index % 10 == 0 else 2
    stages.append({
        'stage':index,'size':10,'name':f'ステージ{index}',
        'difficulty':'HARD' if stars==4 else 'NORMAL' if stars==3 else 'EASY',
        'logicLevel':2,'regions':regions,'solution':solution,
        'tutorial':False,'bonus':False,'hard':stars>=4,
        'specialType':'boss' if index in (150,200) else 'normal',
        'chapter':'chapter-2','sourcePuzzleStage':'generated-stage-101-200-v1',
        'quality':{
            'uniqueSolution':True,'solutionCount':1,'logicOnly':True,
            'highestRuleLevel':2,'difficultyStars':stars,
            'logicalStepCount':steps,'assumptionRequired':False,
            'initialCats':0,'boardGrowthPlan':'10x10-consolidation',
            'generationSingletonSeeds':'3-to-5-for-gentle-entry'
        }
    })

out={
    'title':'NEKOMICHI STAGE 101-200 CANDIDATES',
    'seedFamily':'10120010',
    'policy':{
        'stageRange':[101,200],
        'boardSize':'10x10 fixed to consolidate the larger-board experience',
        'difficulty':'2-3 stars, milestone stages up to 4 stars',
        'maxLogicLevel':2,'assumptionForbidden':True,'contradictionForbidden':True,
        'milestones':[150,200]
    },
    'stages':stages
}
OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('OK: 100 Stage 101-200 candidates generated.')
print('OK: all candidates are 10x10, unique, logic-only, and capped at rule level 2.')
print('OUTPUT: '+OUTPUT.name)
print('SEND: Upload only '+OUTPUT.name+' to Copilot for the independent full audit.')
