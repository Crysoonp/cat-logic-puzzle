from pathlib import Path
from collections import Counter, deque
import hashlib
import json
import random
import sys
import time

ROOT = Path.cwd()
OUTPUT = ROOT / 'NEKOMICHI_STAGE_GENERATOR_BENCHMARK_V206.json'
CANDIDATES = ROOT / 'NEKOMICHI_STAGE_GENERATOR_BENCHMARK_CANDIDATES_V206.json'

SIZES = [8, 9, 10, 11, 12]
SECONDS_PER_SIZE = 20.0
GLOBAL_SECONDS = 100.0
PROGRESS_SECONDS = 5.0
SEED = 20620261013


def neighbors4(r, c, n):
    for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
        if 0 <= rr < n and 0 <= cc < n:
            yield rr, cc


def make_solution(n, rng):
    for _ in range(5000):
        cols = list(range(n))
        rng.shuffle(cols)
        if all(abs(cols[r] - cols[r - 1]) > 1 for r in range(1, n)):
            return cols
    return None


def grow_regions(solution, profile, rng):
    n = len(solution)
    board = [[-1] * n for _ in range(n)]
    cells = [set() for _ in range(n)]
    protected = set()

    for row, col in enumerate(solution):
        board[row][col] = row
        cells[row].add((row, col))

    ids = list(range(n))
    rng.shuffle(ids)
    singleton_ids = set(ids[:2 if profile != 1 else 3])
    double_ids = set(ids[len(singleton_ids):len(singleton_ids) + (2 if profile != 3 else 1)])
    protected |= singleton_ids | double_ids

    occupied = {(r, solution[r]) for r in range(n)}
    for region_id in list(double_ids):
        seed = (region_id, solution[region_id])
        options = [point for point in neighbors4(seed[0], seed[1], n) if point not in occupied]
        if not options:
            return None
        point = rng.choice(options)
        board[point[0]][point[1]] = region_id
        cells[region_id].add(point)
        occupied.add(point)

    remaining = n * n - len(occupied)
    active = [region_id for region_id in range(n) if region_id not in protected]
    if not active:
        return None

    while remaining:
        choices = []
        for region_id in active:
            frontier = set()
            for r, c in cells[region_id]:
                frontier.update((rr, cc) for rr, cc in neighbors4(r, c, n) if board[rr][cc] == -1)
            if frontier:
                choices.append((len(cells[region_id]), region_id, list(frontier)))
        if not choices:
            # Attach enclosed cells to any adjacent non-protected region.
            progress = False
            for r in range(n):
                for c in range(n):
                    if board[r][c] != -1:
                        continue
                    adjoining = [board[rr][cc] for rr,cc in neighbors4(r,c,n)
                                 if board[rr][cc] in active]
                    if adjoining:
                        region_id = rng.choice(adjoining)
                        board[r][c] = region_id
                        cells[region_id].add((r,c))
                        remaining -= 1
                        progress = True
            if not progress:
                return None
            continue
        choices.sort(key=lambda item: item[0])
        width = max(1, min(5, len(choices)))
        _, region_id, frontier = rng.choice(choices[:width])
        r, c = rng.choice(frontier)
        board[r][c] = region_id
        cells[region_id].add((r, c))
        remaining -= 1

    return board


def connected_regions(board):
    n = len(board)
    for region_id in range(n):
        region_cells = {
            (r, c)
            for r in range(n)
            for c in range(n)
            if board[r][c] == region_id
        }
        if not region_cells:
            return False
        start = next(iter(region_cells))
        seen = {start}
        queue = deque([start])
        while queue:
            r, c = queue.popleft()
            for point in neighbors4(r, c, n):
                if point in region_cells and point not in seen:
                    seen.add(point)
                    queue.append(point)
        if seen != region_cells:
            return False
    return True


def count_solutions(board, limit=2):
    n = len(board)
    rows = [None] * n
    used_cols = set()
    used_regions = set()
    total = 0
    first = None

    def search(row):
        nonlocal total, first
        if total >= limit:
            return
        if row == n:
            total += 1
            if first is None:
                first = rows[:]
            return

        options = []
        for col in range(n):
            region_id = board[row][col]
            if col in used_cols or region_id in used_regions:
                continue
            if row > 0 and rows[row - 1] is not None and abs(rows[row - 1] - col) <= 1:
                continue
            options.append(col)

        for col in options:
            region_id = board[row][col]
            rows[row] = col
            used_cols.add(col)
            used_regions.add(region_id)
            search(row + 1)
            used_regions.remove(region_id)
            used_cols.remove(col)
            rows[row] = None
            if total >= limit:
                return

    search(0)
    return total, first


def canonical_key(board):
    n = len(board)
    variants = []
    current = board
    for _ in range(4):
        variants.append(current)
        variants.append([list(reversed(row)) for row in current])
        current = [[current[n - 1 - c][r] for c in range(n)] for r in range(n)]

    signatures = []
    for grid in variants:
        mapping = {}
        next_id = 0
        normalized = []
        for row in grid:
            normalized_row = []
            for value in row:
                if value not in mapping:
                    mapping[value] = next_id
                    next_id += 1
                normalized_row.append(mapping[value])
            normalized.append(normalized_row)
        signatures.append(json.dumps(normalized, separators=(',', ':')))

    return hashlib.sha256(min(signatures).encode('utf-8')).hexdigest()


