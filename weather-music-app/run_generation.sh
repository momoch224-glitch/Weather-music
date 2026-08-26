#!/bin/bash
set -eu

# run_generation.sh は weather-music-app ディレクトリに置く想定。
# このスクリプトがある場所を基準にリポジトリのルートを決める（Main2.java 等がルートにある想定）
DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$DIR/.." && pwd)"   # weather-music-app の一つ上が repo root

CITY="${1:-Tokyo}"
echo "[run_generation] start city=${CITY}"
echo "[run_generation] DIR=${DIR} REPO_ROOT=${REPO_ROOT}"

# 1) weather.py を呼んで chords.json を生成する
#    weather.py は JavaPython ディレクトリ内にある想定
PYTHON_CMD="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON_CMD" ]; then
  echo "エラー: python3 が見つかりません" >&2
  exit 1
fi

# CHORDS_PATH を明確に指定（リポジトリルートに chords.json を生成）
export CHORDS_PATH="${REPO_ROOT}/chords.json"

echo "[run_generation] calling weather.py to create ${CHORDS_PATH}"
$PYTHON_CMD "${REPO_ROOT}/JavaPython/weather.py" "${CITY}"
RET=$?
if [ $RET -ne 0 ]; then
  echo "weather.py が異常終了しました (code=${RET})" >&2
  exit $RET
fi

# 2) chords.json の存在と season をチェック
if [ ! -f "${CHORDS_PATH}" ]; then
  echo "エラー: ${CHORDS_PATH} が見つかりません" >&2
  exit 1
fi

# 簡易に 'season' があるかを確認
if ! grep -q '"season"' "${CHORDS_PATH}"; then
  echo "エラー: chords.json に 'season' キーがありません" >&2
  cat "${CHORDS_PATH}"
  exit 1
fi

echo "[run_generation] chords.json generated: $(head -n 20 "${CHORDS_PATH}")"

# 3) Main.py を実行して final_arranged.mid 等を作る
#    Main.py はリポジトリルートにある想定（もし別フォルダならパスを合わせてください）
echo "[run_generation] running Main.py ..."
$PYTHON_CMD "${REPO_ROOT}/Main.py"
RET2=$?
if [ $RET2 -ne 0 ]; then
  echo "Main.py が異常終了しました (code=${RET2})" >&2
  exit $RET2
fi

echo "[run_generation] finished successfully"
exit 0
