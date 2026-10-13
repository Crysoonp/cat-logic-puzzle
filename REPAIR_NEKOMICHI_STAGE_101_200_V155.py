from pathlib import Path
import copy
import hashlib
import json
import random
import sys
import time
from collections import deque

SOURCE = Path('NEKOMICHI_STAGE_101_200_CANDIDATES.json')
AUDIT = Path('NEKOMICHI_STAGE_101_200_AUDIT_V154.json')
OUTPUT = Path('NEKOMICHI_STAGE_101_200_CANDIDATES_REVISED_V155.json')
REPAIR_STAGES = [
    101, 105, 108, 111, 113, 116, 122,
    131, 133, 134, 135, 136, 142, 146,
    151, 155, 159, 162, 165, 171, 172,
    174, 175, 176, 181, 183, 187, 199,
]
N = 10
MAX_ATTEMPTS_PER_STAGE = 120000


def canonical_regions(regions):
    mapping = {}
    next_id = 0
    normalized = []
    for row in regions:
        normalized_row = []
        for value in row:
            if value not in mapping:
                mapping[value] = next_id
                next_id += 1
            normalized_row.append(mapping[value])
        normalized.append(normalized_row)
    raw = json.dumps(normalized, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def regions_connected(regions):
    for group in range(N):
        cells = {
            (row, col)
            for row in range(N)
            for col in range(N)
            if regions[row][col] == group
        }
        if not cells:
            return False
        start = next(iter(cells))
        seen = {start}
        queue = deque([start])
        while queue:
            row, col = queue.popleft()
            for point in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
                if point in cells and point not in seen:
                    seen.add(point)
                    queue.append(point)
        if seen != cells:
            return False
    return True


def solution_count(regions, limit=2):
    total = 0
    first = None

    def search(row, used_cols, used_groups, previous_col, columns):
        nonlocal total, first
        if total >= limit:
            return
        if row == N:
            total += 1
            if first is None:
                first = columns[:]
            return
        for col in range(N):
            group = regions[row][col]
            if col in used_cols or group in used_groups:
                continue
            if previous_col is not None and abs(col - previous_col) <= 1:
                continue
            search(
                row + 1,
                used_cols | {col},
                used_groups | {group},
                col,
                columns + [col],
            )

    search(0, set(), set(), None, [])
    return total, first


def independent_basic_logic(regions):
    possible = {(row, col) for row in range(N) for col in range(N)}
    cats = set()
    steps = 0

    while len(cats) < N:
        units = []
        for row in range(N):
            units.append(('row', row, {point for point in possible if point[0] == row}))
        for col in range(N):
            units.append(('col', col, {point for point in possible if point[1] == col}))
        for group in range(N):
            units.append((
                'group',
                group,
                {point for point in possible if regions[point[0]][point[1]] == group},
            ))

        hit = None
        for unit_type, key, candidates in units:
            done = (
                (unit_type == 'row' and any(row == key for row, col in cats))
                or (unit_type == 'col' and any(col == key for row, col in cats))
                or (
                    unit_type == 'group'
                    and any(regions[row][col] == key for row, col in cats)
                )
            )
            if not done and len(candidates) == 1:
                hit = next(iter(candidates))
                break

        if hit is None:
            return False, steps

        row, col = hit
        group = regions[row][col]
        cats.add(hit)
        steps += 1
        possible = {
            point
            for point in possible
            if point == hit
            or (
                point[0] != row
                and point[1] != col
                and regions[point[0]][point[1]] != group
                and not (
                    abs(point[0] - row) <= 1
                    and abs(point[1] - col) <= 1
                )
            )
        }

    return True, steps


def make_solution(rng):
    while True:
        columns = list(range(N))
        rng.shuffle(columns)
        if all(abs(columns[row] - columns[row - 1]) > 1 for row in range(1, N)):
            return columns


def make_regions(solution, rng):
    regions = [[-1] * N for _ in range(N)]
    locked_groups = set(rng.sample(range(N), rng.choice([4, 5, 6])))

    for row, col in enumerate(solution):
        regions[row][col] = row

    changed = True
    while changed:
        changed = False
        cells = [
            (row, col)
            for row in range(N)
            for col in range(N)
            if regions[row][col] >= 0 and regions[row][col] not in locked_groups
        ]
        rng.shuffle(cells)
        for row, col in cells:
            empty_neighbors = [
                (next_row, next_col)
                for next_row, next_col in (
                    (row - 1, col), (row + 1, col),
                    (row, col - 1), (row, col + 1),
                )
                if 0 <= next_row < N
                and 0 <= next_col < N
                and regions[next_row][next_col] < 0
            ]
            if empty_neighbors:
                next_row, next_col = rng.choice(empty_neighbors)
                regions[next_row][next_col] = regions[row][col]
                changed = True

    while any(-1 in row for row in regions):
        progress = False
        cells = [(row, col) for row in range(N) for col in range(N) if regions[row][col] < 0]
        rng.shuffle(cells)
        for row, col in cells:
            groups = [
                regions[next_row][next_col]
                for next_row, next_col in (
                    (row - 1, col), (row + 1, col),
                    (row, col - 1), (row, col + 1),
                )
                if 0 <= next_row < N
                and 0 <= next_col < N
                and regions[next_row][next_col] >= 0
            ]
            preferred = [group for group in groups if group not in locked_groups]
            groups = preferred or groups
            if groups:
                regions[row][col] = rng.choice(groups)
                progress = True
        if not progress:
            return None

    return regions


def validate_source(data, audit):
    stages = data.get('stages', [])
    if len(stages) != 100:
        raise RuntimeError(f'source must contain 100 stages, found {len(stages)}')
    if [stage.get('stage') for stage in stages] != list(range(101, 201)):
        raise RuntimeError('source stage numbers must be continuous 101-200')
    audit_failures = sorted(
        detail.get('stage')
        for detail in audit.get('details', [])
        if detail.get('errors')
    )
    if audit_failures != REPAIR_STAGES:
        raise RuntimeError(
            'V154 audit failure list mismatch: '
            + json.dumps(audit_failures, ensure_ascii=False)
        )


def generate_replacement(stage_number, used_layouts):
    rng = random.Random(15500000 + stage_number * 1009)
    started = time.time()

    for attempt in range(1, MAX_ATTEMPTS_PER_STAGE + 1):
        solution = make_solution(rng)
        regions = make_regions(solution, rng)
        if regions is None or not regions_connected(regions):
            continue

        layout_key = canonical_regions(regions)
        if layout_key in used_layouts:
            continue

        count, independent_solution = solution_count(regions, 2)
        if count != 1 or independent_solution != solution:
            continue

        logical_ok, logical_steps = independent_basic_logic(regions)
        if not logical_ok:
            continue

        elapsed = time.time() - started
        print(
            f'REPAIRED: Stage {stage_number} '
            f'attempt={attempt} steps={logical_steps} elapsed={elapsed:.2f}s',
            flush=True,
        )
        return solution, regions, logical_steps, layout_key

    raise RuntimeError(
        f'Stage {stage_number}: no valid replacement found '
        f'within {MAX_ATTEMPTS_PER_STAGE} attempts'
    )


def main():
    if not SOURCE.is_file():
        raise RuntimeError(f'missing source file: {SOURCE.name}')
    if not AUDIT.is_file():
        raise RuntimeError(f'missing audit file: {AUDIT.name}')

    data = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    audit = json.loads(AUDIT.read_text(encoding='utf-8-sig'))
    validate_source(data, audit)

    revised = copy.deepcopy(data)
    stages_by_number = {stage['stage']: stage for stage in revised['stages']}
    original_by_number = {stage['stage']: stage for stage in data['stages']}

    used_layouts = {
        canonical_regions(stage['regions'])
        for stage in revised['stages']
        if stage['stage'] not in REPAIR_STAGES
    }

    for stage_number in REPAIR_STAGES:
        solution, regions, steps, layout_key = generate_replacement(stage_number, used_layouts)
        used_layouts.add(layout_key)

        stage = stages_by_number[stage_number]
        stage['regions'] = regions
        stage['solution'] = solution
        stage['sourcePuzzleStage'] = 'repaired-stage-101-200-v155'
        quality = stage.setdefault('quality', {})
        quality.update({
            'uniqueSolution': True,
            'solutionCount': 1,
            'logicOnly': True,
            'highestRuleLevel': 2,
            'logicalStepCount': steps,
            'assumptionRequired': False,
            'initialCats': 0,
            'repairVersion': 'V155',
            'independentBasicLogicPassed': True,
        })

    unchanged = [
        number
        for number in range(101, 201)
        if number not in REPAIR_STAGES
        and stages_by_number[number] != original_by_number[number]
    ]
    if unchanged:
        raise RuntimeError('non-target stages changed: ' + str(unchanged))

    failures = []
    seen = {}
    for stage in revised['stages']:
        number = stage['stage']
        regions = stage['regions']
        solution = stage['solution']
        key = canonical_regions(regions)
        if key in seen:
            failures.append(f'Stage {number}: duplicate layout with Stage {seen[key]}')
        seen[key] = number
        count, found = solution_count(regions, 2)
        solved, steps = independent_basic_logic(regions)
        if count != 1:
            failures.append(f'Stage {number}: solution count {count}')
        if found != solution:
            failures.append(f'Stage {number}: solution mismatch')
        if not solved:
            failures.append(f'Stage {number}: independent basic logic stalled')
        if not regions_connected(regions):
            failures.append(f'Stage {number}: disconnected region')

    if failures:
        raise RuntimeError('final verification failed: ' + ' | '.join(failures[:20]))

    revised['title'] = 'NEKOMICHI STAGE 101-200 CANDIDATES REVISED V155'
    revised['repair'] = {
        'version': 'V155',
        'source': SOURCE.name,
        'audit': AUDIT.name,
        'repairedStages': REPAIR_STAGES,
        'preservedStages': [
            number for number in range(101, 201) if number not in REPAIR_STAGES
        ],
        'finalIndependentBasicLogicPassed': True,
        'finalUniqueSolutionPassed': True,
    }
    OUTPUT.write_text(
        json.dumps(revised, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    print('OK: V155 repaired all 28 failed Stage 101-200 candidates.')
    print('OK: 72 previously accepted stages were preserved without changes.')
    print('OK: all 100 stages passed unique-solution and independent basic-logic verification.')
    print('OUTPUT: ' + OUTPUT.name)
    print('SEND: Upload only ' + OUTPUT.name + ' to Copilot for the final independent audit.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR: ' + str(exc))
        sys.exit(1)
