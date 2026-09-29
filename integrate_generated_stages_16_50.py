from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
STAGES_FILE = ROOT / "stages.js"
GENERATED_FILE = ROOT / "generated-stages-16-50-python.js"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def find_array_bounds(text: str, variable_name: str) -> tuple[int, int]:
    """Return the [ and ] positions for a JavaScript array assignment."""
    match = re.search(
        rf"\b(?:const|let|var)\s+{re.escape(variable_name)}\s*=\s*\[",
        text,
    )
    if not match:
        fail(f"{variable_name} の配列が見つかりません。")

    start = text.find("[", match.start())
    depth = 0
    in_string: str | None = None
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            continue

        if char in ('"', "'", "`"):
            in_string = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return start, index

    fail(f"{variable_name} の閉じ角括弧が見つかりません。")


def parse_js_array(path: Path, variable_name: str) -> tuple[list[dict], str, int, int]:
    if not path.exists():
        fail(f"{path.name} が見つかりません。プロジェクト直下を確認してください。")

    text = path.read_text(encoding="utf-8-sig")
    start, end = find_array_bounds(text, variable_name)
    raw_array = text[start : end + 1]

    try:
        data = json.loads(raw_array)
    except json.JSONDecodeError as exc:
        fail(
            f"{path.name} の {variable_name} はJSON互換形式ではありません。"
            f" 行{exc.lineno} 列{exc.colno}: {exc.msg}"
        )

    if not isinstance(data, list):
        fail(f"{path.name} の {variable_name} が配列ではありません。")
    if not all(isinstance(item, dict) for item in data):
        fail(f"{path.name} の配列にオブジェクト以外が含まれています。")

    return data, text, start, end


def validate_stage(stage: dict, source: str) -> None:
    required = ("stage", "size", "regions", "solution")
    missing = [key for key in required if key not in stage]
    if missing:
        fail(f"{source} のステージに必須項目がありません: {missing}")

    number = stage["stage"]
    size = stage["size"]
    regions = stage["regions"]
    solution = stage["solution"]

    if not isinstance(number, int) or number < 1:
        fail(f"{source} に不正なステージ番号があります: {number!r}")
    if not isinstance(size, int) or size < 1:
        fail(f"Stage {number}: size が不正です。")
    if not isinstance(regions, list) or len(regions) != size:
        fail(f"Stage {number}: regions の行数が size と一致しません。")
    if any(not isinstance(row, list) or len(row) != size for row in regions):
        fail(f"Stage {number}: regions が {size}x{size} ではありません。")
    if not isinstance(solution, list) or len(solution) != size:
        fail(f"Stage {number}: solution の長さが size と一致しません。")
    if any(not isinstance(column, int) or not 0 <= column < size for column in solution):
        fail(f"Stage {number}: solution に盤面外の列があります。")


def index_by_stage(stages: list[dict], source: str) -> dict[int, dict]:
    indexed: dict[int, dict] = {}
    for stage in stages:
        validate_stage(stage, source)
        number = stage["stage"]
        if number in indexed:
            fail(f"{source} 内で Stage {number} が重複しています。")
        indexed[number] = stage
    return indexed


def main() -> None:
    existing, stages_text, array_start, array_end = parse_js_array(
        STAGES_FILE, "STAGES"
    )
    generated, _, _, _ = parse_js_array(
        GENERATED_FILE, "GENERATED_STAGES"
    )

    existing_map = index_by_stage(existing, STAGES_FILE.name)
    generated_map = index_by_stage(generated, GENERATED_FILE.name)

    generated_numbers = sorted(generated_map)
    expected_generated = list(range(16, 51))
    if generated_numbers != expected_generated:
        missing = sorted(set(expected_generated) - set(generated_numbers))
        extra = sorted(set(generated_numbers) - set(expected_generated))
        fail(
            "生成ファイルは Stage 16-50 の35問である必要があります。"
            f" missing={missing}, extra={extra}"
        )

    required_existing = list(range(1, 16))
    missing_existing = [number for number in required_existing if number not in existing_map]
    if missing_existing:
        fail(f"既存 stages.js に Stage 1-15 がそろっていません: {missing_existing}")

    # Stage 1-15 stays exactly as it is. Stage 16-50 is replaced by generated data.
    merged_map = {
        number: stage
        for number, stage in existing_map.items()
        if number < 16 or number > 50
    }
    merged_map.update(generated_map)
    merged = [merged_map[number] for number in sorted(merged_map)]

    final_numbers = [stage["stage"] for stage in merged if 1 <= stage["stage"] <= 50]
    if final_numbers != list(range(1, 51)):
        fail("統合後の Stage 1-50 が連番になっていません。")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = ROOT / f"backup-before-stages-16-50-integration-{timestamp}"
    backup_dir.mkdir()
    shutil.copy2(STAGES_FILE, backup_dir / STAGES_FILE.name)
    shutil.copy2(GENERATED_FILE, backup_dir / GENERATED_FILE.name)

    rendered_array = json.dumps(merged, ensure_ascii=False, indent=2)
    new_text = (
        stages_text[:array_start]
        + rendered_array
        + stages_text[array_end + 1 :]
    )

    temp_file = ROOT / "stages.js.integration.tmp"
    temp_file.write_text(new_text, encoding="utf-8")

    check = subprocess.run(
        ["node", "--check", str(temp_file)],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        temp_file.unlink(missing_ok=True)
        fail("統合後のJavaScript構文確認に失敗しました。\n" + check.stderr)

    temp_file.replace(STAGES_FILE)

    print("OK: generated-stages-16-50-python.js を stages.js に統合しました。")
    print("維持: Stage 1-15")
    print("追加・置換: Stage 16-50")
    print(f"統合後の総ステージ数: {len(merged)}")
    print(f"Backup: {backup_dir.name}")
    print("構文確認: node --check 合格")


if __name__ == "__main__":
    main()