def area_stats(board):
    n = len(board)
    counts = Counter(value for row in board for value in row)
    sizes = [counts[i] for i in range(n)]
    return {
        'sizes': sizes,
        'minimum': min(sizes),
        'maximum': max(sizes),
        'singletons': sum(value == 1 for value in sizes),
        'twoCells': sum(value == 2 for value in sizes),
    }


def benchmark_size(n, global_deadline):
    rng = random.Random(SEED + n * 1009)
    started = time.perf_counter()
    deadline = min(started + SECONDS_PER_SIZE, global_deadline)
    next_progress = started + PROGRESS_SECONDS
    attempts = 0
    unique_checks = 0
    connected_count = 0
    best = None

    print(f'START: {n}x{n}, time limit {deadline - started:.0f}s', flush=True)

    while time.perf_counter() < deadline:
        attempts += 1
        solution = make_solution(n, rng)
        if solution is None:
            continue

        profile = (attempts - 1) % 4
        board = grow_regions(solution, profile, rng)
        if board is None or not connected_regions(board):
            continue

        connected_count += 1
        stats = area_stats(board)
        if stats['singletons'] > 3 or stats['twoCells'] < 1:
            continue

        unique_checks += 1
        solution_total, found_solution = count_solutions(board, 2)
        if solution_total == 1:
            best = {
                'size': n,
                'solution': found_solution,
                'regions': board,
                'areaStats': stats,
                'canonicalKey': canonical_key(board),
                'attempt': attempts,
                'profile': profile,
            }
            break

        now = time.perf_counter()
        if now >= next_progress:
            elapsed = now - started
            print(
                f'PROGRESS: {n}x{n} elapsed={elapsed:.1f}s '
                f'attempts={attempts} connected={connected_count} '
                f'uniqueChecks={unique_checks}',
                flush=True,
            )
            next_progress = now + PROGRESS_SECONDS

    elapsed = time.perf_counter() - started
    if best:
        print(
            f'FOUND: {n}x{n} elapsed={elapsed:.2f}s attempt={attempts} '
            f'singletons={best["areaStats"]["singletons"]} '
            f'twoCells={best["areaStats"]["twoCells"]}',
            flush=True,
        )
        status = 'FOUND'
    else:
        print(
            f'TIMEOUT: {n}x{n} elapsed={elapsed:.2f}s attempts={attempts}',
            flush=True,
        )
        status = 'TIMEOUT'

    return {
        'size': n,
        'status': status,
        'elapsedSeconds': round(elapsed, 3),
        'attempts': attempts,
        'connectedCandidates': connected_count,
        'uniqueChecks': unique_checks,
        'candidate': best,
    }


def main():
    if not (ROOT / '.git').exists():
        raise RuntimeError('Run from the cat-logic-puzzle project root.')

    started = time.perf_counter()
    global_deadline = started + GLOBAL_SECONDS
    results = []

    for n in SIZES:
        if time.perf_counter() >= global_deadline:
            results.append({
                'size': n,
                'status': 'SKIPPED_GLOBAL_TIMEOUT',
                'elapsedSeconds': 0,
                'attempts': 0,
                'connectedCandidates': 0,
                'uniqueChecks': 0,
                'candidate': None,
            })
            continue
        results.append(benchmark_size(n, global_deadline))

    candidates = [result['candidate'] for result in results if result['candidate']]
    duplicate_keys = len(candidates) - len({item['canonicalKey'] for item in candidates})
    total_elapsed = time.perf_counter() - started

    report = {
        'benchmarkVersion': 'V206',
        'purpose': 'Protected tiny-region growth benchmark for new 8x8-12x12 generation.',
        'timeLimits': {
            'perSizeSeconds': SECONDS_PER_SIZE,
            'globalSeconds': GLOBAL_SECONDS,
            'progressIntervalSeconds': PROGRESS_SECONDS,
        },
        'totalElapsedSeconds': round(total_elapsed, 3),
        'foundCount': len(candidates),
        'requiredCount': len(SIZES),
        'allSizesFound': len(candidates) == len(SIZES),
        'rotationReflectionDuplicateCount': duplicate_keys,
        'results': results,
        'decision': (
            'READY_FOR_10_STAGE_PILOT'
            if len(candidates) == len(SIZES) and duplicate_keys == 0
            else 'GENERATOR_NEEDS_DIFFERENT_CONSTRUCTION'
        ),
        'gameFilesModified': False,
    }

    candidate_payload = {
        'title': 'NEKOMICHI GENERATOR SPEED BENCHMARK CANDIDATES V206',
        'candidateOnly': True,
        'notIntegrated': True,
        'candidates': candidates,
    }

    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    CANDIDATES.write_text(
        json.dumps(candidate_payload, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    print('OK: Speed benchmark finished without an endless search.', flush=True)
    print(f'RESULT: {report["decision"]}', flush=True)
    print(f'FOUND: {len(candidates)}/{len(SIZES)} sizes', flush=True)
    print(f'TOTAL_SECONDS: {total_elapsed:.2f}', flush=True)
    print('REPORT:', OUTPUT, flush=True)
    print('CANDIDATES:', CANDIDATES, flush=True)
    print('SEND: Upload the two generated JSON files to Copilot.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('CANCELLED: User stopped the speed benchmark.', flush=True)
        sys.exit(130)
    except Exception as exc:
        print('ERROR:', exc, flush=True)
        sys.exit(1)
