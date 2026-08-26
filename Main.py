import json
import glob
import shutil
import subprocess
import sys
import math
import random

import note_seq
from note_seq.protobuf import music_pb2
from note_seq import midi_io


print("最新版Main.py起動")


# ==========================================================
# 設定
# ==========================================================

import os
# 既存の CHECKPOINT = "C:/AI/models/cat-mel_2bar_big.ckpt" を下の行に置換
CHECKPOINT = os.environ.get("CHECKPOINT_PATH", "/app/models/cat-mel_2bar_big.ckpt")

BPM = 90


# ==========================================================
# リズム設定
# ==========================================================

# 数字が大きいほど、そのリズムが選ばれやすい
#
# 1拍   = 4分音符
# 0.5拍 = 8分音符
# 0.25拍 = 16分音符
# 1.5拍 = 付点4分音符
# 2拍   = 2分音符

RHYTHM_WEIGHTS = {

    "quarter": 30,

    "eighth": 30,

    "dotted_eighth": 15,

    "sixteenth": 5,

    "half": 10,

    "dotted_quarter": 10
}

SEASON_RHYTHMS = {

    "春": {

        "quarter": 40,
        "eighth": 40,
        "dotted_eighth": 8,
        "sixteenth": 3,
        "half": 5,
        "dotted_quarter": 4,

        "rest_probability": 0.25,
        "triplet_probability": 0.05
    },

    "夏": {

        "quarter": 15,
        "eighth": 45,
        "dotted_eighth": 10,
        "sixteenth": 25,
        "half": 2,
        "dotted_quarter": 3,

        "rest_probability": 0.10,
        "triplet_probability": 0.10
    },

    "秋": {

        "quarter": 45,
        "eighth": 10,
        "dotted_eighth": 5,
        "sixteenth": 2,
        "half": 8,
        "dotted_quarter": 10,

        "rest_probability": 0.20,
        "triplet_probability": 0.50
    },

    "冬": {

        "quarter": 15,
        "eighth": 15,
        "dotted_eighth": 35,
        "sixteenth": 20,
        "half": 5,
        "dotted_quarter": 10,

        "rest_probability": 0.30,
        "triplet_probability": 0.05
    }
}

# ==========================================================
# 季節別メロディ楽器
# ==========================================================

SEASON_INSTRUMENTS = {

    "春": [0],          # Piano

    "夏": [0, 24],      # Piano / Guitar

    "秋": [0, 71],      # Piano / Clarinet

    "冬": [0, 40]       # Piano / Violin
}

RHYTHM_VALUES = {

    "quarter": 1.0,

    "eighth": 0.5,

    "dotted_eighth": 0.75,

    "sixteenth": 0.25,

    "half": 2.0,

    "dotted_quarter": 1.5
}

# ==========================================================
# リズム選択
# ==========================================================

def choose_rhythm(
    remaining,
    previous_rhythm=None,
    consecutive_sixteenths=0,
    consecutive_long_notes=0,
    dotted_previous=False
):

    candidates = []
    weights = []

    for rhythm_name, weight in CURRENT_RHYTHM_WEIGHTS.items():

        duration = RHYTHM_VALUES[rhythm_name]

        # 残り時間に収まらないものは除外
        if duration > remaining + 0.0001:
            continue

        # ----------------------------------------------
        # 16分音符連続制限
        # ----------------------------------------------

        if rhythm_name == "sixteenth":

            if (
            consecutive_sixteenths
              >= MAX_CONSECUTIVE_SIXTEENTHS
            ):
                continue

        # ----------------------------------------------
        # 2分音符連続制限
        # ----------------------------------------------

        if rhythm_name == "half":

            if (
                consecutive_long_notes
                >= MAX_CONSECUTIVE_LONG_NOTES
            ):
                continue

        # ----------------------------------------------
        # 付点音符の後は細かい音を出やすくする
        # ----------------------------------------------

        adjusted_weight = weight

        if dotted_previous:

            if duration <= 0.5:

                adjusted_weight *= DOTTED_FOLLOWUP_BONUS

        candidates.append(
            rhythm_name
        )

        weights.append(
            adjusted_weight
        )

    # ----------------------------------------------
    # 候補がなくなった場合
    # ----------------------------------------------

    if not candidates:

        return "quarter"

    return random.choices(
        candidates,
        weights=weights,
        k=1
    )[0]

# ==========================================================
# 休符設定
# ==========================================================

# 休符が発生する確率
#
# 0.00 = 休符なし
# 0.10 = 10%
# 0.20 = 20%
# 0.30 = 30%

REST_PROBABILITY = 0.20


# ==========================================================
# 3連符設定
# ==========================================================

# 3連符グループが選ばれる確率
#
# 0.00 = 3連符なし
# 0.10 = 少なめ
# 0.20 = 普通
# 0.30 = やや多め

TRIPLET_PROBABILITY = 0.20

CURRENT_RHYTHM_WEIGHTS = RHYTHM_WEIGHTS.copy()

MELODY_PROGRAM = 0

INSTRUMENT_NAMES = {
    0: "Piano",
    24: "Guitar",
    40: "Violin",
    71: "Clarinet"
}


# ==========================================================
# リズム生成ルール
# ==========================================================

# 16分音符を連続させない
MAX_CONSECUTIVE_SIXTEENTHS = 8

# 2分音符以上を連続させない
MAX_CONSECUTIVE_LONG_NOTES = 1

