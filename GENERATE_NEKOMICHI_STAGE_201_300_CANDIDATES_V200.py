from pathlib import Path
import json, random, sys, time
from collections import Counter, deque

ROOT = Path.cwd()
OUT = ROOT / 'NEKOMICHI_STAGE_201_300_CANDIDATES.json'
AUDIT = ROOT / 'NEKOMICHI_STAGE_201_300_GENERATION_AUDIT.json'
SEED = 202610130201300

SIZE_PLAN = ([8] * 18) + ([9] * 20) + ([10] * 24) + ([11] * 20) + ([12] * 18)
DIFF_PLAN = ([2] * 18) + ([3] * 48) + ([4] * 34)
PATTERNS = (
    ['balanced'] * 25 + ['large_small'] * 25 + ['two_large'] * 18 +
    ['tiny_mix'] * 20 + ['long_winding'] * 12
)


def fail(msg):
    raise RuntimeError(msg)


def solution_for(n, rng):
    # A permutation with no diagonal adjacency between successive rows.
    base = list(range(n))
    for _ in range(20000):
        rng.shuffle(base)
        if all(abs(base[r] - base[r + 1]) != 1 for r in range(n - 1)):
            return base[:]
    fail(f'Could not create solution for {n}x{n}')


def neighbors4(r, c, n):
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < n and 0 <= cc < n:
            yield rr, cc


