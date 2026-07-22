import json
import glob
import shutil
import subprocess
import sys
import random

import note_seq
from note_seq.protobuf import music_pb2
from note_seq import midi_io

print("最新版Main.py起動")

CHECKPOINT = "C:/AI/models/cat-mel_2bar_big.ckpt"

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
RHYTHM_LIBRARY = {

    "whole":              4.0,
    "dotted_half":        3.0,
    "half":               2.0,
    "dotted_quarter":     1.5,
    "quarter":            1.0,
    "dotted_eighth":      0.75,
    "eighth":             0.5,
    "sixteenth":          0.25,

    "whole_rest":         -4.0,
    "dotted_half_rest":   -3.0,
    "half_rest":          -2.0,
    "dotted_quarter_rest":-1.5,
    "quarter_rest":       -1.0,
    "dotted_eighth_rest": -0.75,
    "eighth_rest":        -0.5,
    "sixteenth_rest":     -0.25,

    "triplet":            1.0 / 3.0
}

def generate_one_bar(seasoon):
    remaining_beats = 4.0

    rhythm_list = []

    while remaining_beats > 0:

        candidates = {}

        for rhythm_name,duration in RHYTHM_LIBRARY.items():

            if duration <= remaining_beats:

                candidates[rhythm_name] = (RHYTHM_WEIght[season][rhythm_name])

        rhythm_name -list(candidates.keys() )
        thm_weights = list(candidates.values())

        selected_rhythm = random.chooices(rhythm_names,weights=rhythm_weights,k=1)[0]

        duration = RHYTHM_LIBRARY[selected_rhythm]

        rhythm_list.apppend(selected_rhythm)

        remaining_beats -= duration 

    return rhythm_list

RHYTHM_WEIGHT = {

    "春": {
        #八分音符/付点八分音符
        "whole":10,
        "dotted_half":15,
        "half":20,
        "dotted_quarter":20,
        "quarter":20,
        "dotted_eighth":40,
        "eighth":40,
        "sixteenth":25,
        "whole_rest":2,
        "dotted_half_rest":5,
        "half_rest":5,
        "dotted_quarter_rest":7,
        "quarter_rest":7,
        "dotted_eighth_rest":10,
        "eighth_rest":10,
        "sixteenth_rest":10,
        "triplet":20
    },

    "夏": {
        #四分音符/付点四分音符
        "whole":10,
        "dotted_half":15,
        "half":20,
        "dotted_quarter":40,
        "quarter":40,
        "dotted_eighth":20,
        "eighth":20,
        "sixteenth":20,
        "whole_rest":2,
        "dotted_half_rest":5,
        "half_rest":5,
        "dotted_quarter_rest":7,
        "quarter_rest":7,
        "dotted_eighth_rest":10,
        "eighth_rest":10,
        "sixteenth_rest":10,
        "triplet":20
    },

    "秋": {
        #四分音符/三連符
        "whole":10,
        "dotted_half":15,
        "half":20,
        "dotted_quarter":20,
        "quarter":40,
        "dotted_eighth":20,
        "eighth":20,
        "sixteenth":20,
        "whole_rest":2,
        "dotted_half_rest":5,
        "half_rest":5,
        "dotted_quarter_rest":7,
        "quarter_rest":7,
        "dotted_eighth_rest":10,
        "eighth_rest":10,
        "sixteenth_rest":10,
        "triplet":40
    },

    "冬": {
        #四分音符/八分音符
        "whole":10,
        "dotted_half":15,
        "half":20,
        "dotted_quarter":20,
        "quarter":40,
        "dotted_eighth":20,
        "eighth":40,
        "sixteenth":20,
        "whole_rest":2,
        "dotted_half_rest":5,
        "half_rest":5,
        "dotted_quarter_rest":7,
        "quarter_rest":7,
        "dotted_eighth_rest":10,
        "eighth_rest":10,
        "sixteenth_rest":10,
        "triplet":20
    }

}
def choose_rhythm(season):
    weights = RHYTHM_WEIGHT[season]

    rhythm_names = list(weights.keys())

    rhythm_weights = list(weights.values())

    selected_rhythm = random.choices(rhythm_names,weights=rhythm_weights,k=1)[0]

    return selected_rhythm



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


def create_melody_midi(pattern, bpm):

    seq = music_pb2.NoteSequence()

    seq.ticks_per_quarter = 220

    seq.tempos.add(
        qpm=bpm
    )

    note_index = 0

    for chord in pattern["chords"]:

        notes = chord_to_notes(
            chord
        )

        print(
            chord,
            "->",
            notes
        )

        for pitch in notes:

            note = seq.notes.add()

            note.pitch = pitch

            start = note_index * 0.5
            end = start + 0.45

            note.start_time = start
            note.end_time = end

            note.velocity = 90

            note_index += 1

    seq.total_time = note_index * 0.5

    filename = (
        pattern["name"]
        + ".mid"
    )

    note_seq.sequence_proto_to_midi_file(
        seq,
        filename
    )

    print(
        filename,
        "作成完了"
    )

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


def interpolate(midi1, midi2, outdir):

    print(
        "補間開始:",
        midi1,
        "→",
        midi2
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
        "--checkpoint_file=" + CHECKPOINT,
        "--mode=interpolate",
        "--input_midi_1=" + midi1,
        "--input_midi_2=" + midi2,
        "--num_outputs=5",
        "--output_dir=" + outdir
    ]

    result = subprocess.run(cmd)

    print(
        "return code =",
        result.returncode
    )

    if result.returncode != 0:

        raise RuntimeError(
            "MusicVAE失敗"
        )


def append_sequence(
    merged,
    seq,
    current_time
):

    for note in seq.notes:

        new_note = merged.notes.add()

        new_note.pitch = note.pitch
        new_note.velocity = note.velocity

        new_note.start_time = (
            note.start_time
            + current_time
        )

        new_note.end_time = (
            note.end_time
            + current_time
        )

    return (
        current_time
        + seq.total_time
    )

def merge_all():

    print("連結開始")

    merged = music_pb2.NoteSequence()

    merged.tempos.add(
        qpm=90
    )

    current_time = 0.0

    structure = [

        ("A.mid", False),

        ("ab_interp", True),

        ("B.mid", False),

        ("bc_interp", True),
        ("C.mid", False),

        ("cd_interp", True),
        ("D.mid", False),

        ("de_interp", True),
        ("E.mid", False)
    ]

    for item, is_folder in structure:

        if is_folder:

            mids = sorted(
                glob.glob(
                    item + "/*.mid"
                )
            )

            for midi_file in mids:

                seq = (
                    midi_io.midi_file_to_note_sequence(
                        midi_file
                    )
                )

                current_time = append_sequence(
                    merged,
                    seq,
                    current_time
                )

        else:

            seq = (
                midi_io.midi_file_to_note_sequence(
                    item
                )
            )

            current_time = append_sequence(
                merged,
                seq,
                current_time
            )

    merged.total_time = current_time

    note_seq.sequence_proto_to_midi_file(
        merged,
        "Final.mid"
    )

    print("Final.mid 作成完了")


if __name__ == "__main__":

    print("処理開始")

    generate_midis()

    interpolate("A.mid","B.mid","ab_interp")
    interpolate("B.mid","C.mid","bc_interp")
    interpolate("C.mid","D.mid","cd_interp")
    interpolate("D.mid","E.mid","de_interp")

    merge_all()

    print("全処理完了")

    print("rizumutesuto")

    for i in range(20):

        rhythm = choose_rhythm("春")
        print(i+1,rhythm)

    print("rizumutestuowari")    