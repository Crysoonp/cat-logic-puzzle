from pathlib import Path
from collections import Counter, deque
import hashlib, json, random, sys, time

ROOT = Path.cwd()
OUTPUT = ROOT / 'NEKOMICHI_STAGE_201_210_PILOT_V204.json'
AUDIT = ROOT / 'NEKOMICHI_STAGE_201_210_PILOT_AUDIT_V204.json'
SIZE_PLAN = {201:8, 202:9, 203:10, 204:11, 205:12, 206:8, 207:10, 208:12, 209:9, 210:11}
STAR_PLAN = {201:2, 202:2, 203:3, 204:3, 205:4, 206:2, 207:3, 208:4, 209:3, 210:4}
MAX_ATTEMPTS = 300000


def canonical(regions):
    n = len(regions)
    variants = []
    current = regions
    for _ in range(4):
        variants.extend((current, [list(reversed(row)) for row in current]))
        current = [[current[n - 1 - c][r] for c in range(n)] for r in range(n)]
    for grid in variants:
        mapping = {}; nxt = 0; normalized = []
        for row in grid:
            out = []
            for value in row:
                if value not in mapping:
                    mapping[value] = nxt; nxt += 1
                out.append(mapping[value])
            normalized.append(out)
        yield json.dumps(normalized, separators=(',', ':'))


def canonical_key(regions):
    return hashlib.sha256(min(canonical(regions)).encode('utf-8')).hexdigest()


def make_solution(n, rng):
    while True:
        columns = list(range(n)); rng.shuffle(columns)
        if all(abs(columns[r] - columns[r - 1]) > 1 for r in range(1, n)):
            return columns


def neighbors(r, c, n):
    for rr, cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0 <= rr < n and 0 <= cc < n:
            yield rr, cc


def make_regions(solution, rng, profile):
    n = len(solution)
    regions = [[-1] * n for _ in range(n)]
    groups = list(range(n)); rng.shuffle(groups)
    single_count, double_count = profile
    caps = {g: 1 for g in groups[:single_count]}
    caps.update({g: 2 for g in groups[single_count:single_count + double_count]})
    sizes = [0] * n
    for row, col in enumerate(solution):
        regions[row][col] = row; sizes[row] = 1
    empty = n*n - n
    while empty:
        frontier = []
        for g in range(n):
            if g in caps and sizes[g] >= caps[g]:
                continue
            cells = [(r,c) for r in range(n) for c in range(n) if regions[r][c] == g]
            options = set()
            for r,c in cells:
                options.update((rr,cc) for rr,cc in neighbors(r,c,n) if regions[rr][cc] < 0)
            if options:
                frontier.append((g, list(options)))
        if not frontier:
            return None
        minimum = min(sizes[g] for g, _ in frontier)
        preferred = [(g, opts) for g, opts in frontier if sizes[g] <= minimum + 2]
        g, options = rng.choice(preferred)
        r,c = rng.choice(options)
        regions[r][c] = g; sizes[g] += 1; empty -= 1
    return regions


def connected(regions):
    n = len(regions)
    for group in range(n):
        cells = {(r,c) for r in range(n) for c in range(n) if regions[r][c] == group}
        if not cells: return False
        seen = {next(iter(cells))}; queue = deque(seen)
        while queue:
            r,c = queue.popleft()
            for point in neighbors(r,c,n):
                if point in cells and point not in seen:
                    seen.add(point); queue.append(point)
        if seen != cells: return False
    return True


def solution_count(regions, limit=2):
    n = len(regions); total = 0; first = None
    def search(row, used_cols, used_groups, previous, columns):
        nonlocal total, first
        if total >= limit: return
        if row == n:
            total += 1
            if first is None: first = columns[:]
            return
        for col in range(n):
            group = regions[row][col]
            if col in used_cols or group in used_groups: continue
            if previous is not None and abs(col - previous) <= 1: continue
            search(row+1, used_cols|{col}, used_groups|{group}, col, columns+[col])
    search(0, set(), set(), None, [])
    return total, first


def logic_solve(regions):
    n = len(regions); possible = {(r,c) for r in range(n) for c in range(n)}
    cats = set(); direct = locked = common = 0
    while len(cats) < n:
        units = []
        for r in range(n): units.append(('row',r,{x for x in possible if x[0] == r}))
        for c in range(n): units.append(('col',c,{x for x in possible if x[1] == c}))
        for g in range(n): units.append(('region',g,{x for x in possible if regions[x[0]][x[1]] == g}))
        hit = None
        for kind,key,candidates in units:
            done = ((kind=='row' and any(r==key for r,c in cats)) or
                    (kind=='col' and any(c==key for r,c in cats)) or
                    (kind=='region' and any(regions[r][c]==key for r,c in cats)))
            if not done and len(candidates) == 1:
                hit = next(iter(candidates)); break
        if hit:
            r,c = hit; group = regions[r][c]; cats.add(hit); direct += 1
            possible = {x for x in possible if x == hit or
                        (x[0] != r and x[1] != c and regions[x[0]][x[1]] != group and
                         not(abs(x[0]-r) <= 1 and abs(x[1]-c) <= 1))}
            continue
        changed = False
        for kind,key,candidates in units:
            if len(candidates) < 2: continue
            rows={r for r,c in candidates}; cols={c for r,c in candidates}; remove=set()
            if kind=='region' and len(rows)==1:
                rr=next(iter(rows)); remove={x for x in possible if x[0]==rr and x not in candidates}
            elif kind=='region' and len(cols)==1:
                cc=next(iter(cols)); remove={x for x in possible if x[1]==cc and x not in candidates}
            elif kind in ('row','col'):
                groups={regions[r][c] for r,c in candidates}
                if len(groups)==1:
                    g=next(iter(groups)); remove={x for x in possible if regions[x[0]][x[1]]==g and x not in candidates}
            if remove:
                possible -= remove; locked += 1; changed = True; break
        if changed: continue
        for kind,key,candidates in units:
            if not 2 <= len(candidates) <= 4: continue
            common_cells = None
            for r,c in candidates:
                adjacent = {x for x in possible if x not in candidates and abs(x[0]-r)<=1 and abs(x[1]-c)<=1}
                common_cells = adjacent if common_cells is None else common_cells & adjacent
            if common_cells:
                possible -= common_cells; common += 1; changed = True; break
        if not changed:
            return False, {'direct':direct,'locked':locked,'commonAdjacency':common}
    return True, {'direct':direct,'locked':locked,'commonAdjacency':common}


