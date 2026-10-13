from pathlib import Path
from collections import Counter, deque
import copy, hashlib, json, random, sys, time

ROOT = Path.cwd()
SOURCE = ROOT / 'NEKOMICHI_12X12_UNIQUENESS_CANDIDATES_V209.json'
REPORT = ROOT / 'NEKOMICHI_12X12_REPAIR_V211.json'
CANDIDATES = ROOT / 'NEKOMICHI_12X12_REPAIRED_CANDIDATES_V211.json'
TIME_LIMIT = 45.0
SEED = 21120261013


def neighbors4(r,c,n):
    for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
        if 0<=rr<n and 0<=cc<n: yield rr,cc


def region_cells(board,g):
    n=len(board)
    return {(r,c) for r in range(n) for c in range(n) if board[r][c]==g}


def connected_cells(cells,n):
    if not cells: return False
    start=next(iter(cells)); seen={start}; q=deque([start])
    while q:
        r,c=q.popleft()
        for p in neighbors4(r,c,n):
            if p in cells and p not in seen: seen.add(p); q.append(p)
    return seen==cells


def all_connected(board):
    return all(connected_cells(region_cells(board,g),len(board)) for g in range(len(board)))


def stats(board):
    n=len(board); c=Counter(v for row in board for v in row); sizes=[c[i] for i in range(n)]
    return {'sizes':sizes,'minimum':min(sizes),'maximum':max(sizes),
            'singletons':sum(v==1 for v in sizes),'twoCells':sum(v==2 for v in sizes)}


def count_solutions(board,limit=2):
    n=len(board); rows=[None]*n; used_c=set(); used_g=set(); total=0; first=None
    def dfs(r):
        nonlocal total,first
        if total>=limit:return
        if r==n:
            total+=1
            if first is None:first=rows[:]
            return
        opts=[]
        for c in range(n):
            g=board[r][c]
            if c in used_c or g in used_g:continue
            if r and rows[r-1] is not None and abs(rows[r-1]-c)<=1:continue
            opts.append(c)
        for c in opts:
            g=board[r][c]; rows[r]=c; used_c.add(c); used_g.add(g)
            dfs(r+1)
            used_g.remove(g); used_c.remove(c); rows[r]=None
            if total>=limit:return
    dfs(0); return total,first


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


def candidate_moves(board,rng):
    n=len(board); st=stats(board); sizes=st['sizes']; singles=[g for g,v in enumerate(sizes) if v==1]
    moves=[]
    for target in singles:
        tr,tc=next(iter(region_cells(board,target)))
        for rr,cc in neighbors4(tr,tc,n):
            donor=board[rr][cc]
            if donor==target or sizes[donor]<=3:continue
            donor_after=region_cells(board,donor)-{(rr,cc)}
            if connected_cells(donor_after,n):
                moves.append((target,donor,rr,cc))
    rng.shuffle(moves)
    return moves


def score(st):
    return st['singletons']*100 + max(0,2-st['twoCells'])*40 + max(0,st['maximum']-40)*3 + st['maximum']


def main():
    if not SOURCE.exists(): raise RuntimeError(f'Missing source: {SOURCE.name}')
    payload=json.loads(SOURCE.read_text(encoding='utf-8'))
    source=payload.get('candidates',[])
    if len(source)!=1 or source[0].get('size')!=12: raise RuntimeError('Expected exactly one V209 12x12 candidate.')
    original=source[0]; base=original['regions']; rng=random.Random(SEED)
    started=time.perf_counter(); deadline=started+TIME_LIMIT
    queue=[base]; seen={canonical_key(base)}; checks=0; generated=0; best=None; best_score=10**9
    print('START: V211 rechecks the best practical 12x12 repair range from V210 the V209 12x12 uniqueness-first candidate.',flush=True)
    while queue and time.perf_counter()<deadline:
        board=queue.pop(0); st=stats(board); sc=score(st)
        if sc<best_score:
            best_score=sc; best=(copy.deepcopy(board),st)
            print(f'BEST: singletons={st["singletons"]} twoCells={st["twoCells"]} max={st["maximum"]}',flush=True)
        if st['singletons']<=4 and st['twoCells']>=2 and st['maximum']<=40:
            checks+=1; total,solution=count_solutions(board,2)
            if total==1:
                repaired={'size':12,'solution':solution,'regions':board,'areaStats':st,
                          'canonicalKey':canonical_key(board),'repairSource':'V209 attempt 64',
                          'qualityTier':'PRACTICAL_RANGE_CANDIDATE_NOT_INTEGRATED'}
                break
        for target,donor,r,c in candidate_moves(board,rng)[:20]:
            new=copy.deepcopy(board); new[r][c]=target
            key=canonical_key(new)
            if key in seen:continue
            seen.add(key); generated+=1
            nst=stats(new)
            # Keep the search focused and prevent a new giant area.
            if nst['maximum']<=42 and all_connected(new): queue.append(new)
        queue.sort(key=lambda b:score(stats(b)))
        if len(queue)>400: queue=queue[:400]
    else:
        repaired=None
    elapsed=time.perf_counter()-started
    decision='READY_FOR_DEEP_LOGIC_AUDIT' if repaired else 'REPAIR_PATH_NOT_FOUND'
    report={'version':'V211','source':SOURCE.name,'elapsedSeconds':round(elapsed,3),
            'generatedVariants':generated,'uniqueSolutionChecks':checks,'decision':decision,
            'bestObserved':best[1] if best else None,'gameFilesModified':False}
    out={'title':'NEKOMICHI 12X12 REPAIRED CANDIDATES V211','candidateOnly':True,
         'notIntegrated':True,'candidates':[repaired] if repaired else []}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    CANDIDATES.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OK: V211 practical-range repair search finished.',flush=True)
    print('RESULT:',decision,flush=True)
    print('REPORT:',REPORT,flush=True); print('CANDIDATES:',CANDIDATES,flush=True)
    print('SEND: Upload both V211 JSON files to Copilot.',flush=True)

if __name__=='__main__':
    try: main()
    except KeyboardInterrupt:
        print('CANCELLED: User stopped V211.',flush=True); sys.exit(130)
    except Exception as exc:
        print('ERROR:',exc,flush=True); sys.exit(1)
