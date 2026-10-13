from pathlib import Path
from collections import Counter, deque
import hashlib, json, random, sys, time

ROOT = Path.cwd()
REPORT = ROOT / 'NEKOMICHI_12X12_BENCHMARK_V208.json'
CANDIDATES = ROOT / 'NEKOMICHI_12X12_CANDIDATES_V208.json'
SIZES = [12]
SECONDS_PER_SIZE = 35.0
GLOBAL_SECONDS = 40.0
PROGRESS_SECONDS = 5.0
SEED = 20820261013


def neighbors4(r, c, n):
    for rr, cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0 <= rr < n and 0 <= cc < n:
            yield rr, cc


def make_solution(n, rng):
    for _ in range(10000):
        cols = list(range(n)); rng.shuffle(cols)
        if all(abs(cols[r]-cols[r-1]) > 1 for r in range(1,n)):
            return cols
    return None


def choose_anchor_ids(solution, singleton_count, double_count, rng):
    n = len(solution)
    ids = list(range(n)); rng.shuffle(ids)
    chosen = []
    for region_id in ids:
        r, c = region_id, solution[region_id]
        if all(abs(r-pr) > 1 or abs(c-pc) > 1 for pr,pc,_ in chosen):
            chosen.append((r,c,region_id))
        if len(chosen) >= singleton_count + double_count:
            break
    if len(chosen) < singleton_count + double_count:
        chosen = [(i, solution[i], i) for i in ids[:singleton_count+double_count]]
    singles = {item[2] for item in chosen[:singleton_count]}
    doubles = {item[2] for item in chosen[singleton_count:singleton_count+double_count]}
    return singles, doubles


def build_board(solution, profile, rng):
    n = len(solution)
    board = [[-1]*n for _ in range(n)]
    cells = [set() for _ in range(n)]
    singleton_count, double_count = [(3,3),(4,2),(2,4),(3,2)][profile]
    singles, doubles = choose_anchor_ids(solution, singleton_count, double_count, rng)
    protected = singles | doubles

    for r,c in enumerate(solution):
        board[r][c] = r
        cells[r].add((r,c))

    occupied = {(r,solution[r]) for r in range(n)}
    for region_id in doubles:
        seed = (region_id, solution[region_id])
        options = [p for p in neighbors4(seed[0],seed[1],n) if p not in occupied]
        rng.shuffle(options)
        if not options:
            return None
        point = options[0]
        board[point[0]][point[1]] = region_id
        cells[region_id].add(point)
        occupied.add(point)

    active = [i for i in range(n) if i not in protected]
    remaining = n*n-len(occupied)
    soft_cap = (n*n - singleton_count - 2*double_count + len(active)-1)//len(active) + 5

    while remaining:
        choices=[]
        for region_id in active:
            frontier=set()
            for r,c in cells[region_id]:
                frontier.update(p for p in neighbors4(r,c,n) if board[p[0]][p[1]] == -1)
            if frontier:
                penalty = max(0, len(cells[region_id])-soft_cap)
                choices.append((penalty, len(cells[region_id]), region_id, list(frontier)))
        if not choices:
            return None
        choices.sort(key=lambda x:(x[0],x[1]))
        _,_,region_id,frontier = rng.choice(choices[:min(4,len(choices))])
        r,c = rng.choice(frontier)
        board[r][c] = region_id
        cells[region_id].add((r,c))
        remaining -= 1
    return board


def connected(board):
    n=len(board)
    for region_id in range(n):
        target={(r,c) for r in range(n) for c in range(n) if board[r][c]==region_id}
        if not target: return False
        start=next(iter(target)); seen={start}; q=deque([start])
        while q:
            r,c=q.popleft()
            for p in neighbors4(r,c,n):
                if p in target and p not in seen:
                    seen.add(p); q.append(p)
        if seen != target: return False
    return True


def count_solutions(board, limit=2):
    n=len(board); rows=[None]*n; used_c=set(); used_g=set(); total=0; first=None
    def dfs(r):
        nonlocal total,first
        if total>=limit: return
        if r==n:
            total+=1
            if first is None: first=rows[:]
            return
        options=[]
        for c in range(n):
            g=board[r][c]
            if c in used_c or g in used_g: continue
            if r and rows[r-1] is not None and abs(rows[r-1]-c)<=1: continue
            options.append(c)
        options.sort(key=lambda c: sum(1 for rr in range(r+1,n) if board[rr][c]==board[r][c]))
        for c in options:
            g=board[r][c]; rows[r]=c; used_c.add(c); used_g.add(g)
            dfs(r+1)
            used_g.remove(g); used_c.remove(c); rows[r]=None
            if total>=limit: return
    dfs(0)
    return total,first


