#!/bin/bash
set -eu

# weather-music-app/run_generation.sh
DIR="$(cd "$(dirname "$0")" && pwd)"         # weather-music-app のフルパス
REPO_ROOT="$(cd "$DIR/.." && pwd)"           # repo root
CITY="${1:-Tokyo}"
echo "[run_generation] start city=${CITY} (DIR=${DIR} REPO_ROOT=${REPO_ROOT})"

# 必要な実行バイナリ
JAVAC="$(command -v javac || true)"
JAVA="$(command -v java || true)"
PYTHON="$(command -v python3 || command -v python || true)"

if [ -z "$PYTHON" ]; then
  echo "エラー: python3 が見つかりません" >&2
  exit 1
fi

if [ -z "$JAVA" ] || [ -z "$JAVAC" ]; then
  echo "警告: java/javac が見つかりません。JDK が無ければローカルでのJava実行はできません。" >&2
fi

# --- 1) Main.java をコンパイルして実行（Main.java は repo root にある想定） ---
MAIN_SRC="${REPO_ROOT}/Main.java"
if [ ! -f "$MAIN_SRC" ]; then
  echo "エラー: ${MAIN_SRC} が見つかりません" >&2
  exit 1
fi

TMPCLASSDIR="$(mktemp -d)"
echo "[run_generation] Compiling Main.java ..."
javac -encoding UTF-8 -d "$TMPCLASSDIR" "$MAIN_SRC" || { echo "javac failed"; rm -rf "$TMPCLASSDIR"; exit 1; }

# 実行：Main.java は stdin で都市名を受け、標準出力に JSON を出す設計（想定）
echo "[run_generation] Running Main (city via stdin) ..."
# 出力はファイルに保存（後で JSON 部分を抽出）
echo "$CITY" | java -cp "$TMPCLASSDIR" Main > "$TMPCLASSDIR/main_out.txt" 2>&1
RET=$?
if [ $RET -ne 0 ]; then
  echo "Main が異常終了しました (code=${RET})" >&2
  echo "---- Main stdout/stderr ----"
  cat "$TMPCLASSDIR/main_out.txt" >&2
  rm -rf "$TMPCLASSDIR"
  exit $RET
fi

# --- 2) Main の出力から JSON 部分を抽出して chords.json を作る ---
# 探し方は Main の出力フォーマットによる（例: "DEBUG JSON = { ... }" が出る場合を想定）
OUTFILE="${REPO_ROOT}/chords.json"
# Try to find a JSON-looking substring in the output
MAIN_JSON=$(sed -n 's/.*DEBUG JSON = //p' "$TMPCLASSDIR/main_out.txt" | head -n 1 || true)

if [ -z "$MAIN_JSON" ]; then
  # fallback: try to find first line that starts with '{'
  MAIN_JSON=$(sed -n '/^{/,$p' "$TMPCLASSDIR/main_out.txt" | sed -n '1p' || true)
fi

if [ -z "$MAIN_JSON" ]; then
  echo "エラー: Main の出力から JSON を検出できませんでした。出力は下記:" >&2
  cat "$TMPCLASSDIR/main_out.txt" >&2
  rm -rf "$TMPCLASSDIR"
  exit 1
fi

# 保存
echo "$MAIN_JSON" > "$OUTFILE"
echo "[run_generation] chords.json created at ${OUTFILE}:"
head -n 20 "$OUTFILE"

rm -rf "$TMPCLASSDIR"

# --- 3) chords.json に 'season' があるかチェック ---
if ! grep -q '"season"' "$OUTFILE"; then
  echo "エラー: chords.json に 'season' キーがありません" >&2
  cat "$OUTFILE"
  exit 1
fi

# --- 4) Main.py を呼んで最終成果物を作る（必要な環境変数を渡すこと） ---
# 例: CHECKPOINT_PATH を設定してから呼ぶ（もし必要なら）
# export CHECKPOINT_PATH="/path/to/models/cat-mel_2bar_big.ckpt"
echo "[run_generation] Running Main.py ..."
$PYTHON "${REPO_ROOT}/Main.py"
RET2=$?
if [ $RET2 -ne 0 ]; then
  echo "Main.py が異常終了しました (code=${RET2})" >&2
  exit $RET2
fi

echo "[run_generation] finished successfully"
exit 0
