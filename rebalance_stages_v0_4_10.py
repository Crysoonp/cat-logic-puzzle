from __future__ import annotations

import importlib.util
import json
import random
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
STAGES_FILE = ROOT / "stages.js"
GENERATOR_FILE = ROOT / "generate_cat_logic_stages.py"
RESERVE_DIR = ROOT / "stage-reserve"
RESERVE_FILE = RESERVE_DIR / "reserved-stages-before-v0.4.10.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def find_window_array(text: str, name: str) -> tuple[int, int]:
    marker = f"window.{name}="
    pos = text.find(marker)
    if pos < 0:
        marker = f"window.{name} ="
        pos = text.find(marker)
    if pos < 0:
        fail(f"window.{name} が見つかりません。")
    start = text.find("[", pos)
    depth = 0
    quote = None
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'", "`"):
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return start, i
    fail(f"window.{name} の配列終端が見つかりません。")


def load_stages() -> tuple[list[dict], str, int, int]:
    if not STAGES_FILE.exists():
        fail("stages.js が見つかりません。")
    text = STAGES_FILE.read_text(encoding="utf-8-sig")
    start, end = find_window_array(text, "CLP_STAGES")
    try:
        stages = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        fail(f"stages.js を解析できません: 行{exc.lineno} 列{exc.colno} {exc.msg}")
    if len(stages) < 50:
        fail(f"stages.js は50問必要です。現在 {len(stages)}問です。")
    return stages, text, start, end


