import hashlib
from pathlib import Path

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def find_exact_duplicates(paths):
    groups={}
    for item in paths:
        p=Path(item)
        try:
            groups.setdefault((p.stat().st_size,sha256_file(p)),[]).append(str(p))
        except OSError:
            pass
    return [v for v in groups.values() if len(v)>1]
