import random,itertools,time
N=8

def gen_solution(rng):
 for _ in range(10000):
  p=list(range(N));rng.shuffle(p)
  if all(abs(p[i]-p[i-1])>1 for i in range(1,N)): return p

def regions_voronoi(sol,rng):
 weights=[rng.uniform(-1.5,1.5) for _ in range(N)]
 reg=[]
 for r in range(N):
  row=[]
  for c in range(N):
   scores=[]
   for i,sc in enumerate(sol):
    d=abs(r-i)+abs(c-sc)+weights[i]+rng.uniform(-.18,.18)
    scores.append(d)
   row.append(min(range(N),key=lambda i:scores[i]))
  reg.append(row)
 for i,c in enumerate(sol): reg[i][c]=i
 return reg

def connected(reg):
 for k in range(N):
  cells={(r,c) for r in range(N) for c in range(N) if reg[r][c]==k}
  if not cells:return False
  seen={next(iter(cells))}; st=list(seen)
  while st:
   r,c=st.pop()
   for q in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
    if q in cells and q not in seen:seen.add(q);st.append(q)
  if seen!=cells:return False
 return True

def count(reg,limit=2):
 regs=[set() for _ in range(N)]
 for r in range(N):
  for c in range(N):regs[reg[r][c]].add((r,c))
 count=0
 def rec(r,usedc,usedg,prev):
  nonlocal count
  if count>=limit:return
  if r==N:count+=1;return
  for c in range(N):
   g=reg[r][c]
   if c in usedc or g in usedg or (prev is not None and abs(c-prev)<=1): continue
   rec(r+1,usedc|{c},usedg|{g},c)
 rec(0,set(),set(),None)
 return count

def logical(reg):
 poss={(r,c) for r in range(N) for c in range(N)}; cats=set(); steps=[]
 def eliminate_cat(r,c):
  nonlocal poss
  rem=set()
  for rr,cc in poss:
   if (rr,cc)==(r,c):continue
   if rr==r or cc==c or reg[rr][cc]==reg[r][c] or (abs(rr-r)<=1 and abs(cc-c)<=1): rem.add((rr,cc))
  poss-=rem; cats.add((r,c));poss.discard((r,c));steps.append(('cat',r,c,len(rem)))
 while len(cats)<N:
  changed=False
  units=[]
  for r in range(N): units.append(('r',r,{x for x in poss if x[0]==r}))
  for c in range(N): units.append(('c',c,{x for x in poss if x[1]==c}))
  for g in range(N): units.append(('g',g,{x for x in poss if reg[x[0]][x[1]]==g}))
  for typ,k,s in units:
   if ((typ=='r' and any(r==k for r,c in cats)) or (typ=='c' and any(c==k for r,c in cats)) or (typ=='g' and any(reg[r][c]==k for r,c in cats))): continue
   if len(s)==1:
    eliminate_cat(*next(iter(s)));changed=True;break
  if changed:continue
  # locked candidates
  for typ,k,s in units:
   if len(s)<2:continue
   rows={r for r,c in s}; cols={c for r,c in s}
   rem=set()
   if typ=='g' and len(rows)==1:
    rr=next(iter(rows));rem={x for x in poss if x[0]==rr and x not in s}
   elif typ=='g' and len(cols)==1:
    cc=next(iter(cols));rem={x for x in poss if x[1]==cc and x not in s}
   elif typ in 'rc':
    gs={reg[r][c] for r,c in s}
    if len(gs)==1:
     g=next(iter(gs));rem={x for x in poss if reg[x[0]][x[1]]==g and x not in s}
   if rem:
    poss-=rem;steps.append(('x',len(rem)));changed=True;break
  if changed:continue
  # common adjacency for a unit
  for typ,k,s in units:
   if len(s)<2 or len(s)>4:continue
   common=None
   for r,c in s:
    adj={(rr,cc) for rr,cc in poss if (rr,cc) not in s and abs(rr-r)<=1 and abs(cc-c)<=1}
    common=adj if common is None else common&adj
   if common:
    poss-=common;steps.append(('x',len(common)));changed=True;break
  if not changed:return False,len(steps)
 return True,len(steps)

rng=random.Random(510060)
found=[]; start=time.time()
for k in range(200000):
 sol=gen_solution(rng);reg=regions_voronoi(sol,rng)
 if not connected(reg):continue
 if count(reg)!=1:continue
 ok,st=logical(reg)
 if not ok:continue
 found.append((sol,reg,st));print('found',len(found),k,st,time.time()-start)
 if len(found)>=10:break
print('total',len(found))

if len(found) < 10:
    raise SystemExit('ERROR: could not generate 10 approved candidates')
import json
stages=[]
for offset,(sol,reg,steps) in enumerate(found):
    stage_no=51+offset
    stages.append({
        'stage':stage_no,'size':8,'name':f'ステージ{stage_no}',
        'difficulty':'EASY','logicLevel':2,'regions':reg,'solution':sol,
        'tutorial':False,'bonus':False,'hard':False,'specialType':'normal',
        'chapter':'chapter-2','sourcePuzzleStage':'generated-stage-51-60-v1',
        'quality':{'uniqueSolution':True,'solutionCount':1,'logicOnly':True,
                   'highestRuleLevel':2,'difficultyStars':2,
                   'logicalStepCount':steps,'assumptionRequired':False,
                   'initialCats':0,'boardGrowthPlan':'8x8-stability'}
    })
out={'title':'NEKOMICHI STAGE 51-60 CANDIDATES','seed':510060,
     'policy':{'sizes':[8]*10,'stars':[2]*10,'maxLogicLevel':2,
               'assumptionForbidden':True,'contradictionForbidden':True,
               'purpose':'Keep difficulty gentle while stabilizing 8x8 play before 9x9 introduction.'},
     'stages':stages}
Path=__import__('pathlib').Path
Path('NEKOMICHI_STAGE_51_60_CANDIDATES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('OK: 10 Stage 51-60 candidates generated.')
print('OK: all candidates are 8x8, unique, logic-only, and capped at rule level 2.')
print('OUTPUT: NEKOMICHI_STAGE_51_60_CANDIDATES.json')
print('SEND: Upload only NEKOMICHI_STAGE_51_60_CANDIDATES.json to Copilot.')
