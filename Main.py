import json
import subprocess
import sys
import glob

import note_seq
from note_seq.protobuf import music_pb2
from note_seq import midi_io

print("最新版Main.py起動")


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

    filename = f"{pattern['name']}.mid"

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


def run_musicvae():

    print("MusicVAE開始")

    cmd = [
        sys.executable,
        "-m",
        "magenta.models.music_vae.music_vae_generate",
        "--config=cat-mel_2bar_big",
        "--checkpoint_file=C:/AI/models/cat-mel_2bar_big.ckpt",
        "--mode=interpolate",
        "--input_midi_1=A.mid",
        "--input_midi_2=B.mid",
        "--num_outputs=5",
        "--output_dir=interpolate_test"
    ]

    result = subprocess.run(cmd)

    print("return code =", result.returncode)

    print("MusicVAE終了")


def merge_midis():

    print("MIDI連結開始")

    midi_files = sorted(
        glob.glob("interpolate_test/*.mid")
    )

    print("検出数 =", len(midi_files))

    merged = music_pb2.NoteSequence()

    current_time = 0.0

    for midi_file in midi_files:

        seq = midi_io.midi_file_to_note_sequence(
            midi_file
        )

        for note in seq.notes:

            new_note = merged.notes.add()

            new_note.pitch = note.pitch
            new_note.velocity = note.velocity

            new_note.start_time = (
                note.start_time + current_time
            )

            new_note.end_time = (
                note.end_time + current_time
            )

        current_time += seq.total_time

    merged.total_time = current_time

    merged.tempos.add(qpm=90)

    note_seq.sequence_proto_to_midi_file(
        merged,
        "final.mid"
    )

    print("final.mid 作成完了")


if __name__ == "__main__":

    print("処理開始")

    generate_midis()

    run_musicvae()

    merge_midis()

    print("全処理完了")