# 付点音符の後に細かい音を出しやすくする
DOTTED_FOLLOWUP_BONUS = 2.0


# ==========================================================
# 3連符
# ==========================================================

TRIPLET_UNIT = 1.0 / 3.0


# ==========================================================
# 3連符グループを生成
# ==========================================================

def create_triplet_group():

    return [
        TRIPLET_UNIT,
        TRIPLET_UNIT,
        TRIPLET_UNIT
    ]

NOTE_MAP = {
    "C": 60,
    "C#": 61,
    "D": 62,
    "D#": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "G": 67,
    "G#": 68,
    "A": 69,
    "A#": 70,
    "B": 71
}

# ==========================================================
# Key → Scale
# ==========================================================

def key_to_scale(key):

    # メジャースケール
    major_pattern = [
        0, 2, 4, 5, 7, 9, 11
    ]

    # 和声的短音階
    harmonic_minor_pattern = [
        0, 2, 3, 5, 7, 8, 11
    ]

    is_minor = key.endswith("m")

    root_name = (
        key[:-1]
        if is_minor
        else key
    )

    root_pc = (
        NOTE_MAP[root_name]
        % 12
    )

    pattern = (
        harmonic_minor_pattern
        if is_minor
        else major_pattern
    )

    return {
        (
            root_pc + x
        ) % 12
        for x in pattern
    }

# ==========================================================
# スケール拘束
# ==========================================================

def force_scale(
    midi_file,
    key
):

    allowed = key_to_scale(key)

    seq = (
        midi_io
        .midi_file_to_note_sequence(
            midi_file
        )
    )

    for note in seq.notes:

        pitch_class = (
            note.pitch % 12
        )

        if pitch_class in allowed:
            continue

        best_pitch = note.pitch
        best_distance = 999

        for candidate in range(
            note.pitch - 2,
            note.pitch + 3
        ):

            if (
                candidate % 12
                in allowed
            ):

                distance = abs(
                    candidate
                    - note.pitch
                )

                if distance < best_distance:

                    best_distance = distance
                    best_pitch = candidate

        note.pitch = best_pitch

    note_seq.sequence_proto_to_midi_file(
        seq,
        midi_file
    )

# ==========================================================
# コード → 構成音
# ==========================================================

def chord_to_notes(chord):

    if chord.endswith("M7"):

        root_name = chord[:-2]

        root = NOTE_MAP.get(
            root_name,
            60
        )

        return [
            root,
            root + 4,
            root + 7,
            root + 11
        ]

    elif chord.endswith("m7"):

        root_name = chord[:-2]

        root = NOTE_MAP.get(
            root_name,
            60
        )

        return [
            root,
            root + 3,
            root + 7,
            root + 10
        ]

    elif chord.endswith("7"):

        root_name = chord[:-1]

        root = NOTE_MAP.get(
            root_name,
            60
        )

        return [
            root,
            root + 4,
            root + 7,
            root + 10
        ]

    elif chord.endswith("m"):

        root_name = chord[:-1]

        root = NOTE_MAP.get(
            root_name,
            60
        )

        return [
            root,
            root + 3,
            root + 7
        ]

    else:

        root = NOTE_MAP.get(
            chord,
            60
        )

        return [
            root,
            root + 4,
            root + 7
        ]


# ==========================================================
# 最も近いルート音を探す
# ==========================================================

def nearest_root_pitch(
    current_pitch,
    root_pitch
):

    best_pitch = root_pitch
    best_distance = 9999

    for octave in range(-3, 4):

        candidate = (
            root_pitch
            + octave * 12
        )

        distance = abs(
            candidate
            - current_pitch
        )

        if distance < best_distance:

            best_distance = distance
            best_pitch = candidate

    return best_pitch


    # ==========================================================
# フレーズ終端だけコードへ再拘束
# ==========================================================

def reharmonize_phrase_end(
    midi_file,
    chords
):

    print()
    print("==========================================")
    print("フレーズ終端再拘束")
    print("==========================================")

    seq = (
        midi_io
        .midi_file_to_note_sequence(
            midi_file
        )
    )


    melody_notes = [

        note

        for note in seq.notes

        if not note.is_drum
    ]

    if not melody_notes:

        return midi_file

   


    # --------------------------------------
    # 最後の音を取得
    # --------------------------------------

    last_note = max(
        melody_notes,
        key=lambda n: n.start_time
    )

    old_pitch = last_note.pitch

    # --------------------------------------
    # 最終コード
    # --------------------------------------

    last_chord = chords[-1]

    root_pitch = (
        chord_to_notes(
            last_chord
        )[0]
    )

    # --------------------------------------
    # 最も近いルートへ移動
    # --------------------------------------

    new_pitch = nearest_root_pitch(
        old_pitch,
        root_pitch
    )

    last_note.pitch = new_pitch

    print(
        "最終コード:",
        last_chord
    )

    print(
        "終端音:",
        midi_pitch_name(old_pitch),
        "→",
        midi_pitch_name(new_pitch)
    )

    output_file = (
        midi_file.replace(
            ".mid",
            "_reharm.mid"
        )
    )

    note_seq.sequence_proto_to_midi_file(
        seq,
        output_file
    )

    print(
        "再拘束完了:",
        output_file
    )

    return output_file





# ==========================================================
# A.mid / B.mid を作成
# ==========================================================

