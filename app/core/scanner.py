from pathlib import Path
from mutagen import File as MutagenFile

AUDIO_EXTS = {".mp3",".wav",".flac",".aiff",".aif",".m4a",".aac",".ogg",".opus"}

def scan_folder(root):
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS:
            yield p

def read_metadata(path):
    p = Path(path)
    easy = MutagenFile(str(p), easy=True)
    def first(key):
        values = easy.get(key, []) if easy else []
        return str(values[0]) if values else ""
    duration = bitrate = sample_rate = None
    raw = MutagenFile(str(p))
    if raw and raw.info:
        duration = float(getattr(raw.info, "length", 0) or 0)
        bitrate = int(getattr(raw.info, "bitrate", 0) or 0)
        sample_rate = int(getattr(raw.info, "sample_rate", 0) or 0)
    return {"path":str(p.resolve()),"filename":p.name,"title":first("title") or p.stem,
      "artist":first("artist"),"album":first("album"),"genre":first("genre"),
      "duration":duration,"bitrate":bitrate,"sample_rate":sample_rate,
      "file_size":p.stat().st_size,"sha256":None}
