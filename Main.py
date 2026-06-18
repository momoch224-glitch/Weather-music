import json
import glob
import shutil
import subprocess
import sys

import note_seq
from note_seq.protobuf import music_pb2
from note_seq import midi_io

print("最新版Main.py起動")


CHECKPOINT = "C:/AI/models/cat-mel_2bar_big.ckpt"


def create_melody_midi(pattern, bpm):

    seq = music_pb2.NoteSequence()

    seq.ticks_per_quarter = 220
    seq.tempos.add(qpm=bpm)

    melody_map = {
        "C": [60, 64],
        "Dm": [62, 65],
        "Em": [64, 67],
        "F": [65, 69],
        "G": [67, 71],
        "Am": [69, 72]
    }

    note_index = 0

    for chord in pattern["chords"]:

        notes = melody_map.get(chord, [60, 64])

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

    filename = pattern["name"] + ".mid"

    note_seq.sequence_proto_to_midi_file(
        seq,
        filename
    )

    print(filename + " 作成完了")


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
            note.start_time +
            current_time
        )

        new_note.end_time = (
            note.end_time +
            current_time
        )

    return current_time + seq.total_time


def merge_all():

    print("連結開始")

    merged = music_pb2.NoteSequence()

    merged.tempos.add(qpm=90)

    current_time = 0.0

    structure = [

        ("A.mid", None),

        ("ab_interp", True),
        ("B.mid", None),

        ("bc_interp", True),
        ("C.mid", None),

        ("cd_interp", True),
        ("D.mid", None),

        ("de_interp", True),
        ("E.mid", None)
    ]

    for item, is_folder in structure:

        if is_folder:

            mids = sorted(
                glob.glob(
                    item + "/*of-005.mid"
                )
            )

            for midi_file in mids:

                seq = (
                    midi_io
                    .midi_file_to_note_sequence(
                        midi_file
                    )
                )

                current_time = (
                    append_sequence(
                        merged,
                        seq,
                        current_time
                    )
                )

        else:

            seq = (
                midi_io
                .midi_file_to_note_sequence(
                    item
                )
            )

            current_time = (
                append_sequence(
                    merged,
                    seq,
                    current_time
                )
            )

    merged.total_time = current_time

    note_seq.sequence_proto_to_midi_file(
        merged,
        "final.mid"
    )

    print("final.mid 作成完了")


if __name__ == "__main__":

    print("処理開始")

    generate_midis()

    interpolate(
        "A.mid",
        "B.mid",
        "ab_interp"
    )

    interpolate(
        "B.mid",
        "C.mid",
        "bc_interp"
    )

    interpolate(
        "C.mid",
        "D.mid",
        "cd_interp"
    )

    interpolate(
        "D.mid",
        "E.mid",
        "de_interp"
    )

    merge_all()

    print("全処理完了")