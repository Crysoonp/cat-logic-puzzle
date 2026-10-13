from pathlib import Path
import json, random, sys, time
from collections import Counter

ROOT=Path.cwd()
OUT=ROOT/'NEKOMICHI_STAGE_201_300_CANDIDATES.json'
AUDIT=ROOT/'NEKOMICHI_STAGE_201_300_GENERATION_AUDIT.json'
SEED=202610130201302
SOURCE_NAMES=[
 'NEKOMICHI_STAGE_101_200_CANDIDATES_REVISED_V156.json',
 'NEKOMICHI_STAGE_101_200_CANDIDATES.json'
]

def fail(m): raise RuntimeError(m)
def load_source():
    for name in SOURCE_NAMES:
        p=ROOT/name
        if p.is_file():
            data=json.loads(p.read_text(encoding='utf-8-sig'))
            stages=data.get('stages') if isinstance(data,dict) else data
            if isinstance(stages,list) and len(stages)>=100:
                return name,stages
    fail('Missing usable Stage 101-200 candidate JSON: '+', '.join(SOURCE_NAMES))
def get(item,*names):
    for n in names:
        if n in item:return item[n]
    return None
def transform_grid(grid,mode):
    n=len(grid)
    if mode==0:return [row[:] for row in grid]
    if mode==1:return [[grid[n-1-c][r] for c in range(n)] for r in range(n)]
    if mode==2:return [[grid[n-1-r][n-1-c] for c in range(n)] for r in range(n)]
    if mode==3:return [[grid[c][n-1-r] for c in range(n)] for r in range(n)]
    if mode==4:return [list(reversed(row)) for row in grid]
    if mode==5:return list(reversed([row[:] for row in grid]))
    if mode==6:return [[grid[c][r] for c in range(n)] for r in range(n)]
    return [[grid[n-1-c][n-1-r] for c in range(n)] for r in range(n)]
def transform_solution(sol,n,mode):
    pts=[(r,c) for r,c in enumerate(sol)]
    def f(r,c):
        return [(r,c),(c,n-1-r),(n-1-r,n-1-c),(n-1-c,r),(r,n-1-c),(n-1-r,c),(c,r),(n-1-c,n-1-r)][mode]
    out=[None]*n
    for r,c in pts:
        rr,cc=f(r,c);out[rr]=cc
    return out
def normalize_regions(grid,rng):
    labels=[]
    for row in grid:
        for v in row:
            if v not in labels:labels.append(v)
    shuffled=list(range(len(labels)));rng.shuffle(shuffled)
    remap={old:new for old,new in zip(labels,shuffled)}
    return [[remap[v] for v in row] for row in grid]
def connected(grid,label):
    n=len(grid); cells={(r,c) for r in range(n) for c in range(n) if grid[r][c]==label}
    if not cells:return False
    todo=[next(iter(cells))];seen={todo[0]}
    while todo:
        r,c=todo.pop()
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(r+dr,c+dc)
            if p in cells and p not in seen:seen.add(p);todo.append(p)
    return seen==cells
def count_solutions(n,regions,limit=2):
    rows=[None]*n;used_c=set();used_g=set();count=0
    def dfs(r):
        nonlocal count
        if count>=limit:return
        if r==n:count+=1;return
        for c in range(n):
            g=regions[r][c]
            if c in used_c or g in used_g:continue
            if r and rows[r-1] is not None and abs(rows[r-1]-c)<=1:continue
            rows[r]=c;used_c.add(c);used_g.add(g);dfs(r+1)
            used_g.remove(g);used_c.remove(c);rows[r]=None
            if count>=limit:return
    dfs(0);return count
def area_stats(regions):
    n=len(regions);vals=sorted(Counter(v for row in regions for v in row).values())
    return {'areas':vals,'min':min(vals),'max':max(vals),'singletons':sum(v==1 for v in vals),'twoCells':sum(v==2 for v in vals),'largeShare':round(max(vals)/(n*n),4)}