def region_targets(n, pattern, rng):
    total = n * n
    if pattern == 'balanced':
        vals = [total // n] * n
    elif pattern == 'large_small':
        tiny = [1, 2, 2, 3][:min(4, n - 2)]
        vals = tiny + [max(3, (total - sum(tiny)) // (n - len(tiny)))] * (n - len(tiny))
    elif pattern == 'two_large':
        vals = [max(n + 4, total // 4), max(n + 2, total // 5)] + [3] * (n - 2)
    elif pattern == 'tiny_mix':
        small_count = max(2, n // 3)
        vals = [1 if i % 3 == 0 else 2 + (i % 2) for i in range(small_count)] + [4] * (n - small_count)
    else:
        vals = [max(3, n - 2 + (i % 5)) for i in range(n)]
    while sum(vals) < total:
        idx = rng.randrange(n)
        weight = 4 if pattern == 'large_small' and idx == n - 1 else 1
        vals[idx] += weight
    while sum(vals) > total:
        candidates = [i for i, v in enumerate(vals) if v > 1]
        idx = rng.choice(candidates)
        vals[idx] -= 1
    rng.shuffle(vals)
    return vals


def make_regions(n, solution, pattern, rng):
    # Seed every region on its answer cell, then grow connected regions.
    targets = region_targets(n, pattern, rng)
    region = [[-1] * n for _ in range(n)]
    cells = [set() for _ in range(n)]
    for r, c in enumerate(solution):
        region[r][c] = r
        cells[r].add((r, c))

    unassigned = n * n - n
    guard = 0
    while unassigned and guard < n * n * 80:
        guard += 1
        ids = list(range(n))
        rng.shuffle(ids)
        ids.sort(key=lambda i: (len(cells[i]) >= targets[i], len(cells[i]) / max(1, targets[i])))
        moved = False
        for rid in ids:
            frontier = []
            for r, c in cells[rid]:
                for rr, cc in neighbors4(r, c, n):
                    if region[rr][cc] == -1:
                        frontier.append((rr, cc))
            if not frontier:
                continue
            rr, cc = rng.choice(frontier)
            region[rr][cc] = rid
            cells[rid].add((rr, cc))
            unassigned -= 1
            moved = True
            break
        if not moved:
            break
    if unassigned:
        return None
    return region


def candidates_for(n, regions):
    return {(r, c) for r in range(n) for c in range(n)}


def count_solutions(n, regions, limit=2):
    reg_cells = [[] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            reg_cells[regions[r][c]].append((r, c))
    rows = [None] * n
    used_cols = set()
    used_regs = set()
    count = 0

    def legal(r, c):
        if c in used_cols or regions[r][c] in used_regs:
            return False
        if r > 0 and rows[r - 1] is not None and abs(rows[r - 1] - c) <= 1:
            return False
        return True

    def dfs(r):
        nonlocal count
        if count >= limit:
            return
        if r == n:
            count += 1
            return
        options = [c for c in range(n) if legal(r, c)]
        for c in options:
            rows[r] = c
            used_cols.add(c)
            used_regs.add(regions[r][c])
            dfs(r + 1)
            used_regs.remove(regions[r][c])
            used_cols.remove(c)
            rows[r] = None
            if count >= limit:
                return
    dfs(0)
    return count


def logic_trace(n, regions):
    poss = {(r, c) for r in range(n) for c in range(n)}
    cats = set()
    rounds = singles = exclusions = 0

    def groups():
        result = []
        for r in range(n): result.append([(r, c) for c in range(n)])
        for c in range(n): result.append([(r, c) for r in range(n)])
        for rid in range(n): result.append([(r, c) for r in range(n) for c in range(n) if regions[r][c] == rid])
        return result

    changed = True
    while changed and len(cats) < n and rounds < n * n * 4:
        rounds += 1
        changed = False
        for group in groups():
            opts = [x for x in group if x in poss]
            if len(opts) == 1 and opts[0] not in cats:
                r, c = opts[0]
                cats.add((r, c)); singles += 1; changed = True
                rid = regions[r][c]
                remove = set()
                for rr, cc in poss:
                    if (rr, cc) == (r, c): continue
                    if rr == r or cc == c or regions[rr][cc] == rid or (abs(rr-r) <= 1 and abs(cc-c) <= 1):
                        remove.add((rr, cc))
                if remove:
                    poss -= remove; exclusions += len(remove)
        for group in groups():
            if not any(x in cats for x in group) and not any(x in poss for x in group):
                return {'solved': False, 'rounds': rounds, 'singles': singles, 'exclusions': exclusions}
    return {'solved': len(cats) == n, 'rounds': rounds, 'singles': singles, 'exclusions': exclusions}


def area_stats(regions, n):
    counts = Counter(v for row in regions for v in row)
    vals = sorted(counts.values())
    return {
        'areas': vals,
        'min': min(vals), 'max': max(vals),
        'singletons': sum(v == 1 for v in vals),
        'twoCells': sum(v == 2 for v in vals),
        'largeShare': round(max(vals) / (n * n), 4)
    }


def choose_plan(rng):
    sizes = SIZE_PLAN[:]
    diffs = DIFF_PLAN[:]
    patterns = PATTERNS[:]
    rng.shuffle(sizes); rng.shuffle(diffs); rng.shuffle(patterns)
    # Prevent long runs and force landmark stages.
    for i in range(1, len(sizes)):
        if i >= 2 and sizes[i] == sizes[i-1] == sizes[i-2]:
            j = next((j for j in range(i+1, len(sizes)) if sizes[j] != sizes[i]), None)
            if j is not None: sizes[i], sizes[j] = sizes[j], sizes[i]
    diffs[49] = 4
    diffs[99] = 4
    sizes[49] = rng.choice([10,11,12])
    sizes[99] = rng.choice([11,12])
    return sizes, diffs, patterns


def make_stage(stage, n, target_diff, pattern, rng):
    for attempt in range(1, 2501):
        solution = solution_for(n, rng)
        regions = make_regions(n, solution, pattern, rng)
        if regions is None:
            continue
        if count_solutions(n, regions, 2) != 1:
            continue
        trace = logic_trace(n, regions)
        stats = area_stats(regions, n)
        # Difficulty is provisional. Direct-logic solved boards are 2-3; stalled boards are 3-4.
        if trace['solved']:
            measured = 2 if trace['rounds'] <= max(4, n // 2) else 3
        else:
            measured = 4 if n >= 10 else 3
        # Keep requested distribution near target, but never call a stalled board star 2.
        difficulty = max(measured, target_diff if target_diff <= measured + 1 else measured)
        difficulty = min(4, max(2, difficulty))
        if target_diff == 2 and not trace['solved']:
            continue
        return {
            'stage': stage,
            'size': n,
            'difficulty': difficulty,
            'difficultyTarget': target_diff,
            'pattern': pattern,
            'boss': stage in (250, 300),
            'regions': regions,
            'solution': solution,
            'areaStats': stats,
            'logic': trace,
            'uniqueSolution': True,
            'attempt': attempt
        }
    fail(f'Stage {stage}: no candidate after 2500 attempts')


def main():
    rng = random.Random(SEED)
    sizes, diffs, patterns = choose_plan(rng)
    stages = []
    started = time.time()
    for index, stage_no in enumerate(range(201, 301)):
        stage_rng = random.Random(SEED + stage_no * 1009)
        stage = make_stage(stage_no, sizes[index], diffs[index], patterns[index], stage_rng)
        stages.append(stage)
        print(f"OK: Stage {stage_no} {stage['size']}x{stage['size']} star{stage['difficulty']} {stage['pattern']} attempt={stage['attempt']}")

    # Cross-stage exact-layout duplicate check.
    signatures = [json.dumps(s['regions'], separators=(',', ':')) for s in stages]
    if len(set(signatures)) != 100:
        fail('Duplicate region layout detected')

    payload = {
        'format': 'nekomichi-stage-candidates-v1',
        'range': [201, 300],
        'seed': SEED,
        'candidateOnly': True,
        'notIntegrated': True,
        'rules': {
            'oneCatPerRow': True, 'oneCatPerColumn': True,
            'oneCatPerRegion': True, 'noAdjacentEightDirections': True
        },
        'design': {
            'sizes': '8x8 through 12x12, mixed rather than monotonic',
            'visibleEasyLabel': False,
            'allowedAreaVariation': ['balanced','large_small','two_large','tiny_mix','long_winding'],
            'oneAndTwoCellRegionsAllowed': True,
            'stage250And300': 'milestone candidates, star 4 target',
            'star5Included': False,
            'newRuleIncluded': False
        },
        'stages': stages
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    summary = {
        'generated': len(stages),
        'range': [201,300],
        'sizes': dict(sorted(Counter(s['size'] for s in stages).items())),
        'difficulty': dict(sorted(Counter(s['difficulty'] for s in stages).items())),
        'targets': dict(sorted(Counter(s['difficultyTarget'] for s in stages).items())),
        'patterns': dict(sorted(Counter(s['pattern'] for s in stages).items())),
        'uniqueSolutionAll': all(s['uniqueSolution'] for s in stages),
        'directLogicSolved': sum(s['logic']['solved'] for s in stages),
        'containsSingletonRegions': sum(s['areaStats']['singletons'] > 0 for s in stages),
        'containsTwoCellRegions': sum(s['areaStats']['twoCells'] > 0 for s in stages),
        'duplicateLayouts': 0,
        'elapsedSeconds': round(time.time() - started, 3),
        'candidateOnly': True,
        'nextStep': 'Run a deeper production-logic and difficulty audit before integration.'
    }
    AUDIT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('OK: Generated 100 candidate stages for Stage 201-300.')
    print('OK: Every candidate has exactly one solution.')
    print('OK: Board sizes 8x8-12x12 and varied region-area patterns were used.')
    print('OK: No player-visible easy/rest label, new rule, story, companion, reward or timer was added.')
    print('OK: Candidate files only; game files were not modified.')
    print('OUTPUT:', OUT)
    print('AUDIT:', AUDIT)
    print('SEND: Upload both generated JSON files to Copilot.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc)
        sys.exit(1)
