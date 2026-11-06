"""Safe preview-first copy. Never moves, overwrites or deletes source tracks."""
from pathlib import Path
import hashlib
import re
import shutil
from app.core.genre_ai import prediction_map

ELECTRONIC={'house','afro house','tech house','deep house','progressive house','techno','minimal','melodic techno','trance','edm','electro house','dance','latin house'}
LATIN={'reggaeton','reggaetón','salsa','merengue','cumbia','bachata','dembow','latin pop','musica urbana','música urbana'}
COMMERCIAL={'pop','rock','disco','funk','hip hop','rap'}

def genre_folder(genre):
    g=(genre or '').strip()
    k=g.casefold()
    if k in ELECTRONIC: group='01 - ELECTRONICA'
    elif k in LATIN: group='02 - LATIN MUSIC'
    elif k in COMMERCIAL: group='03 - MUSICA COMERCIAL'
    else: return Path('05 - POR CLASIFICAR')
    safe=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',g).strip(' .')[:75]
    return Path(group)/safe.upper()

def plan(paths,destination, threshold=0.70):
    pred=prediction_map()
    from app.core.database import connect
    con=connect()
    try:
        metadata={r['path']:r['genre'] for r in con.execute('SELECT path,genre FROM tracks')}
    finally: con.close()
    root=Path(destination).resolve()
    items=[]; reserved=set()
    for path in paths:
        src=Path(path).resolve()
        if not src.is_file(): raise FileNotFoundError(str(src))
        genre,similarity=pred.get(str(src),('POR CLASIFICAR',0.0))
        if similarity<threshold:
            # Use a genre from existing audio metadata only when no accepted AI prediction.
            genre=metadata.get(str(src)) or None
        dst=root/genre_folder(genre)/src.name
        # Do not copy into same location or overwrite existing files.
        if dst==src or dst.exists() or str(dst).casefold() in reserved:
            raise FileExistsError('Destino ocupado o igual al origen: '+str(dst))
        reserved.add(str(dst).casefold())
        items.append((src,dst))
    return items

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def copy_verified(items):
    done=[]
    for src,dst in items:
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists(): raise FileExistsError(str(dst))
        # Exclusive creation avoids accidental overwrite, including concurrent runs.
        try:
            with src.open('rb') as reader, dst.open('xb') as writer:
                shutil.copyfileobj(reader,writer,1024*1024)
            if sha256(src)!=sha256(dst): raise IOError('La copia no coincide: '+str(dst))
            shutil.copystat(src,dst)
            done.append((str(src),str(dst)))
        except Exception:
            if dst.exists(): dst.unlink()
            raise
    return done