def create_melody_midi(pattern, bpm):

    print()
    print("==========================================")
    print("MIDI生成")
    print("==========================================")

    seq = music_pb2.NoteSequence()

    seq.ticks_per_quarter = 480

    seq.tempos.add(
        qpm=bpm
    )

    # ======================================================
    # 4/4拍子
    # ======================================================

    BEATS_PER_MEASURE = 4.0

    current_time = 0.0


    previous_pitch = None


    # ======================================================
    # コードごとに処理
    # ======================================================

    for chord_index, chord in enumerate(
        pattern["chords"]
    ):

        notes = chord_to_notes(
            chord
        )

        print()
        print(
            f"Chord {chord_index + 1}:",
            chord,
            "->",
            notes
        )

        # ==================================================
        # このコードが担当する1小節
        # ==================================================

        chord_start = current_time

        chord_end = (
            chord_start
            + BEATS_PER_MEASURE
        )

        rhythm_position = chord_start

        note_number = 0

        # ==================================================
        # リズム状態
        # ==================================================

        previous_rhythm = None

        consecutive_sixteenths = 0

        consecutive_long_notes = 0

        dotted_previous = False

        # ==================================================
        # 1小節の最初かどうか
        # ==================================================

        is_measure_start = True

        # ==================================================
        # リズム生成
        # ==================================================

        while rhythm_position < chord_end - 0.0001:

            remaining = (
                chord_end
                - rhythm_position
            )

            # ==================================================
            # 1拍目は基本的に音を置く
            # ==================================================

            force_note = is_measure_start

            # ==================================================
            # 3連符グループ
            # ==================================================

            triplet_available = (
                remaining >= 1.0 - 0.0001
            )

            use_triplet = False

            if triplet_available:

                if random.random() < TRIPLET_PROBABILITY:

                    use_triplet = True

            # ==================================================
            # 3連符
            # ==================================================

            if use_triplet:

                triplet_values = (
                    create_triplet_group()
                )

                print(
                    "  [3連符グループ]"
                )

                for triplet_index, duration in enumerate(
                    triplet_values
                ):

                    # ------------------------------------------
                    # 3連符の音
                    # ------------------------------------------

                    if previous_pitch is None:

                        pitch = random.choice(notes)

                    else:

                        candidates = []

                        for candidate in notes:

                            if abs(
                                candidate
                                - previous_pitch
                            ) <= 7:

                                candidates.append(
                                    candidate
                                )

                        if candidates:

                            pitch = random.choice(
                                candidates
                            )

                        else:

                            pitch = random.choice(
                                notes
                            )

                    previous_pitch = pitch

                    note = seq.notes.add()

                    note.pitch = pitch

                    note.start_time = round(
                        rhythm_position,
                        6
                    )

                    gate = (
                        duration * 0.90
                    )

                    note.end_time = round(
                        rhythm_position + gate,
                        6
                    )

                    note.velocity = random.randint(
                        75,
                        95
                    )

                    note.instrument = 0
                    note.program = MELODY_PROGRAM

                    # オクターブユニゾン
                    if pitch >= 48:

                        layer = seq.notes.add()

                        layer.pitch = pitch - 12

                        layer.start_time = note.start_time
                        layer.end_time = note.end_time

                        layer.velocity = int(
                            note.velocity * 0.40
                        )

                        layer.instrument = 0
                        layer.program = MELODY_PROGRAM

                    print(
                        f"    triplet "
                        f"{triplet_index + 1}/3"
                        f" / "
                        f"{duration:.3f}拍"
                        f" / "
                        f"{midi_pitch_name(pitch)}"
                    )

                    rhythm_position += duration
                    rhythm_position = round(
                        rhythm_position,
                        6
                    )

                    note_number += 1

                previous_rhythm = "triplet"

                consecutive_sixteenths = 0

                consecutive_long_notes = 0

                dotted_previous = False

                is_measure_start = False

                continue

            # ==================================================
            # 通常リズム
            # ==================================================

            rhythm_name = choose_rhythm(

                remaining,

                previous_rhythm,

                consecutive_sixteenths,

                consecutive_long_notes,

                dotted_previous

            )

            duration = RHYTHM_VALUES[
                rhythm_name
            ]

            # ==================================================
            # 4拍を絶対に超えない
            # ==================================================

            duration = min(
                duration,
                remaining
            )

            # ==================================================
            # 休符判定
            # ==================================================

            use_rest = False

            if not force_note:

                if random.random() < REST_PROBABILITY:

                    use_rest = True

            # ==================================================
            # 休符
            # ==================================================

            if use_rest:

                print(
                    f"  REST"
                    f" / "
                    f"{rhythm_name}"
                    f" / "
                    f"{duration:.2f}拍"
                )

                rhythm_position += duration
                rhythm_position = round(
                    rhythm_position,
                    6
                )

                # ----------------------------------------------
                # 休符は音符の連続状態をリセット
                # ----------------------------------------------

                consecutive_sixteenths = 0

                consecutive_long_notes = 0

                dotted_previous = (
                    rhythm_name
                    in [
                        "dotted_eighth",
                        "dotted_quarter"
                    ]
                )

                previous_rhythm = (
                    rhythm_name + "_rest"
                )

                is_measure_start = False

                continue

            # ==================================================
            # 音符
            # ==================================================


            if previous_pitch is None:

                pitch = random.choice(notes)

            else:

                candidates = []

                for candidate in notes:

                    distance = abs(
                        candidate - previous_pitch
                    )

                    if distance <= 7:

                        candidates.append(
                            candidate
                        )

                if candidates:

                    pitch = random.choice(
                        candidates
                    )
                    

                else:

                    pitch = random.choice(
                        notes
                    )

                if random.random() < 0.15:
                    pitch += 12 

            previous_pitch = pitch


            

            note = seq.notes.add()

            note.pitch = pitch

            note.start_time = round(
                rhythm_position,
                6
            )

            # ==================================================
            # 少しだけ隙間を作る
            # ==================================================

            gate = duration * 0.98
            

            if gate <= 0:

                gate = duration

            note.end_time = round(
                rhythm_position + gate,
                6
            )

            note.velocity = random.randint(
                75,
                95
            )

            note.instrument = 0
            note.program = MELODY_PROGRAM

            # オクターブユニゾン
            if pitch >= 48:

                layer = seq.notes.add()

                layer.pitch = pitch - 12

                layer.start_time = note.start_time
                layer.end_time = note.end_time

                layer.velocity = int(
                    note.velocity * 0.40
                )

                layer.instrument = 0
                layer.program = MELODY_PROGRAM

            # ==================================================
            # ログ
            # ==================================================

            print(
                f"  {rhythm_name}"
                f" / "
                f"{duration:.2f}拍"
                f" / "
                f"{midi_pitch_name(pitch)}"
            )

            # ==================================================
            # 状態更新
            # ==================================================

            if rhythm_name == "sixteenth":

                consecutive_sixteenths += 1

            else:

                consecutive_sixteenths = 0

            # ==================================================
            # 2分音符連続制御
            # ==================================================

            if rhythm_name == "half":

                consecutive_long_notes += 1

            else:

                consecutive_long_notes = 0

            # ==================================================
            # 付点音符判定
            # ==================================================

            dotted_previous = (
                rhythm_name
                in [
                    "dotted_eighth",
                    "dotted_quarter"
                ]
            )

            previous_rhythm = (
                rhythm_name
            )

            # ==================================================
            # 次の音へ
            # ==================================================

            rhythm_position += duration
            rhythm_position = round(
                rhythm_position,
                6
            )

            note_number += 1

            is_measure_start = False

        # ==================================================
        # 4拍ぴったりに補正
        # ==================================================

        rhythm_position = chord_end

        current_time = chord_end

    # ======================================================
    # MIDI全体の長さ
    # ======================================================

    seq.total_time = current_time

    filename = (
        pattern["name"]
        + ".mid"
    )

    note_seq.sequence_proto_to_midi_file(
        seq,
        filename
    )

    print()
    print(
        filename,
        "作成完了"
    )

    print(
        "全体長:",
        f"{seq.total_time:.2f}拍"
    )

