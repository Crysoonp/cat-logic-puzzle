#!/usr/bin/env python3
"""Cat Logic Puzzle offline stage generator Ver.1.0.
Run from the cat-logic-puzzle project root.
"""
from __future__ import annotations
import argparse, json, logging, os, random, re, signal, sys, time
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VERSION = "1.0.4"
ROOT = Path.cwd()
DATA_DIR = ROOT / "generator-data"
GENERATED_JSON = DATA_DIR / "generated-stages.json"
PROGRESS_JSON = DATA_DIR / "generator-progress-v104.json"
FINGERPRINTS_JSON = DATA_DIR / "stage-fingerprints.json"
REJECTED_JSON = DATA_DIR / "rejected-statistics.json"
LOG_FILE = DATA_DIR / "generator.log"
IMPORT_JS = ROOT / "generated-stages-16-50.js"
EXPORT_JS = ROOT / "generated-stages-16-50-python.js"
STAGES_JS = ROOT / "stages.js"
CONFIG_JSON = ROOT / "generator_config.json"
STOP = False

DEFAULT_CONFIG = {
    "stage_ranges": [
        {"start": 16, "end": 20, "size": 5, "difficulty_min": 1, "difficulty_max": 2, "logic_only": True},
        {"start": 21, "end": 30, "size": 6, "difficulty_min": 1, "difficulty_max": 2, "logic_only": True},
        {"start": 31, "end": 40, "size": 7, "difficulty_min": 2, "difficulty_max": 3, "logic_only": True},
        {"start": 41, "end": 50, "size": 8, "difficulty_min": 2, "difficulty_max": 3, "logic_only": True}
    ],
    "progress_interval": 1000,
    "checkpoint_interval": 100,
    "max_attempts_per_stage": 250000,
    "random_seed": 20260929
}

