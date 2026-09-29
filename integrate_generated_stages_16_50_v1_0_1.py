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
    patterns = [
        rf"\b(?:const|let|var)\s+{re.escape(variable_name)}\s*=\s*\[",
        rf"\bwindow\s*\.\s*{re.escape(variable_name)}\s*=\s*\[",
    ]
    match = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            break
    if not match:
        fail(f"{variable_name} の配列が見つかりません。")

    start = text.find("[", match.start())
    depth = 0
    quote = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ('"', "'", "`"):
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return start, index
    fail(f"{variable_name} の閉じ角括弧が見つかりません。")


def parse_js_array(path: Path, variable_name: str):
    if not path.exists():
        fail(f"{path.name} が見つかりません。")
    text = path.read_text(encoding="utf-8-sig")
    start, end = find_array_bounds(text, variable_name)
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        fail(f"{path.name} の配列を解析できません。行{exc.lineno} 列{exc.colno}: {exc.msg}")
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        fail(f"{path.name} の配列形式が不正です。")
    return data, text, start, end


def validate(stage: dict, source: str) -> None:
    for key in ("stage", "size", "regions", "solution"):
        if key not in stage:
            fail(f"{source}: 必須項目 {key} がありません。")
    number, size = stage["stage"], stage["size"]
    if not isinstance(number, int) or not isinstance(size, int) or size < 1:
        fail(f"{source}: ステージ番号またはsizeが不正です。")
    if len(stage["regions"]) != size or any(len(row) != size for row in stage["regions"]):
        fail(f"Stage {number}: regions が {size}x{size} ではありません。")
    if len(stage["solution"]) != size:
        fail(f"Stage {number}: solution の長さが不正です。")
    if any(not isinstance(c, int) or c < 0 or c >= size for c in stage["solution"]):
        fail(f"Stage {number}: solution に盤面外の値があります。")


def build_map(stages: list[dict], source: str) -> dict[int, dict]:
    result = {}
    for stage in stages:
        validate(stage, source)
        number = stage["stage"]
        if number in result:
            fail(f"{source}: Stage {number} が重複しています。")
        result[number] = stage
    return result


def main() -> None:
    existing, original_text, start, end = parse_js_array(STAGES_FILE, "CLP_STAGES")
    generated, _, _, _ = parse_js_array(GENERATED_FILE, "GENERATED_STAGES")

    existing_map = build_map(existing, STAGES_FILE.name)
    generated_map = build_map(generated, GENERATED_FILE.name)

    expected = set(range(16, 51))
    actual = set(generated_map)
    if actual != expected:
        fail(f"生成ファイルはStage 16-50が必要です。missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    if not set(range(1, 16)).issubset(existing_map):
        fail("既存stages.jsにStage 1-15がそろっていません。")

    merged_map = {n: s for n, s in existing_map.items() if n < 16 or n > 50}
    merged_map.update(generated_map)
    merged = [merged_map[n] for n in sorted(merged_map)]
    if [s["stage"] for s in merged if 1 <= s["stage"] <= 50] != list(range(1, 51)):
        fail("統合後のStage 1-50が連番ではありません。")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / f"backup-before-stages-integration-v1.0.1-{stamp}"
    backup.mkdir()
    shutil.copy2(STAGES_FILE, backup / STAGES_FILE.name)
    shutil.copy2(GENERATED_FILE, backup / GENERATED_FILE.name)

    rendered = json.dumps(merged, ensure_ascii=False, separators=(",", ":"))
    updated = original_text[:start] + rendered + original_text[end + 1:]
    temp = ROOT / "stages.integration.check.js"
    temp.write_text(updated, encoding="utf-8")
    check = subprocess.run(["node", "--check", str(temp)], capture_output=True, text=True)
    if check.returncode:
        temp.unlink(missing_ok=True)
        fail("統合後のJavaScript構文確認に失敗しました。\n" + check.stderr)
    temp.replace(STAGES_FILE)

    print("OK: generated-stages-16-50-python.js を stages.js に統合しました。")
    print("配列: window.CLP_STAGES")
    print("維持: Stage 1-15")
    print("追加・置換: Stage 16-50")
    print(f"統合後の総ステージ数: {len(merged)}")
    print(f"Backup: {backup.name}")
    print("構文確認: node --check 合格")


if __name__ == "__main__":
    main()