def load_generator():
    if not GENERATOR_FILE.exists():
        fail("generate_cat_logic_stages.py が見つかりません。")
    spec = importlib.util.spec_from_file_location("clp_generator", GENERATOR_FILE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    required = (
        "make_solution", "make_regions", "adaptive_repair", "find_solutions",
        "logical_solve", "fingerprint", "connected_regions", "make_8x8_seed"
    )
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        fail(f"生成器に必要な関数がありません: {missing}")
    return module


def clone_puzzle(source: dict, new_stage: int) -> dict:
    result = json.loads(json.dumps(source, ensure_ascii=False))
    result["stage"] = new_stage
    result["name"] = f"ステージ{new_stage}"
    result.pop("title", None)
    result.pop("guide", None)
    result["tutorial"] = new_stage <= 9
    result["bonus"] = False
    result["hard"] = new_stage in (10, 20, 30, 40)
    result["specialType"] = (
        "boss" if new_stage == 50 else
        "elite" if new_stage in (20, 30, 40) else
        "graduation" if new_stage == 10 else
        "normal"
    )
    if new_stage <= 9:
        result["chapter"] = "tutorial"
    elif new_stage == 10:
        result["chapter"] = "graduation"
    elif new_stage <= 20:
        result["chapter"] = "chapter-1"
    elif new_stage <= 30:
        result["chapter"] = "chapter-2"
    elif new_stage <= 40:
        result["chapter"] = "chapter-3"
    else:
        result["chapter"] = "lost-forest"
    if new_stage == 50:
        result["bossId"] = "lost-forest-big-cat"
        result["bossPhasePlan"] = [
            {"phase": 1, "label": "50-1", "size": 7},
            {"phase": 2, "label": "50-2", "size": 8},
            {"phase": 3, "label": "50-3", "size": 9},
        ]
        result["bossImplementation"] = "planned"
    return result


def generate_puzzle(gen, size: int, stage_no: int, known: set[str], rng: random.Random) -> dict:
    started = time.time()
    for attempt in range(1, 20001):
        if size == 8:
            stage = gen.make_8x8_seed(50, rng)
        else:
            solution = gen.make_solution(size, rng)
            if solution is None:
                continue
            regions = gen.make_regions(size, solution, rng)
            if regions is None:
                continue
            stage = {
                "stage": stage_no,
                "size": size,
                "name": f"ステージ{stage_no}",
                "difficulty": "自動判定",
                "logicLevel": 0,
                "regions": regions,
                "solution": solution,
            }
        if stage is None or not gen.connected_regions(stage):
            continue
        solutions = gen.find_solutions(stage, 2)
        repair_count = 0
        if len(solutions) > 1:
            stage, repair_count = gen.adaptive_repair(stage, rng)
            if stage is None:
                continue
        if len(gen.find_solutions(stage, 2)) != 1:
            continue
        logic = gen.logical_solve(stage)
        if not logic["solved"] or not 1 <= logic["difficulty"] <= 3:
            continue
        fp = gen.fingerprint(stage)
        if fp in known:
            continue
        known.add(fp)
        stage["quality"] = {
            "uniqueSolution": True,
            "difficulty": logic["difficulty"],
            "difficultyScore": logic["score"],
            "logicOnly": True,
            "logicStepCount": logic["steps"],
            "highestRuleLevel": logic["highest_rule"],
            "solverVersion": "python-1.0.4",
            "adaptiveRepairMoves": repair_count,
        }
        print(
            f"新規 {size}x{size} を Stage {stage_no} 用に生成 | "
            f"試行 {attempt} | 難易度 {logic['difficulty']} | {time.time()-started:.1f}秒",
            flush=True,
        )
        return stage
    fail(f"Stage {stage_no} 用の {size}x{size} を20,000回以内に生成できませんでした。")


def main() -> None:
    stages, original_text, start, end = load_stages()
    gen = load_generator()
    by_no = {stage["stage"]: stage for stage in stages}
    if sorted(n for n in by_no if 1 <= n <= 50) != list(range(1, 51)):
        fail("Stage 1-50 が連番ではありません。")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / f"backup-before-v0.4.10-rebalance-{timestamp}"
    backup.mkdir()
    shutil.copy2(STAGES_FILE, backup / STAGES_FILE.name)
    shutil.copy2(GENERATOR_FILE, backup / GENERATOR_FILE.name)

    reserve = []
    used_sources: set[int] = set()
    new_stages: dict[int, dict] = {}

    def assign(target: int, source: int) -> None:
        used_sources.add(source)
        new_stages[target] = clone_puzzle(by_no[source], target)
        new_stages[target]["sourcePuzzleStage"] = source

    # Tutorial and graduation.
    assign(1, 1); assign(2, 2); assign(3, 3)
    assign(4, 4); assign(5, 5); assign(6, 6)
    assign(7, 16); assign(8, 17); assign(9, 18)
    assign(10, 10)

    # Chapter 1: 6x6. Reuse generated Stage 21-30 puzzles.
    for target, source in zip(range(11, 20), range(21, 30)):
        assign(target, source)

    # Chapter 2: reuse the ten existing 7x7 puzzles for Stage 20-29.
    for target, source in zip(range(20, 30), range(31, 41)):
        assign(target, source)

    # Stage 30-32 and the 7x7 rests at 34 and 36 require fresh unique puzzles.
    # This avoids assigning the same puzzle to two different stage numbers.
    known = {gen.fingerprint(stage) for stage in new_stages.values()}
    rng = random.Random(20260929 + int(time.time()))
    for target in (30, 31, 32):
        fresh = generate_puzzle(gen, 7, target, known, rng)
        new_stages[target] = clone_puzzle(fresh, target)
        new_stages[target]["sourcePuzzleStage"] = "generated-v0.4.10.1"

    # Transition band: alternate fresh 7x7 rests with preserved 8x8 puzzles.
    assign(33, 11)
    for target in (34, 36):
        fresh = generate_puzzle(gen, 7, target, known, rng)
        new_stages[target] = clone_puzzle(fresh, target)
        new_stages[target]["sourcePuzzleStage"] = "generated-v0.4.10.1"
    assign(35, 12)
    assign(37, 13)
    assign(38, 14)
    assign(39, 15)
    assign(40, 41)

    # Lost Forest 41-49: shift existing 8x8 constructed puzzles.
    for target, source in zip(range(41, 50), range(42, 51)):
        assign(target, source)

    # Generate a fresh provisional 8x8 base for Stage 50.
    fresh_50 = generate_puzzle(gen, 8, 50, known, rng)
    new_stages[50] = clone_puzzle(fresh_50, 50)
    new_stages[50]["sourcePuzzleStage"] = "generated-v0.4.10.1"

    # Save every puzzle not used in its original position or no longer assigned.
    for source_no in range(1, 51):
        retained_same = source_no in new_stages and new_stages[source_no].get("sourcePuzzleStage") == source_no
        if not retained_same:
            reserve.append({
                "reserveId": f"R-{by_no[source_no]['size']}x{by_no[source_no]['size']}-{source_no:03d}",
                "originalStage": source_no,
                "reason": "v0.4.10-size-rebalance",
                "puzzle": by_no[source_no],
            })

    final = [new_stages[n] for n in range(1, 51)]
    expected_sizes = {
        **{n: 4 for n in range(1, 4)},
        **{n: 5 for n in range(4, 10)},
        **{n: 6 for n in range(10, 20)},
        **{n: 7 for n in range(20, 33)},
        33: 8, 34: 7, 35: 8, 36: 7, 37: 8, 38: 8, 39: 8, 40: 8,
        **{n: 8 for n in range(41, 51)},
    }
    errors = [f"Stage {s['stage']}={s['size']}x{s['size']} expected {expected_sizes[s['stage']]}" for s in final if s["size"] != expected_sizes[s["stage"]]]
    if errors:
        fail("サイズ検査に失敗しました: " + "; ".join(errors))

    RESERVE_DIR.mkdir(exist_ok=True)
    RESERVE_FILE.write_text(json.dumps(reserve, ensure_ascii=False, indent=2), encoding="utf-8")

    rendered = json.dumps(final, ensure_ascii=False, separators=(",", ":"))
    updated = original_text[:start] + rendered + original_text[end + 1:]
    temp = ROOT / "stages.v0.4.10.check.js"
    temp.write_text(updated, encoding="utf-8")
    result = subprocess.run(["node", "--check", str(temp)], capture_output=True, text=True)
    if result.returncode:
        temp.unlink(missing_ok=True)
        fail("統合後のJavaScript構文確認に失敗しました。\n" + result.stderr)
    temp.replace(STAGES_FILE)

    print("OK: Ver.0.4.10.1 盤面サイズ再編を適用しました。")
    print("構成: 1-3=4x4 / 4-9=5x5 / 10-19=6x6 / 20-32=7x7 / 33以降は移行帯と8x8")
    print(f"予備問題保存: {RESERVE_FILE.relative_to(ROOT)} ({len(reserve)}問)")
    print("Stage 50: 現在は8x8仮盤面。50-1/50-2/50-3の計画メタデータを追加済み。")
    print(f"Backup: {backup.name}")
    print("構文確認: node --check 合格")


if __name__ == "__main__":
    main()
