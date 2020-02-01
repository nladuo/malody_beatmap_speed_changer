import librosa


def compress_music(filepath):
    x, sr = librosa.load(filepath, sr=8400)
    librosa.output.write_wav(filepath, x, sr)