def stats(board):
    n=len(board); counts=Counter(v for row in board for v in row); sizes=[counts[i] for i in range(n)]
    return {'sizes':sizes,'minimum':min(sizes),'maximum':max(sizes),
            'singletons':sum(v==1 for v in sizes),'twoCells':sum(v==2 for v in sizes)}


def canonical_key(board):
    n=len(board); variants=[]; cur=board
    for _ in range(4):
        variants += [cur,[list(reversed(row)) for row in cur]]
        cur=[[cur[n-1-c][r] for c in range(n)] for r in range(n)]
    signatures=[]
    for grid in variants:
        remap={}; nxt=0; norm=[]
        for row in grid:
            out=[]
            for v in row:
                if v not in remap: remap[v]=nxt; nxt+=1
                out.append(remap[v])
            norm.append(out)
        signatures.append(json.dumps(norm,separators=(',',':')))
    return hashlib.sha256(min(signatures).encode()).hexdigest()


def run_size(n, global_deadline):
    rng=random.Random(SEED+n*1009); started=time.perf_counter()
    deadline=min(started+SECONDS_PER_SIZE,global_deadline); next_progress=started+PROGRESS_SECONDS
    attempts=connected_count=unique_checks=0; candidate=None; best_max=None
    print(f'START: {n}x{n}, large-board limit {deadline-started:.0f}s',flush=True)
    while time.perf_counter()<deadline:
        attempts+=1; solution=make_solution(n,rng)
        if solution is None: continue
        profile=(attempts-1)%4; board=build_board(solution,profile,rng)
        if board is None or not connected(board): continue
        connected_count+=1; area=stats(board)
        best_max=area['maximum'] if best_max is None else min(best_max,area['maximum'])
        if area['singletons']>4 or area['twoCells']<2 or area['maximum']>30: continue
        unique_checks+=1; total,found=count_solutions(board,2)
        if total==1:
            candidate={'size':n,'solution':found,'regions':board,'areaStats':area,
                       'canonicalKey':canonical_key(board),'attempt':attempts,'profile':profile}
            break
        now=time.perf_counter()
        if now>=next_progress:
            print(f'PROGRESS: {n}x{n} elapsed={now-started:.1f}s attempts={attempts} connected={connected_count} uniqueChecks={unique_checks} bestMaxArea={best_max}',flush=True)
            next_progress=now+PROGRESS_SECONDS
    elapsed=time.perf_counter()-started
    status='FOUND' if candidate else 'TIMEOUT'
    print(f'{status}: {n}x{n} elapsed={elapsed:.2f}s attempts={attempts} uniqueChecks={unique_checks}',flush=True)
    return {'size':n,'status':status,'elapsedSeconds':round(elapsed,3),'attempts':attempts,
            'connectedCandidates':connected_count,'uniqueChecks':unique_checks,
            'bestObservedMaximumArea':best_max,'candidate':candidate}


def main():
    if not (ROOT/'.git').exists(): raise RuntimeError('Run from cat-logic-puzzle project root.')
    started=time.perf_counter(); deadline=started+GLOBAL_SECONDS
    results=[run_size(n,deadline) for n in SIZES]
    candidates=[r['candidate'] for r in results if r['candidate']]
    passed=len(candidates)==1
    report={'benchmarkVersion':'V208','purpose':'12x12-only strengthened-anchor feasibility benchmark.',
            'timeLimits':{'perSizeSeconds':SECONDS_PER_SIZE,'globalSeconds':GLOBAL_SECONDS},
            'totalElapsedSeconds':round(time.perf_counter()-started,3),'foundCount':len(candidates),
            'requiredCount':1,'allLargeSizesFound':len(candidates)==1,'results':results,
            'decision':'READY_FOR_DEEP_LOGIC_AUDIT' if passed else 'LARGE_BOARD_CONSTRUCTION_NEEDS_REPAIR',
            'gameFilesModified':False}
    payload={'title':'NEKOMICHI 12X12 CANDIDATES V208','candidateOnly':True,
             'notIntegrated':True,'candidates':candidates}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    CANDIDATES.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OK: V208 12x12 benchmark finished.',flush=True)
    print('RESULT:',report['decision'],flush=True)
    print(f'FOUND: {len(candidates)}/1 target size',flush=True)
    print('REPORT:',REPORT,flush=True); print('CANDIDATES:',CANDIDATES,flush=True)
    print('SEND: Upload both V208 JSON files to Copilot.',flush=True)

if __name__=='__main__':
    try: main()
    except KeyboardInterrupt:
        print('CANCELLED: User stopped V208.',flush=True); sys.exit(130)
    except Exception as exc:
        print('ERROR:',exc,flush=True); sys.exit(1)