def atomic_json(path: Path, data) -> None:
    """Windows対応の安全保存。置換競合時は再試行し、最後は直接保存する。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    last_error = None
    for retry in range(8):
        tmp = path.with_name(f"{path.name}.{os.getpid()}.{retry}.tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            return
        except PermissionError as exc:
            last_error = exc
            try:
                if tmp.exists(): tmp.unlink()
            except OSError:
                pass
            time.sleep(0.15 * (retry + 1))
    # ウイルス対策やVS Codeの監視で置換だけ拒否される場合の最終手段。
    try:
        path.write_text(payload, encoding="utf-8")
        print(f"保存警告: {path.name} は直接保存へ切り替えました。", flush=True)
        return
    except OSError as exc:
        raise RuntimeError(f"{path} を保存できません: {exc}; replace error={last_error}") from exc

def load_json(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError): return default

def extract_array(path: Path) -> list:
    if not path.exists(): return []
    text = path.read_text(encoding="utf-8-sig")
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < start: return []
    chunk = text[start:end+1]
    try: return json.loads(chunk)
    except json.JSONDecodeError:
        # Convert the limited JS object syntax used in stages.js.
        chunk = re.sub(r"(?([{,])\s*([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', chunk)
        chunk = chunk.replace("'", '"').replace("undefined", "null")
        chunk = re.sub(r",\s*([}\]])", r"\1", chunk)
        try: return json.loads(chunk)
        except json.JSONDecodeError: return []

def stage_rule(no: int, cfg: dict) -> dict:
    for rule in cfg["stage_ranges"]:
        if rule["start"] <= no <= rule["end"]: return rule
    raise ValueError(f"Stage {no} has no configuration")

def valid_solution(sol: list[int]) -> bool:
    return len(sol) == len(set(sol)) and all(abs(sol[r] - sol[r-1]) > 1 for r in range(1, len(sol)))

def make_solution(n: int, rng: random.Random) -> Optional[list[int]]:
    values = list(range(n))
    for _ in range(3000):
        rng.shuffle(values)
        if valid_solution(values): return values.copy()
    return None

def neighbors4(r, c, n):
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < n and 0 <= cc < n: yield rr, cc

def make_regions(n: int, solution: list[int], rng: random.Random) -> Optional[list[list[int]]]:
    grid = [[-1]*n for _ in range(n)]
    cells = [[] for _ in range(n)]
    for r, c in enumerate(solution): grid[r][c] = r; cells[r].append((r,c))
    left, guard = n*n-n, n*n*400
    while left and guard:
        guard -= 1
        expandable = [g for g in range(n) if any(grid[rr][cc] < 0 for r,c in cells[g] for rr,cc in neighbors4(r,c,n))]
        if not expandable: break
        min_size = min(len(cells[g]) for g in expandable)
        pool = [g for g in expandable if len(cells[g]) <= min_size+1]
        g = rng.choice(pool)
        frontier = list({(rr,cc) for r,c in cells[g] for rr,cc in neighbors4(r,c,n) if grid[rr][cc] < 0})
        if not frontier: continue
        rr, cc = rng.choice(frontier); grid[rr][cc] = g; cells[g].append((rr,cc)); left -= 1
    return None if left else grid

def connected_regions(stage: dict) -> bool:
    n, regions = stage["size"], stage["regions"]
    for g in range(n):
        pts = {(r,c) for r in range(n) for c in range(n) if regions[r][c] == g}
        if not pts: return False
        seen, q = {next(iter(pts))}, deque([next(iter(pts))])
        while q:
            r,c=q.popleft()
            for p in neighbors4(r,c,n):
                if p in pts and p not in seen: seen.add(p); q.append(p)
        if seen != pts: return False
    return True

def find_solutions(stage: dict, limit=2) -> list[list[int]]:
    """Return up to limit solutions, so adaptive repair can compare alternatives."""
    n, reg = stage["size"], stage["regions"]
    used_c, used_g, chosen, found = set(), set(), [-1]*n, []
    def dfs(r, prev):
        if len(found) >= limit: return
        if r == n: found.append(chosen.copy()); return
        for c in range(n):
            g=reg[r][c]
            if c in used_c or g in used_g or (prev is not None and abs(c-prev)<=1): continue
            chosen[r]=c; used_c.add(c); used_g.add(g); dfs(r+1,c); used_c.remove(c); used_g.remove(g); chosen[r]=-1
            if len(found)>=limit: return
    dfs(0,None); return found

def count_solutions(stage: dict, limit=2) -> int:
    return len(find_solutions(stage,limit))

def region_connected_after_move(grid, cell, new_region, n):
    r,c=cell; old=grid[r][c]
    if old==new_region: return False
    test=[row[:] for row in grid]; test[r][c]=new_region
    for g in (old,new_region):
        pts={(rr,cc) for rr in range(n) for cc in range(n) if test[rr][cc]==g}
        if not pts: return False
        first=next(iter(pts)); seen={first}; q=deque([first])
        while q:
            rr,cc=q.popleft()
            for p in neighbors4(rr,cc,n):
                if p in pts and p not in seen: seen.add(p); q.append(p)
        if seen!=pts: return False
    return True

def solution_count_score(stage: dict, limit=128) -> int:
    """Count enough solutions to guide gradual repair. limit means 128 or more."""
    return len(find_solutions(stage, limit))

def boundary_moves(grid, protected, n):
    moves=[]
    for r in range(n):
        for c in range(n):
            if (r,c) in protected: continue
            old=grid[r][c]
            for new_region in {grid[rr][cc] for rr,cc in neighbors4(r,c,n) if grid[rr][cc]!=old}:
                if region_connected_after_move(grid,(r,c),new_region,n):
                    moves.append(((r,c),new_region))
    return moves

def adaptive_repair(stage: dict, rng: random.Random, max_repairs=160):
    """Stage 41 capable repair: accept gradual reductions, not only 2 -> 1."""
    n=stage["size"]; grid=[row[:] for row in stage["regions"]]; target=stage["solution"]
    protected={(r,target[r]) for r in range(n)}
    trial=dict(stage); trial["regions"]=grid
    best_score=solution_count_score(trial,128)
    if best_score==1: return trial,0
    stagnant=0
    for repair in range(1,max_repairs+1):
        moves=boundary_moves(grid,protected,n); rng.shuffle(moves)
        best_move=None; best_grid=None; round_score=best_score
        # Search many legal boundary mutations and keep the strongest reduction.
        for cell,new_region in moves[:min(len(moves),180)]:
            candidate=[row[:] for row in grid]; r,c=cell; candidate[r][c]=new_region
            check=dict(stage); check["regions"]=candidate
            score=solution_count_score(check,128)
            if score==0: continue
            if score<round_score:
                round_score=score; best_move=(cell,new_region); best_grid=candidate
                if score==1: break
        if best_grid is not None:
            grid=best_grid; best_score=round_score; stagnant=0
            if best_score==1:
                result=dict(stage); result["regions"]=grid; return result,repair
            continue
        stagnant+=1
        # Escape local minima with a reversible legal mutation after repeated stalls.
        if stagnant>=6 and moves:
            cell,new_region=rng.choice(moves); candidate=[row[:] for row in grid]; r,c=cell; candidate[r][c]=new_region
            check=dict(stage); check["regions"]=candidate; score=solution_count_score(check,128)
            if 0<score<=best_score+8:
                grid=candidate; best_score=score
            stagnant=0
    return None,max_repairs

def anchor_count_for_stage(stage_no: int) -> int:
    """Vary the number of logic anchors so stages 41-50 are not identical."""
    pattern = {
        41: 2,
        42: 3,
        43: 2,
        44: 4,
        45: 3,
        46: 2,
        47: 4,
        48: 3,
        49: 2,
        50: 4,
    }
    return pattern.get(stage_no, 3)


def anchor_keep_size(stage_no: int, anchor_index: int) -> int:
    """Return 2 or 3 cells to create different starting structures."""
    return 2 + ((stage_no + anchor_index) % 2)


def make_8x8_seed(stage_no: int, rng: random.Random):
    """Construct an 8x8 seed for stages 41-50 with varied logic anchors."""
    n = 8
    for _ in range(400):
        solution = make_solution(n, rng)
        if not solution:
            continue

        grid = make_regions(n, solution, rng)
        if grid is None:
            continue

        protected = {(r, solution[r]) for r in range(n)}
        anchor_count = anchor_count_for_stage(stage_no)

        # Rotate the preferred region order by stage number for variety.
        region_order = list(range(n))
        shift = (stage_no - 41) % n
        region_order = region_order[shift:] + region_order[:shift]
        head = region_order[:max(anchor_count + 2, 5)]
        rng.shuffle(head)
        anchors = head[:anchor_count]

        for anchor_index, region_id in enumerate(anchors):
            cat = (region_id, solution[region_id])
            desired_size = anchor_keep_size(stage_no, anchor_index)
            keep = {cat}

            # Keep a short connected arm around the correct cat.
            frontier = [cat]
            while len(keep) < desired_size and frontier:
                base = frontier.pop(0)
                choices = [
                    p for p in neighbors4(*base, n)
                    if grid[p[0]][p[1]] == region_id and p not in keep
                ]
                rng.shuffle(choices)
                if not choices:
                    continue
                chosen = choices[0]
                keep.add(chosen)
                frontier.append(chosen)

            owned = [
                (r, c)
                for r in range(n)
                for c in range(n)
                if grid[r][c] == region_id and (r, c) not in keep
            ]
            rng.shuffle(owned)

            for cell in owned:
                neighboring_regions = list({
                    grid[rr][cc]
                    for rr, cc in neighbors4(*cell, n)
                    if grid[rr][cc] != region_id
                })
                rng.shuffle(neighboring_regions)

                for new_region in neighboring_regions:
                    if cell in protected:
                        continue
                    if region_connected_after_move(grid, cell, new_region, n):
                        grid[cell[0]][cell[1]] = new_region
                        break

        stage = {
            "stage": stage_no,
            "size": 8,
            "name": f"ステージ{stage_no}",
            "difficulty": "自動判定",
            "logicLevel": 0,
            "regions": grid,
            "solution": solution,
            "generationProfile": {
                "type": "constructed-8x8",
                "anchorCount": anchor_count,
                "profileVersion": "1.0.4",
            },
        }

        if connected_regions(stage):
            return stage

    return None

def key(r,c): return (r,c)
def candidates(stage, cats: set, xs: set) -> set:
    n, reg = stage["size"], stage["regions"]
    rows={r for r,c in cats}; cols={c for r,c in cats}; regs={reg[r][c] for r,c in cats}; out=set()
    for r in range(n):
        for c in range(n):
            if (r,c) in cats or (r,c) in xs or r in rows or c in cols or reg[r][c] in regs: continue
            if any(abs(rr-r)<=1 and abs(cc-c)<=1 for rr,cc in cats): continue
            out.add((r,c))
    return out

def units(stage, cats, cand):
    n, reg=stage["size"],stage["regions"]; out=[]
    for r in range(n):
        cells=[(r,c) for c in range(n)]
        if not any(x in cats for x in cells): out.append(("row",r,cells,[x for x in cells if x in cand]))
    for c in range(n):
        cells=[(r,c) for r in range(n)]
        if not any(x in cats for x in cells): out.append(("column",c,cells,[x for x in cells if x in cand]))
    for g in range(n):
        cells=[(r,c) for r in range(n) for c in range(n) if reg[r][c]==g]
        if not any(x in cats for x in cells): out.append(("region",g,cells,[x for x in cells if x in cand]))
    return out

def logical_solve(stage: dict) -> dict:
    n, reg=stage["size"],stage["regions"]; cats=set(); xs=set(); usage=Counter(); steps=0; guard=n*n*20
    while len(cats)<n and guard:
        guard-=1; changed=False
        # Level 1 exclusions from found cats.
        ex=set()
        for fr,fc in cats:
            g=reg[fr][fc]
            for r in range(n):
                for c in range(n):
                    if (r,c) not in cats and (r==fr or c==fc or reg[r][c]==g or (abs(fr-r)<=1 and abs(fc-c)<=1)): ex.add((r,c))
        new=ex-xs
        if new: xs|=new; usage[1]+=1; steps+=1; continue
        cand=candidates(stage,cats,xs); us=units(stage,cats,cand)
        one=next((u for u in us if len(u[3])==1),None)
        if one: cats.add(one[3][0]); usage[1]+=1; steps+=1; continue
        # Level 2 locked candidates.
        applied=False
        for typ,idx,cells,opts in us:
            if len(opts)<2: continue
            rows={r for r,c in opts}; cols={c for r,c in opts}; regs={reg[r][c] for r,c in opts}
            checks=[]
            if typ!='row' and len(rows)==1: checks.append(('row',next(iter(rows))))
            if typ!='column' and len(cols)==1: checks.append(('column',next(iter(cols))))
            if typ!='region' and len(regs)==1: checks.append(('region',next(iter(regs))))
            for t,i in checks:
                other=next((u for u in us if u[0]==t and u[1]==i),None)
                targets=set(other[3])-set(opts) if other else set()
                if targets: xs|=targets; usage[2]+=1; steps+=1; applied=True; break
            if applied: break
        if applied: continue
        # Level 2 common adjacency.
        for typ,idx,cells,opts in us:
            if 2<=len(opts)<=4:
                target=next((p for p in cand-set(opts) if all(abs(p[0]-r)<=1 and abs(p[1]-c)<=1 for r,c in opts)),None)
                if target: xs.add(target); usage[2]+=1; steps+=1; applied=True; break
        if applied: continue
        break
    hi=max(usage.keys(),default=1); score={1:0,2:10,3:25}.get(hi,25)+(0 if n<=4 else 3 if n<=6 else 6)+ (0 if steps<=2 else 3 if steps<=4 else 6 if steps<=7 else 10 if steps<=11 else 15)
    diff=1 if score<=14 else 2 if score<=29 else 3 if score<=49 else 4
    return {"solved":len(cats)==n,"difficulty":max(diff,hi),"score":score,"steps":steps,"highest_rule":hi,"usage":dict(usage)}

def normalized_regions(regions):
    mapping={}; nxt=0; out=[]
    for row in regions:
        nr=[]
        for v in row:
            if v not in mapping: mapping[v]=nxt; nxt+=1
            nr.append(mapping[v])
        out.append(nr)
    return out

def transform(stage,t):
    n=stage["size"]; reg=[[0]*n for _ in range(n)]; sol=[0]*n
    def xy(r,c):
        return ((r,c),(c,n-1-r),(n-1-r,n-1-c),(n-1-c,r),(r,n-1-c),(n-1-r,c),(c,r),(n-1-c,n-1-r))[t]
    for r in range(n):
        for c in range(n): rr,cc=xy(r,c); reg[rr][cc]=stage["regions"][r][c]
    for r,c in enumerate(stage["solution"]): rr,cc=xy(r,c); sol[rr]=cc
    return normalized_regions(reg),sol

def fingerprint(stage):
    n=stage["size"]; values=[]
    for t in range(8):
        reg,sol=transform(stage,t); values.append(f"{n}|"+'/'.join(','.join(map(str,row)) for row in reg)+'|'+','.join(map(str,sol)))
    return min(values)

def export_js(stages):
    EXPORT_JS.write_text("// Generated by Python Cat Logic Generator Ver.1.0\nconst GENERATED_STAGES = "+json.dumps(sorted(stages,key=lambda s:s['stage']),ensure_ascii=False,indent=2)+";\n",encoding="utf-8")

def install_signal():
    def handler(sig, frame):
        global STOP; STOP=True; print("\n停止要求を受け付けました。安全に保存して終了します。")
    signal.signal(signal.SIGINT,handler)

def generate(args, cfg, stages):
    rng=random.Random(cfg["random_seed"]+int(time.time())); existing={fingerprint(s) for s in stages}; stats=Counter(load_json(REJECTED_JSON,{})); progress=load_json(PROGRESS_JSON,{})
    start=args.start or min(r["start"] for r in cfg["stage_ranges"]); end=args.end or max(r["end"] for r in cfg["stage_ranges"])
    if args.stage: start=end=args.stage
    done={s["stage"] for s in stages}; targets=[n for n in range(start,end+1) if n not in done]
    print(f"Cat Logic Stage Generator Ver.{VERSION}\n生成済み: {len([n for n in done if 16<=n<=50])}/35  次の対象: {targets[0] if targets else 'なし'}")
    for no in targets:
        rule=stage_rule(no,cfg); attempts=int(progress.get(str(no),{}).get("attempts",0)); started=time.time(); local=Counter(); accepted=None; max_attempts=args.max_attempts or cfg["max_attempts_per_stage"]
        logging.info("Stage %s generation started",no)
        while attempts < max_attempts and not STOP:
            attempts+=1
            if attempts % cfg.get("progress_interval",1000)==0:
                elapsed=max(time.time()-started,0.001); rate=attempts/elapsed
                print(f"Stage {no} | {attempts:,}/{max_attempts:,} | {elapsed:.1f}秒 | {rate:.1f}候補/秒 | {dict(local)}", flush=True)
                progress[str(no)]={"attempts":attempts,"updated":time.strftime('%Y-%m-%d %H:%M:%S'),"rejected":dict(local),"generatorVersion":VERSION}
                atomic_json(PROGRESS_JSON,progress)
            sol=make_solution(rule["size"],rng)
            if sol is None: local["solution_generation"]+=1; continue
            if 41 <= no <= 50:
                stage = make_8x8_seed(no, rng)
                if stage is None:
                    local["region_generation"] += 1
                    continue
                sol = stage["solution"]
                reg = stage["regions"]
            else:
                reg=make_regions(rule["size"],sol,rng)
                if reg is None: local["region_generation"]+=1; continue
                stage={"stage":no,"size":rule["size"],"name":f"ステージ{no}","difficulty":"自動判定","logicLevel":0,"regions":reg,"solution":sol}
            if not connected_regions(stage): local["disconnected"]+=1; continue
            initial=find_solutions(stage,2)
            if len(initial)>1:
                repaired,repair_count=adaptive_repair(stage,rng)
                if repaired is None: local["multiple_unrepaired"]+=1; continue
                stage=repaired; local["adaptive_repaired"]+=1; local["repair_moves"]+=repair_count
            elif not initial: local["no_solution"]+=1; continue
            if count_solutions(stage,2)!=1: local["multiple"]+=1; continue
            logic=logical_solve(stage)
            if rule["logic_only"] and not logic["solved"]: local["not_logic_only"]+=1; continue
            if not rule["difficulty_min"]<=logic["difficulty"]<=rule["difficulty_max"]: local["difficulty_outside"]+=1; continue
            fp=fingerprint(stage)
            if fp in existing: local["duplicate"]+=1; continue
            stage["quality"]={"uniqueSolution":True,"difficulty":logic["difficulty"],"difficultyScore":logic["score"],"logicOnly":logic["solved"],"logicStepCount":logic["steps"],"highestRuleLevel":logic["highest_rule"],"solverVersion":"python-1.0.4","adaptiveRepair":True,"generationProfile":stage.get("generationProfile", {}).get("type", "random")}
            accepted=stage; existing.add(fp); stages.append(stage); break

            # unreachable
        # Progress visibility and checkpointing.
            
        stats.update(local); progress[str(no)]={"attempts":attempts,"updated":time.strftime('%Y-%m-%d %H:%M:%S'),"rejected":dict(local),"generatorVersion":VERSION}
        if accepted:
            progress.pop(str(no),None); atomic_json(GENERATED_JSON,sorted(stages,key=lambda s:s["stage"])); atomic_json(FINGERPRINTS_JSON,sorted(existing)); export_js(stages)
            elapsed=time.time()-started; print(f"Stage {no} 採用 | 試行 {attempts:,} | 難易度 {accepted['quality']['difficulty']} | {elapsed:.1f}秒 | 適応修正 {local['adaptive_repaired']:,}"); logging.info("Stage %s accepted attempts=%s",no,attempts)
        else:
            print(f"Stage {no} 未完了 | 累計 {attempts:,} | 理由 {dict(local)}")
        atomic_json(PROGRESS_JSON,progress); atomic_json(REJECTED_JSON,dict(stats))
        if STOP or not accepted: break
    export_js(stages); return stages

def verify(stages):
    bad=[]; seen={}
    for s in sorted(stages,key=lambda x:x["stage"]):
        errors=[]
        if not valid_solution(s["solution"]): errors.append("正解配置不正")
        if not connected_regions(s): errors.append("領域非連結")
        if count_solutions(s,2)!=1: errors.append("唯一解でない")
        fp=fingerprint(s)
        if fp in seen: errors.append(f"Stage {seen[fp]} と重複")
        seen[fp]=s["stage"]
        if errors: bad.append({"stage":s["stage"],"errors":errors})
    print(f"検査: {len(stages)}問 / 不合格: {len(bad)}問")
    for x in bad: print(x)
    return not bad

def main():
    p=argparse.ArgumentParser(description="Cat Logic Puzzle offline stage generator")
    p.add_argument("--start",type=int);p.add_argument("--end",type=int);p.add_argument("--stage",type=int);p.add_argument("--max-attempts",type=int)
    p.add_argument("--status",action="store_true");p.add_argument("--export",action="store_true");p.add_argument("--verify",action="store_true")
    args=p.parse_args(); DATA_DIR.mkdir(exist_ok=True)
    if not CONFIG_JSON.exists(): atomic_json(CONFIG_JSON,DEFAULT_CONFIG)
    cfg=load_json(CONFIG_JSON,DEFAULT_CONFIG)
    imported=extract_array(IMPORT_JS); saved=load_json(GENERATED_JSON,[]); by_no={s["stage"]:s for s in imported+saved}; stages=list(by_no.values())
    logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format="%(asctime)s %(message)s",encoding="utf-8")
    if imported and len(saved)<len(by_no): atomic_json(GENERATED_JSON,sorted(stages,key=lambda s:s["stage"]))
    if args.status:
        nums=sorted(by_no); print(f"保存済み: {nums}\n次: {next((n for n in range(16,51) if n not in by_no),None)}\n進捗: {load_json(PROGRESS_JSON,{})}"); return
    if args.export: export_js(stages); print(f"出力: {EXPORT_JS}"); return
    if args.verify: sys.exit(0 if verify(stages) else 1)
    install_signal(); generate(args,cfg,stages)

if __name__=="__main__": main()