def area_stats(regions):
    n=len(regions); counts=Counter(v for row in regions for v in row)
    return {'singletons':sum(v==1 for v in counts.values()),
            'twoCells':sum(v==2 for v in counts.values()),
            'minimum':min(counts.values()), 'maximum':max(counts.values()),
            'sizes':[counts[g] for g in range(n)]}


def generate(stage_no, used):
    n=SIZE_PLAN[stage_no]; rng=random.Random(20400000 + stage_no*1009)
    profiles=[(3,1),(4,1),(2,2),(3,2)]
    started=time.time()
    for attempt in range(1, MAX_ATTEMPTS+1):
        solution=make_solution(n,rng)
        profile=profiles[(attempt-1)//25000 % len(profiles)]
        regions=make_regions(solution,rng,profile)
        if regions is None or not connected(regions): continue
        stats=area_stats(regions)
        if stats['singletons'] > 4 or stats['twoCells'] < 1: continue
        key=canonical_key(regions)
        if key in used: continue
        count,found=solution_count(regions,2)
        if count != 1 or found != solution: continue
        solved,steps=logic_solve(regions)
        if not solved: continue
        print(f'FOUND: Stage {stage_no} {n}x{n} attempt={attempt} profile={profile} singletons={stats["singletons"]} twoCells={stats["twoCells"]} elapsed={time.time()-started:.1f}s',flush=True)
        return solution,regions,steps,stats,key,attempt,profile
    raise RuntimeError(f'Stage {stage_no}: no pilot candidate found within {MAX_ATTEMPTS} attempts')


def main():
    if not (ROOT/'.git').exists(): raise RuntimeError('Run from cat-logic-puzzle project root.')
    stages=[]; used=set(); details=[]
    for no in range(201,211):
        solution,regions,steps,stats,key,attempt,profile=generate(no,used); used.add(key)
        stars=STAR_PLAN[no]
        stage={'stage':no,'size':SIZE_PLAN[no],'name':f'ステージ{no}',
               'difficulty':'EASY' if stars==2 else 'NORMAL' if stars==3 else 'HARD',
               'logicLevel':2,'regions':regions,'solution':solution,'tutorial':False,
               'bonus':False,'hard':stars>=4,'specialType':'milestone' if no in (205,210) else 'normal',
               'chapter':'chapter-3','sourcePuzzleStage':'generated-new-stage-201-210-v204-pilot',
               'areaStats':stats,
               'quality':{'uniqueSolution':True,'solutionCount':1,'logicOnly':True,
                          'highestRuleLevel':2,'difficultyStars':stars,
                          'logicalStepCount':sum(steps.values()),'ruleUsage':steps,
                          'assumptionRequired':False,'initialCats':0,
                          'newLayout':True,'rotationReflectionChecked':True}}
        stages.append(stage)
        details.append({'stage':no,'size':SIZE_PLAN[no],'stars':stars,'attempt':attempt,
                        'profile':list(profile),'areaStats':stats,'logic':steps})
    payload={'title':'NEKOMICHI STAGE 201-210 NEW GENERATOR PILOT V204',
             'seedFamily':'20400000 + stage*1009','method':'new constrained region growth; no Stage 101-200 source layouts',
             'policy':{'stageRange':[201,210],'sizes':'8x8-12x12 mixed','stars':'2-4 mixed',
                       'maxSingletonsPerStage':4,'minimumTwoCellRegionsPerStage':1,
                       'uniqueSolution':True,'logicOnlyLevel2':True,'assumptionForbidden':True},
             'stages':stages}
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    audit={'title':'NEKOMICHI STAGE 201-210 PILOT AUDIT V204','passed':True,
           'stageCount':len(stages),'stageRange':[201,210],
           'sizes':dict(Counter(s['size'] for s in stages)),
           'difficultyStars':dict(Counter(s['quality']['difficultyStars'] for s in stages)),
           'allUnique':True,'allLogicOnlyLevel2':True,'allConnected':True,
           'allHaveTwoCellRegion':all(s['areaStats']['twoCells']>=1 for s in stages),
           'maximumSingletons':max(s['areaStats']['singletons'] for s in stages),
           'details':details}
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OK: Stage 201-210 new-generator pilot completed.')
    print('OK: sizes 8x8-12x12 and stars 2-4 are mixed.')
    print('OK: every pilot board is new, connected, unique and level-2 logic-only.')
    print('OUTPUT:',OUTPUT.name)
    print('AUDIT:',AUDIT.name)
    print('SEND: Upload both generated JSON files to Copilot.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('ERROR:',exc); sys.exit(1)
