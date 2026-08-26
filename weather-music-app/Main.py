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


CHECKPOINT = (
    "C:/AI/models/"
    "cat-mel_2bar_big/"
    "cat-mel_2bar_big.ckpt"
)
RHYTHMS = {
    "calm": [1, 1, 1, 1],
    "flowing": [1, 0.5, 0.5, 1, 1],
    "active": [0.5, 0.5, 0.5, 0.5, 1, 1],
    "dramatic": [0.25, 0.25, 0.5, 0.5, 0.5, 1]
}

def choose_rhythm(pattern_name):

    if pattern_name == "A":
        return "calm"

    elif pattern_name == "B":
        return "flowing"

    elif pattern_name == "C":
        return "active"

    else:
        return "dramatic"
    
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

    bass_map = {
        "C": 36,
        "Dm": 38,
        "Em": 40,
        "F": 41,
        "G": 43,
        "Am": 45
    }

    current_time = 0

    rhythm_name = choose_rhythm(
        pattern["name"]
    )

    rhythm = RHYTHMS[rhythm_name]
    measure_length = sum(rhythm)

    for chord in pattern["chords"]:

        measure_start = current_time

        pitches = melody_map.get(
            chord,
            [60, 64]
        )

        bass_pitch = bass_map.get(
            chord,
            36
        )

        #
        # ===== Bass =====
        #
        bass = seq.notes.add()
        bass.pitch = bass_pitch
        bass.start_time = measure_start
        bass.end_time = (
            measure_start
            + measure_length
        )
        bass.velocity = 70
        bass.instrument = 1
        bass.program = 32

        #
        # ===== Strings Pad =====
        #
        pad1 = seq.notes.add()
        pad1.pitch = bass_pitch + 24
        pad1.start_time = measure_start
        pad1.end_time = (
            measure_start
            + measure_length *2
        )
        pad1.velocity = 30
        pad1.instrument = 2
        pad1.program = 48

        pad2 = seq.notes.add()
        pad2.pitch = bass_pitch + 31
        pad2.start_time = measure_start
        pad2.end_time = (
            measure_start
            + measure_length*2
        )
        pad2.velocity = 30
        pad2.instrument = 2
        pad2.program = 48

        #
        # ===== Melody =====
        #
        for duration in rhythm:

            pitch = pitches[
                int(current_time)
                % len(pitches)
            ]

            note = seq.notes.add()

            note.pitch = pitch
            note.start_time = current_time
            note.end_time = (
                current_time
                + duration
            )
            note.velocity = 90
            note.instrument = 0
            note.program = 0

            current_time += duration

        #
        # ===== Drum =====
        #
        beat_time = measure_start

        for i in range(
            int(measure_length)
        ):

            # HiHat
            hat = seq.notes.add()
            hat.pitch = 42
            hat.start_time = (
                beat_time + i
            )
            hat.end_time = (
                beat_time + i + 0.1
            )
            hat.velocity = 60
            hat.instrument = 9
            hat.is_drum = True

            # Kick
            if i % 2 == 0:

                kick = seq.notes.add()

                kick.pitch = 36
                kick.start_time = (
                    beat_time + i
                )
                kick.end_time = (
                    beat_time + i + 0.1
                )
                kick.velocity = 80
                kick.instrument = 9
                kick.is_drum = True

            # Snare
            else:

                snare = seq.notes.add()

                snare.pitch = 38
                snare.start_time = (
                    beat_time + i
                )
                snare.end_time = (
                    beat_time + i + 0.1
                )
                snare.velocity = 75
                snare.instrument = 9
                snare.is_drum = True

    seq.total_time = current_time

    filename = (
        pattern["name"]
        + ".mid"
    )

    note_seq.sequence_proto_to_midi_file(
        seq,
        filename
    )

    print(
        filename
        + " 作成完了"
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

        new_note.instrument = note.instrument
        new_note.program = note.program
        new_note.is_drum = note.is_drum

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
    def add_arrangement():
        print("編曲開始")

        seq = midi_io.midi_file_to_note_sequence(
            "final.mid"
        )

        new_notes = []

        # コード感を推定するため、
        # 低い音以外のメロディを利用
        measure = 4.0
        current = 0.0

        while current < seq.total_time:

            pitches = []

            for note in seq.notes:
                if (
                    current <= note.start_time
                    < current + measure
                ):
                    pitches.append(
                        note.pitch
                    )

            if len(pitches) == 0:
                current += measure
                continue

            root = min(pitches)

            #
            # ===== Bass =====
            #
            bass = music_pb2.Note()

            bass.pitch = max(
                root - 24,
                36
            )

            bass.start_time = current
            bass.end_time = (
                current + measure
            )

            bass.velocity = 70
            bass.instrument = 1
            bass.program = 32

            new_notes.append(bass)

            #
            # ===== Strings =====
            #
            for interval in [0, 7]:

                pad = music_pb2.Note()

                pad.pitch = (
                    bass.pitch
                    + 24
                    + interval
                )

                pad.start_time = current

                pad.end_time = (
                    current
                    + measure * 2
                )

                pad.velocity = 35
                pad.instrument = 2
                pad.program = 48

                new_notes.append(
                    pad
                )

            #
            # ===== Drums =====
            #
            for beat in range(4):

                hat = music_pb2.Note()

                hat.pitch = 42
                hat.start_time = (
                    current + beat
                )
                hat.end_time = (
                    current
                    + beat
                    + 0.1
                )

                hat.velocity = 60
                hat.instrument = 9
                hat.is_drum = True

                new_notes.append(hat)

                if beat % 2 == 0:

                    kick = music_pb2.Note()

                    kick.pitch = 36
                    kick.start_time = (
                        current + beat
                    )
                    kick.end_time = (
                        current
                        + beat
                        + 0.1
                    )

                    kick.velocity = 80
                    kick.instrument = 9
                    kick.is_drum = True

                    new_notes.append(
                        kick
                    )

                else:

                    snare = music_pb2.Note()

                    snare.pitch = 38
                    snare.start_time = (
                        current + beat
                    )
                    snare.end_time = (
                        current
                        + beat
                        + 0.1
                    )

                    snare.velocity = 75
                    snare.instrument = 9
                    snare.is_drum = True

                    new_notes.append(
                        snare
                    )

            current += measure

        #
        # 追加
        #
        for n in new_notes:
            seq.notes.add().CopyFrom(n)

        note_seq.sequence_proto_to_midi_file(
            seq,
            "../weather_music_ui/final_arranged.mid"
        )

        print(
            "final_arranged.mid 作成完了"
        )

    # ==========================================
    # ここから下が merge_all() のメイン処理
    # ==========================================
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
    
    # 最後に add_arrangement() を呼び出して伴奏を付け、UIフォルダに保存する
    add_arrangement()
    def add_arrangement():

        print("編曲開始")

        seq = midi_io.midi_file_to_note_sequence(
        "final.mid"
        )

        new_notes = []

    # コード感を推定するため、
    # 低い音以外のメロディを利用
        measure = 4.0
        current = 0.0

        while current < seq.total_time:
            pitches = []

            for note in seq.notes:
                if (
                    current <= note.start_time
                    < current + measure
                ):
                    pitches.append(
                        note.pitch
                    )

            if len(pitches) == 0:
                current += measure
                continue

        root = min(pitches)

        #
        # ===== Bass =====
        #
        bass = music_pb2.Note()

        bass.pitch = max(
            root - 24,
            36
        )

        bass.start_time = current
        bass.end_time = (
            current + measure
        )

        bass.velocity = 70
        bass.instrument = 1
        bass.program = 32

        new_notes.append(bass)

        #
        # ===== Strings =====
        #
        for interval in [0, 7]:

            pad = music_pb2.Note()

            pad.pitch = (
                bass.pitch
                + 24
                + interval
            )

            pad.start_time = current

            pad.end_time = (
                current
                + measure * 2
            )

            pad.velocity = 35
            pad.instrument = 2
            pad.program = 48

            new_notes.append(
                pad
            )

        #
        # ===== Drums =====
        #
        for beat in range(4):

            hat = music_pb2.Note()

            hat.pitch = 42
            hat.start_time = (
                current + beat
            )
            hat.end_time = (
                current
                + beat
                + 0.1
            )

            hat.velocity = 60
            hat.instrument = 9
            hat.is_drum = True

            new_notes.append(hat)

            if beat % 2 == 0:

                kick = music_pb2.Note()

                kick.pitch = 36
                kick.start_time = (
                    current + beat
                )
                kick.end_time = (
                    current
                    + beat
                    + 0.1
                )

                kick.velocity = 80
                kick.instrument = 9
                kick.is_drum = True

                new_notes.append(
                    kick
                )

            else:

                snare = music_pb2.Note()

                snare.pitch = 38
                snare.start_time = (
                    current + beat
                )
                snare.end_time = (
                    current
                    + beat
                    + 0.1
                )

                snare.velocity = 75
                snare.instrument = 9
                snare.is_drum = True

                new_notes.append(
                    snare
                )

        current += measure

    #
    # 追加
    #
    for n in new_notes:

        seq.notes.add().CopyFrom(n)

    note_seq.sequence_proto_to_midi_file(
        seq,
        "../weather_music_ui/final_arranged.mid"
    )

    print(
        "final_arranged.mid 作成完了"
    )
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
    add_arrangement()

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