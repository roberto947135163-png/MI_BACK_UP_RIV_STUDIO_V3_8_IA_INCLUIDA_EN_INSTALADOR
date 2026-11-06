from app.core.scanner import AUDIO_EXTS
from app.core.duplicates import sha256_file

def test_supported_formats():
    assert ".mp3" in AUDIO_EXTS and ".flac" in AUDIO_EXTS

def test_hash(tmp_path):
    p=tmp_path/"sample.bin"; p.write_bytes(b"test")
    assert len(sha256_file(p))==64