# ==========================================================
# MIDI生成
# ==========================================================

def generate_midis():

    with open(
        "chords.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    bpm = data["bpm"]

    for pattern in data["patterns"]:

        create_melody_midi(
            pattern,
            bpm
        )


# ==========================================================
# MIDI解析
# ==========================================================

def midi_pitch_name(pitch):

    NOTE_NAMES = [
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ]

    octave = (pitch // 12) - 1

    name = NOTE_NAMES[
        pitch % 12
    ]

    return f"{name}{octave}"


def analyze_midi(midi_file):

    seq = midi_io.midi_file_to_note_sequence(
        midi_file
    )

    pitches = [
        note.pitch
        for note in seq.notes
        if note.pitch > 0
    ]

    if not pitches:

        raise RuntimeError(
            "MIDIに音符がありません: "
            + midi_file
        )

    min_pitch = min(pitches)
    max_pitch = max(pitches)

    average_pitch = (
        sum(pitches)
        / len(pitches)
    )

    pitch_range = (
        max_pitch
        - min_pitch
    )

    return {
        "file": midi_file,
        "min": min_pitch,
        "max": max_pitch,
        "average": average_pitch,
        "range": pitch_range
    }

# ==========================================================
# コード進行取得
# ==========================================================

def load_pattern_chords():

    with open(
        "chords.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    result = {}

    for pattern in data["patterns"]:

        result[
            pattern["name"]
        ] = pattern["chords"]

    return result


def load_keys():

    with open(
        "chords.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return (
        data["key1"],
        data["key2"]
    )

def load_season():

    with open(
        "chords.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data["season"]

def print_midi_analysis(info):

    print(
        f"{info['file']}"
    )

    print(
        f"  最低音 : "
        f"{info['min']} "
        f"({midi_pitch_name(info['min'])})"
    )

    print(
        f"  最高音 : "
        f"{info['max']} "
        f"({midi_pitch_name(info['max'])})"
    )

    print(
        f"  平均音高 : "
        f"{info['average']:.2f}"
    )

    print(
        f"  音域幅 : "
        f"{info['range']} 半音"
    )


# ==========================================================
# 補間候補選別
# ==========================================================

def select_interpolation_candidates(
    midi1,
    midi2,
    interpolation_dir
):

    print()
    print("==========================================")
    print("補間MIDI解析")
    print("==========================================")

    info1 = analyze_midi(midi1)
    info2 = analyze_midi(midi2)

    print()
    print("【入力1】")
    print_midi_analysis(info1)

    print()
    print("【入力2】")
    print_midi_analysis(info2)

    MIN_TOLERANCE = 5
    MAX_TOLERANCE = 5
    AVERAGE_TOLERANCE = 6
    RANGE_TOLERANCE = 6

    target_min_low = min(
        info1["min"],
        info2["min"]
    ) - MIN_TOLERANCE

    target_min_high = max(
        info1["min"],
        info2["min"]
    ) + MIN_TOLERANCE

    target_max_low = min(
        info1["max"],
        info2["max"]
    ) - MAX_TOLERANCE

    target_max_high = max(
        info1["max"],
        info2["max"]
    ) + MAX_TOLERANCE

    target_average_low = min(
        info1["average"],
        info2["average"]
    ) - AVERAGE_TOLERANCE

    target_average_high = max(
        info1["average"],
        info2["average"]
    ) + AVERAGE_TOLERANCE

    target_range_low = min(
        info1["range"],
        info2["range"]
    ) - RANGE_TOLERANCE

    target_range_high = max(
        info1["range"],
        info2["range"]
    ) + RANGE_TOLERANCE

    interpolation_files = sorted(
        glob.glob(
            interpolation_dir
            + "/*.mid"
        )
    )

    if not interpolation_files:

        raise RuntimeError(
            "補間MIDIが見つかりません: "
            + interpolation_dir
        )

    accepted_files = []

    for midi_file in interpolation_files:

        info = analyze_midi(
            midi_file
        )

        min_ok = (
            target_min_low
            <= info["min"]
            <= target_min_high
        )

        max_ok = (
            target_max_low
            <= info["max"]
            <= target_max_high
        )

        average_ok = (
            target_average_low
            <= info["average"]
            <= target_average_high
        )

        range_ok = (
            target_range_low
            <= info["range"]
            <= target_range_high
        )

        ok_count = sum([
            min_ok,
            max_ok,
            average_ok,
            range_ok
        ])

        accepted = (
            ok_count >= 3
        )

        print()
        print(
            midi_file
        )

        print(
            f"  最低音   : "
            f"{info['min']} "
            f"{'○' if min_ok else '×'}"
        )

        print(
            f"  最高音   : "
            f"{info['max']} "
            f"{'○' if max_ok else '×'}"
        )

        print(
            f"  平均音高 : "
            f"{info['average']:.2f} "
            f"{'○' if average_ok else '×'}"
        )

        print(
            f"  音域幅   : "
            f"{info['range']} 半音 "
            f"{'○' if range_ok else '×'}"
        )

        print(
            f"  判定     : "
            f"{ok_count}/4 "
            f"{'採用' if accepted else '除外'}"
        )

        if accepted:

            accepted_files.append(
                midi_file
            )

    if not accepted_files:

        print(
            "全候補が除外されたため、"
            "最も近い候補を採用します。"
        )

        best_file = None
        best_score = float("inf")

        for midi_file in interpolation_files:

            info = analyze_midi(
                midi_file
            )

            score = (

                abs(
                    info["min"]
                    - (
                        info1["min"]
                        + info2["min"]
                    ) / 2
                )

                +

                abs(
                    info["max"]
                    - (
                        info1["max"]
                        + info2["max"]
                    ) / 2
                )

                +

                abs(
                    info["average"]
                    - (
                        info1["average"]
                        + info2["average"]
                    ) / 2
                )
            )

            if score < best_score:

                best_score = score
                best_file = midi_file

        accepted_files.append(
            best_file
        )

    print()
    print("採用された補間MIDI:")

    for midi_file in accepted_files:

        print(
            "  ",
            midi_file
        )

    return accepted_files

# ==========================================================
# A/Bそれぞれから「Best MIDI」を選ぶ
# ==========================================================

def select_best_from_midi(
    original_midi,
    candidate_dir
):

    print()
    print("==========================================")
    print("Best MIDI選択")
    print("==========================================")

    original_info = analyze_midi(
        original_midi
    )

    print()
    print("基準MIDI:")
    print_midi_analysis(
        original_info
    )

    candidates = sorted(
        glob.glob(
            candidate_dir
            + "/*.mid"
        )
    )

    if not candidates:

        raise RuntimeError(
            "候補MIDIがありません: "
            + candidate_dir
        )

    best_file = None
    best_score = float("inf")

    for midi_file in candidates:

        info = analyze_midi(
            midi_file
        )

        # --------------------------------------
        # A/B元音源との音域差を計算
        # --------------------------------------

        score = (
            abs(
                info["min"]
                - original_info["min"]
            )
            +
            abs(
                info["max"]
                - original_info["max"]
            )
            +
            abs(
                info["average"]
                - original_info["average"]
            )
        )

        print()
        print(
            midi_file
        )

        print(
            f"  最低音   : {info['min']}"
        )

        print(
            f"  最高音   : {info['max']}"
        )

        print(
            f"  平均音高 : "
            f"{info['average']:.2f}"
        )

        print(
            f"  距離スコア : "
            f"{score:.2f}"
        )

        if score < best_score:

            best_score = score
            best_file = midi_file

    print()
    print("==========================================")
    print("Best MIDI決定")
    print("==========================================")

    print(
        "元MIDI:",
        original_midi
    )

    print(
        "Best:",
        best_file
    )

    print(
        "Score:",
        best_score
    )

    return best_file

# ==========================================================
# MusicVAE入力抽出
# ==========================================================

def extract_midi(
    midi_file,
    extract_dir
):

    print(
        "入力MIDI抽出開始:",
        midi_file
    )

    shutil.rmtree(
        extract_dir,
        ignore_errors=True
    )

    cmd = [

        sys.executable,

        "-m",
        "magenta.models.music_vae.music_vae_generate",

        "--config=cat-mel_2bar_big",

        "--checkpoint_file="
        + CHECKPOINT,

        "--input_midi_1="
        + midi_file,

        "--output_dir="
        + extract_dir
    ]

    result = subprocess.run(
        cmd
    )

    print(
        "抽出 return code =",
        result.returncode
    )

    if result.returncode != 0:

        raise RuntimeError(
            "MusicVAE入力抽出失敗: "
            + midi_file
        )

    extracted_files = sorted(
        glob.glob(
            extract_dir
            + "/cat-mel_2bar_big_sample_*-of-005.mid"
        )
    )

    if not extracted_files:

        raise RuntimeError(
            "MusicVAE用入力MIDIがありません: "
            + midi_file
        )

    selected = extracted_files[0]

    print(
        "使用する候補:",
        selected
    )

    return selected

# ==========================================================
# A/BのBest MIDIを作成
# ==========================================================

def create_best_midis():

    print()
    print("==========================================")
    print("A/B Best MIDI作成")
    print("==========================================")

    # --------------------------------------
    # A.midから候補を生成
    # --------------------------------------

    a_dir = "A_candidates"

    shutil.rmtree(
        a_dir,
        ignore_errors=True
    )

    cmd_a = [
        sys.executable,
        "-m",
        "magenta.models.music_vae.music_vae_generate",

        "--config=cat-mel_2bar_big",

        "--checkpoint_file="
        + CHECKPOINT,

        "--input_midi_1=A.mid",

        "--num_outputs=5",

        "--output_dir="
        + a_dir
    ]

    result_a = subprocess.run(
        cmd_a
    )

    if result_a.returncode != 0:

        raise RuntimeError(
            "A.midのBest候補生成に失敗"
        )

    # --------------------------------------
    # B.midから候補を生成
    # --------------------------------------

    b_dir = "B_candidates"

    shutil.rmtree(
        b_dir,
        ignore_errors=True
    )

    cmd_b = [
        sys.executable,
        "-m",
        "magenta.models.music_vae.music_vae_generate",

        "--config=cat-mel_2bar_big",

        "--checkpoint_file="
        + CHECKPOINT,

        "--input_midi_1=B.mid",

        "--num_outputs=5",

        "--output_dir="
        + b_dir
    ]

    result_b = subprocess.run(
        cmd_b
    )

    if result_b.returncode != 0:

        raise RuntimeError(
            "B.midのBest候補生成に失敗"
        )

    # --------------------------------------
    # Bestを選択
    # --------------------------------------

    a_best = select_best_from_midi(
        "A.mid",
        a_dir
    )

    b_best = select_best_from_midi(
        "B.mid",
        b_dir
    )

    print()
    print("A_best =", a_best)
    print("B_best =", b_best)

    return (
        a_best,
        b_best
    )


# ==========================================================
# コード進行提示用MIDI
# ==========================================================

def create_chord_reference_midi(
    chords
):

    pattern = {
        "name": "A_CODE",
        "chords": chords
    }

    create_melody_midi(
        pattern,
        BPM
    )

    return "A_CODE.mid"
# ==========================================================
# MusicVAE補間
# ==========================================================

def interpolate(
    midi1,
    midi2,
    outdir
):

    print()
    print("==========================================")
    print("MusicVAE補間開始")
    print("==========================================")

    extract_dir1 = (
        outdir
        + "_input1"
    )

    extract_dir2 = (
        outdir
        + "_input2"
    )

    extracted1 = extract_midi(
        midi1,
        extract_dir1
    )

    extracted2 = extract_midi(
        midi2,
        extract_dir2
    )

    shutil.rmtree(
        outdir,
        ignore_errors=True
    )

    cmd = [

        sys.executable,

        "-m",
        "magenta.models.music_vae.music_vae_generate",

        "--config=cat-mel_2bar_big",

        "--checkpoint_file="
        + CHECKPOINT,

        "--mode=interpolate",

        "--input_midi_1="
        + extracted1,

        "--input_midi_2="
        + extracted2,

        "--num_outputs=5",

        "--output_dir="
        + outdir
    ]

    result = subprocess.run(
        cmd
    )

    print(
        "return code =",
        result.returncode
    )

    if result.returncode != 0:

        raise RuntimeError(
            "MusicVAE補間失敗"
        )

    print(
        "補間完了"
    )

    selected = (
        select_interpolation_candidates(
            midi1,
            midi2,
            outdir
        )
    )

    return selected


# ==========================================================
# MIDI連結
# ==========================================================

def append_sequence(
    merged,
    seq,
    current_time,
    label=""
):

    print()
    print("==========================================")
    print("連結データ確認")
    print("==========================================")

    pitches_before = []

    for note in seq.notes:

        if note.is_drum:
            continue

        if note.pitch > 0:
            pitches_before.append(
                note.pitch
            )

        new_note = merged.notes.add()

        # --------------------------------------
        # 音高を完全にそのままコピー
        # --------------------------------------

        new_note.pitch = note.pitch

        new_note.velocity = note.velocity

        new_note.instrument = note.instrument

        new_note.program = note.program

        new_note.is_drum = note.is_drum

        new_note.start_time = (
            note.start_time
            + current_time
        )

        new_note.end_time = (
            note.end_time
            + current_time
        )

    if pitches_before:

        print(
            "セクション:",
            label
        )

        print(
            "開始時刻:",
            current_time
        )

        print(
            "最低音:",
            min(pitches_before),
            midi_pitch_name(
                min(pitches_before)
            )
        )

        print(
            "最高音:",
            max(pitches_before),
            midi_pitch_name(
                max(pitches_before)
            )
        )

        print(
            "平均音高:",
            f"{sum(pitches_before) / len(pitches_before):.2f}"
        )

    return (
        current_time
        + seq.total_time
    )


# ==========================================================
# 最終MIDI作成
# ==========================================================

# ==========================================================
# MIDI連結
# ==========================================================

def merge_all(
    a_best,
    a_code,
    b_best,
    selected_a_code,
    selected_code_b
):
    print()
    print("==========================================")
    print("MIDI連結開始")
    print("==========================================")

    merged = (
        music_pb2.NoteSequence()
    )

    merged.tempos.add(
        qpm=BPM
    )

    current_time = 0.0

    # ======================================================
    # 最終構成
    # ======================================================
    structure = []

    structure.append(
        ("A_best", a_best)
    )

    for i, midi_file in enumerate(
        selected_a_code,
        start=1
    ):
        structure.append(
            (
                f"A_CODE_INTERP_{i}",
                midi_file
            )
        )

    structure.append(
        (
            "A_CODE",
            a_code
        )
    )

    for i, midi_file in enumerate(
        selected_code_b,
        start=1
    ):
        structure.append(
            (
                f"CODE_B_INTERP_{i}",
                midi_file
            )
        )

    structure.append(
        (
            "B_best",
            b_best
        )
    )



    print()
    print("最終連結順:")

    for i, (
        label,
        midi_file
    ) in enumerate(
        structure,
        start=1
    ):

        print(
            f"  {i}. {label}"
        )

        print(
            f"     {midi_file}"
        )

    # ======================================================
    # 連結
    # ======================================================

    for label, midi_file in structure:

        print()
        print("------------------------------------------")
        print(
            "連結中:",
            label
        )



        print(
            midi_file
        )

        seq = (
            midi_io
            .midi_file_to_note_sequence(
                midi_file
            )
        )

        print(
            "Length:",
            seq.total_time
        )

        # --------------------------------------
        # 連結前の音域を確認
        # --------------------------------------

        pitches = [

            note.pitch

            for note in seq.notes

            if (
                note.pitch > 0
                and not note.is_drum
            )
        ]

        if pitches:

            print(
                "連結前:"
            )

            print(
                "  最低音:",
                min(pitches),
                midi_pitch_name(
                    min(pitches)
                )
            )

            print(
                "  最高音:",
                max(pitches),
                midi_pitch_name(
                    max(pitches)
                )
            )

            print(
                "  平均:",
                f"{sum(pitches) / len(pitches):.2f}"
            )

        # --------------------------------------
        # 実際にコピー
        # --------------------------------------

        current_time = append_sequence(

            merged,

            seq,

            current_time,

            label

        )

    # ======================================================
    # Final.mid
    # ======================================================

    merged.total_time = current_time

    note_seq.sequence_proto_to_midi_file(

        merged,

        "Final.mid"

    )

    print()
    print("==========================================")
    print("Final.mid 作成完了")
    print("==========================================")

    # ======================================================
    # Final.midを書き出した後、再度読み込んで確認
    # ======================================================

    final_seq = (
        midi_io
        .midi_file_to_note_sequence(
            "Final.mid"
        )
    )

    final_pitches = [

        note.pitch

        for note in final_seq.notes

        if (
            note.pitch > 0
            and not note.is_drum
        )
    ]

    if final_pitches:

        print()
        print("Final.mid全体確認")

        print(
            "最低音:",
            min(final_pitches),
            midi_pitch_name(
                min(final_pitches)
            )
        )

        print(
            "最高音:",
            max(final_pitches),
            midi_pitch_name(
                max(final_pitches)
            )
        )

        print(
            "平均音高:",
            f"{sum(final_pitches) / len(final_pitches):.2f}"
        )

        print(
            "音域幅:",
            max(final_pitches)
            - min(final_pitches),
            "半音"
        )

    return "Final.mid"

# ==========================================================
# ここから編曲
# ==========================================================

def get_root_pitch(
    pitches
):

    if not pitches:

        return 60

    # 最低音を基本的なルート候補として利用
    root = min(pitches)

    # ベース用に低い音域へ
    while root > 48:

        root -= 12

    while root < 36:

        root += 12

    return root


# ==========================================================
# ベース
# ==========================================================

def add_bass(
    seq,
    start,
    end,
    root
):

    bass = seq.notes.add()

    bass.pitch = root

    bass.start_time = start

    bass.end_time = end

    bass.velocity = 65

    bass.instrument = 1

    bass.program = 32


# ==========================================================
# ストリングスパッド
# ==========================================================

def add_pad(
    seq,
    start,
    end,
    root
):

    # 5度
    pad1 = seq.notes.add()

    pad1.pitch = (
        root
        + 24
    )

    pad1.start_time = start

    pad1.end_time = end

    pad1.velocity = 28

    pad1.instrument = 2

    pad1.program = 48


    # 3度/5度系の音
    pad2 = seq.notes.add()

    pad2.pitch = (
        root
        + 31
    )

    pad2.start_time = start

    pad2.end_time = end

    pad2.velocity = 25

    pad2.instrument = 2

    pad2.program = 48


# ==========================================================
# ドラム
# ==========================================================

def add_drums(
    seq,
    start,
    measure_length
):

    beat = 0

    while beat < measure_length:

        # Hi-Hat
        hat = seq.notes.add()

        hat.pitch = 42

        hat.start_time = (
            start + beat
        )

        hat.end_time = (
            start
            + beat
            + 0.08
        )

        hat.velocity = 40

        hat.instrument = 9

        hat.is_drum = True


        # Kick
        if beat % 2 == 0:

            kick = seq.notes.add()

            kick.pitch = 36

            kick.start_time = (
                start + beat
            )

            kick.end_time = (
                start
                + beat
                + 0.08
            )

            kick.velocity = 55

            kick.instrument = 9

            kick.is_drum = True


        # Snare
        else:

            snare = seq.notes.add()

            snare.pitch = 38

            snare.start_time = (
                start + beat
            )

            snare.end_time = (
                start
                + beat
                + 0.08
            )

            snare.velocity = 45

            snare.instrument = 9

            snare.is_drum = True

        beat += 1


# ==========================================================
# 自動編曲
# ==========================================================

def add_arrangement(
    input_file
):

    print()
    print("==========================================")
    print("自動編曲開始")
    print("==========================================")

    seq = (
        midi_io
        .midi_file_to_note_sequence(
            input_file
        )
    )

    original_notes = []

    for note in seq.notes:

        # ドラムなどを除外
        if note.is_drum:

            continue

        original_notes.append(
            note
        )

    # 4拍を1小節として扱う
    measure_length = 4.0

    current = 0.0

    while current < seq.total_time:

        measure_end = (
            current
            + measure_length
        )

        pitches = []

        for note in original_notes:

            if (
                current
                <= note.start_time
                < measure_end
            ):

                pitches.append(
                    note.pitch
                )

        if pitches:

            root = get_root_pitch(
                pitches
            )

            print(
                f"小節 {current:.2f}"
                f" → root = "
                f"{midi_pitch_name(root)}"
            )

            # --------------------------
            # Bass
            # --------------------------

            add_bass(
                seq,
                current,
                measure_end,
                root
            )

            # --------------------------
            # Strings
            # --------------------------

            add_pad(
                seq,
                current,
                measure_end,
                root
            )

            # --------------------------
            # Drums
            # --------------------------

            add_drums(
                seq,
                current,
                measure_length
            )

        current += measure_length

    # ======================================================
    # 最後に少し余韻を作る
    # ======================================================

    if original_notes:

        last_pitch = (
            original_notes[-1].pitch
        )

        final_root = get_root_pitch(
            [last_pitch]
        )

        tail_start = (
            seq.total_time
        )

        tail_end = (
            seq.total_time
            + 2.0
        )

        add_bass(
            seq,
            tail_start,
            tail_end,
            final_root
        )

        add_pad(
            seq,
            tail_start,
            tail_end,
            final_root
        )

        seq.total_time = (
            tail_end
        )

    note_seq.sequence_proto_to_midi_file(
        seq,
        "Final_arranged.mid"
    )

    print(
        "Final_arranged.mid 作成完了"
    )


# ==========================================================
# メイン
# ==========================================================

if __name__ == "__main__":

    print("処理開始")

    season = load_season()

    print(
        "季節リズム:",
        season
    )

    CURRENT_RHYTHM_WEIGHTS = (
        SEASON_RHYTHMS[season].copy()
    )

    REST_PROBABILITY = (
        CURRENT_RHYTHM_WEIGHTS.pop(
            "rest_probability"
        )
    )

    TRIPLET_PROBABILITY = (
        CURRENT_RHYTHM_WEIGHTS.pop(
            "triplet_probability"
        )
    )

    MELODY_PROGRAM = random.choice(
        SEASON_INSTRUMENTS[season]
    )

    print(
        "メロディ楽器:",
        INSTRUMENT_NAMES[MELODY_PROGRAM]
    )


    # ------------------------------------------------------
    # 1. A.mid / B.mid作成
    # ------------------------------------------------------

    generate_midis()

    # ------------------------------------------------------
    # 2. A → B 補間
    # ------------------------------------------------------

    a_best, b_best = create_best_midis()

    patterns = load_pattern_chords()

    key1, key2 = load_keys()

  

    a_best = reharmonize_phrase_end(
        a_best,
        patterns["A"]
    )

    force_scale(
        a_best,
        key1
    )

    a_code = create_chord_reference_midi(
        patterns["A"]
    )

    b_best = reharmonize_phrase_end(
        b_best,
        patterns["B"]
    )

    force_scale(
        b_best,
        key1
    )



    selected_a_code = interpolate(
        a_best,
        a_code,
        "a_code_interp"
    )

    for midi_file in selected_a_code:

        force_scale(
            midi_file,
            key1
        )
    selected_code_b = interpolate(
        a_code,
        b_best,
        "code_b_interp"
    )

    for midi_file in selected_code_b:

        force_scale(
            midi_file,
            key1
        )

    # ------------------------------------------------------
    # 3. A_best → 補間 → B_best を連結
    # ------------------------------------------------------
    merge_all(
        a_best,
        a_code,
        b_best,
        selected_a_code,
        selected_code_b
    )

    # ------------------------------------------------------
    # 4. 完成した曲を自動編曲
    # ------------------------------------------------------



    add_arrangement(
            "../weather_music_ui/final_arranged.mid"
    )




    print()
    print("==========================================")
    print("全処理完了")
    print("==========================================")
