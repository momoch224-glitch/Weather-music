#!/bin/bash
set -eu

# weather-music-app/run_generation.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$DIR"
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

# --- 1) Main.java をコンパイルして実行 ---
MAIN_SRC="${REPO_ROOT}/Main.java"
if [ ! -f "$MAIN_SRC" ]; then
  echo "エラー: ${MAIN_SRC} が見つかりません" >&2
  exit 1
fi

TMPCLASSDIR="$(mktemp -d)"
echo "[run_generation] Compiling Main.java ..."
javac -encoding UTF-8 -d "$TMPCLASSDIR" "$MAIN_SRC" || { echo "javac failed"; rm -rf "$TMPCLASSDIR"; exit 1; }

echo "[run_generation] Running Main (city via stdin) ..."
echo "$CITY" | java -cp "$TMPCLASSDIR" Main > "$TMPCLASSDIR/main_out.txt" 2>&1
RET=$?
if [ $RET -ne 0 ]; then
  echo "Main が異常終了しました (code=${RET})" >&2
  cat "$TMPCLASSDIR/main_out.txt" >&2
  rm -rf "$TMPCLASSDIR"
  exit $RET
fi

# ★Main.javaが自分で chords.json を作るので、抽出・上書き処理は削除しました！
rm -rf "$TMPCLASSDIR"

OUTFILE="${REPO_ROOT}/chords.json"

# --- 2) Main.py を呼んで最終成果物を作る ---
echo "[run_generation] Running Main.py ..."
$PYTHON "${REPO_ROOT}/Main.py"
RET2=$?
if [ $RET2 -ne 0 ]; then
  echo "Main.py が異常終了しました (code=${RET2})" >&2
  exit $RET2
fi

echo "[run_generation] finished successfully"
exit 0