def main():
    if not (ROOT/'.git').exists():fail('Run from the cat-logic-puzzle project root')
    source_name,raw=load_source();rng=random.Random(SEED)
    prepared=[]
    for item in raw:
        regions=get(item,'regions','regionMap','areas')
        solution=get(item,'solution','answer','cats')
        if not isinstance(regions,list) or not regions or not isinstance(regions[0],list):continue
        n=len(regions)
        if n<8 or n>12 or any(len(row)!=n for row in regions):continue
        if not isinstance(solution,list) or len(solution)!=n:continue
        if len(set(v for row in regions for v in row))!=n:continue
        if not all(connected(regions,g) for g in set(v for row in regions for v in row)):continue
        if count_solutions(n,regions,2)!=1:continue
        prepared.append(item)
    if len(prepared)<100:fail(f'Only {len(prepared)} valid unique connected source stages; expected 100')
    # Keep all 100 proven boards, but rearrange sizes so progression is not monotonic.
    rng.shuffle(prepared); result=[];seen=set()
    for idx,item in enumerate(prepared[:100]):
        stage=201+idx;n=len(get(item,'regions','regionMap','areas'))
        base=get(item,'regions','regionMap','areas');sol=get(item,'solution','answer','cats')
        modes=list(range(8));rng.shuffle(modes);chosen=None
        for mode in modes:
            reg=normalize_regions(transform_grid(base,mode),rng)
            sig=json.dumps(reg,separators=(',',':'))
            if sig not in seen:
                chosen=(mode,reg,sig);break
        if chosen is None:fail('Could not create distinct transform for Stage '+str(stage))
        mode,reg,sig=chosen;seen.add(sig);newsol=transform_solution(sol,n,mode)
        if count_solutions(n,reg,2)!=1:fail('Transformed stage lost unique solution: '+str(stage))
        olddiff=get(item,'difficulty','stars','level')
        try: diff=int(olddiff)
        except: diff=3
        diff=max(2,min(4,diff))
        if stage in (250,300):diff=4
        result.append({'stage':stage,'size':n,'difficulty':diff,'difficultyTarget':diff,'pattern':'proven_transformed_variety','boss':stage in (250,300),'regions':reg,'solution':newsol,'areaStats':area_stats(reg),'uniqueSolution':True,'sourceStage':get(item,'stage','id','number'),'transformMode':mode})
    payload={'format':'nekomichi-stage-candidates-v3','range':[201,300],'seed':SEED,'candidateOnly':True,'notIntegrated':True,'source':source_name,'method':'validated Stage 101-200 boards transformed by rotation/reflection and reordered','design':{'visibleEasyLabel':False,'sizes':'existing proven 8x8-12x12 mix','oneAndTwoCellRegionsPreservedWhenPresent':True,'stage250And300':'star 4 milestone candidates','star5Included':False,'newRuleIncluded':False},'stages':result}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={'generated':100,'range':[201,300],'source':source_name,'sizes':dict(sorted(Counter(s['size'] for s in result).items())),'difficulty':dict(sorted(Counter(s['difficulty'] for s in result).items())),'uniqueSolutionAll':True,'connectedRegionsAll':True,'duplicateLayouts':0,'containsSingletonRegions':sum(s['areaStats']['singletons']>0 for s in result),'containsTwoCellRegions':sum(s['areaStats']['twoCells']>0 for s in result),'candidateOnly':True,'nextStep':'Run production-logic, similarity and difficulty audit before integration.'}
    AUDIT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OK: Generated 100 Stage 201-300 candidates from validated Stage 101-200 source boards.')
    print('OK: Every transformed candidate has exactly one solution and connected regions.')
    print('OK: Rotation, reflection, region relabeling and stage reordering created a separate candidate set.')
    print('OK: Stage 250 and 300 are star 4 milestone candidates; no star 5 or new rule was added.')
    print('OK: Candidate files only; game files were not modified.')
    print('OUTPUT:',OUT);print('AUDIT:',AUDIT)
    print('SEND: Upload both generated JSON files to Copilot.')
if __name__=='__main__':
    try:main()
    except Exception as e:print('ERROR:',e);sys.exit(1)
