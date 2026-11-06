"""Offline audio feature estimation. Estimates can be wrong; user should verify DJ-critical tracks."""
import numpy as np

CAMELOT_MAJOR = {"C":"8B", "C#":"3B", "D":"10B", "D#":"5B", "E":"12B", "F":"7B", "F#":"2B", "G":"9B", "G#":"4B", "A":"11B", "A#":"6B", "B":"1B"}
CAMELOT_MINOR = {"C":"5A", "C#":"12A", "D":"7A", "D#":"2A", "E":"9A", "F":"4A", "F#":"11A", "G":"6A", "G#":"1A", "A":"8A", "A#":"3A", "B":"10A"}
NOTES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
MAJOR_PROFILE = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
MINOR_PROFILE = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])

def estimate_key(chroma):
    vector = np.asarray(chroma, dtype=float).mean(axis=1)
    if vector.shape != (12,) or not np.isfinite(vector).all() or np.max(vector) <= 1e-8:
        return None, None
    scores=[]
    for root in range(12):
        for mode, profile in (("major",MAJOR_PROFILE),("minor",MINOR_PROFILE)):
            scores.append((float(np.corrcoef(vector, np.roll(profile,root))[0,1]),root,mode))
    _, root, mode = max(scores)
    note = NOTES[root]
    return f"{note} {mode}", (CAMELOT_MAJOR if mode=="major" else CAMELOT_MINOR)[note]

def analyze_audio(path, seconds=90):
    import librosa
    # Load bounded excerpts to keep RAM use controlled on 8GB machines.
    y, sr = librosa.load(path, sr=22050, mono=True, duration=seconds)
    if len(y) < sr * 3 or np.max(np.abs(y)) < 1e-6:
        raise ValueError("Audio demasiado corto o silencioso")
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    tempo = librosa.feature.tempo(onset_envelope=onset, sr=sr, hop_length=512, aggregate=np.median)
    bpm = round(float(tempo[0]), 1) if len(tempo) else None
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=1024)
    key, camelot = estimate_key(chroma)
    rms = librosa.feature.rms(y=y)[0]
    energy = round(float(np.clip(np.mean(rms) * 100, 0, 100)), 1)
    return {"bpm":bpm,"musical_key":key,"camelot":camelot,"energy":energy}
