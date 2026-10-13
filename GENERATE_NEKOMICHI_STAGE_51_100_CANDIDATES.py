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

SOURCE = Path('NEKOMICHI_STAGE_51_60_CANDIDATES.json')
OUTPUT = Path('NEKOMICHI_STAGE_51_100_CANDIDATES.json')
if not SOURCE.is_file():
    raise SystemExit('ERROR: place NEKOMICHI_STAGE_51_60_CANDIDATES.json in the project root')
base = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
stages = list(base.get('stages', []))
if [s.get('stage') for s in stages] != list(range(51, 61)):
    raise SystemExit('ERROR: source JSON must contain Stage 51-60 in order')

size_plan = {
    61:8,62:8,63:8,64:8,65:9,66:8,67:9,68:9,69:9,70:9,
    71:9,72:9,73:9,74:8,75:9,76:9,77:9,78:8,79:9,80:9,
    81:9,82:9,83:10,84:9,85:10,86:9,87:10,88:10,89:9,90:10,
    91:10,92:10,93:10,94:10,95:10,96:10,97:10,98:10,99:10,100:10,
}
star_plan = {n:(4 if n==100 else 3 if n>=90 or n in (75,76,79,80,88) else 2) for n in range(61,101)}
by_size={8:[],9:[],10:[]}
needed={n:list(size_plan.values()).count(n) for n in (8,9,10)}
for size in (8,9,10):
    print(f'GENERATE: {needed[size]} candidates for {size}x{size}', flush=True)
    by_size[size]=gen(size,needed[size],610100+size)
    if len(by_size[size])!=needed[size]:
        raise SystemExit(f'ERROR: generated {len(by_size[size])}/{needed[size]} candidates for {size}x{size}')

indexes={8:0,9:0,10:0}
for stage_no in range(61,101):
    size=size_plan[stage_no]
    soln,regions,steps=by_size[size][indexes[size]]; indexes[size]+=1
    stars=star_plan[stage_no]
    stages.append({
        'stage':stage_no,'size':size,'name':f'ステージ{stage_no}',
        'difficulty':'EASY' if stars==2 else 'NORMAL' if stars==3 else 'HARD',
        'logicLevel':2,'regions':regions,'solution':soln,
        'tutorial':False,'bonus':False,'hard':stars>=4,
        'specialType':'boss' if stage_no==100 else 'normal',
        'chapter':'chapter-2','sourcePuzzleStage':'generated-stage-61-100-v1',
        'quality':{
            'uniqueSolution':True,'solutionCount':1,'logicOnly':True,
            'highestRuleLevel':2,'difficultyStars':stars,
            'logicalStepCount':steps,'assumptionRequired':False,
            'initialCats':0,
            'boardGrowthPlan':f'{size}x{size}-gradual-introduction',
            'generationSingletonSeeds':'3-to-5-for-gentle-entry',
        }
    })

out={
 'title':'NEKOMICHI STAGE 51-100 CANDIDATES',
 'seedFamily':'510060 + 610100-size',
 'policy':{
   'stageRange':[51,100],
   'difficulty':'mostly 2-3 stars; Stage 100 up to 4 stars',
   'maxLogicLevel':2,'assumptionForbidden':True,'contradictionForbidden':True,
   'sizeProgression':'8x8 -> 9x9 -> 10x10',
   'stage100':'10x10, 4-star metadata ceiling, no assumption or contradiction',
 },
 'sizePlan':{str(k):v for k,v in size_plan.items()},
 'stages':stages,
}
OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
counts={n:sum(1 for s in stages if s['size']==n) for n in (8,9,10)}
print('OK: Stage 51-100 candidate generation completed.')
print('OK: 50 stages are present with unique solution and logic-only generation checks.')
print('SIZES: '+', '.join(f'{k}x{k}={v}' for k,v in counts.items()))
print('OUTPUT: '+OUTPUT.name)
print('NEXT: run the full Stage 51-100 independent audit after uploading the combined JSON.')
