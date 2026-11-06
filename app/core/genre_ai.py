"""Offline, audio-based, user-trained genre classifier.

This is NOT a pretrained general-purpose model. It learns from the user's own
tracks with verified genre tags; it never guesses from filenames. Confidence
is a distance-based similarity score, not a calibrated probability.
"""
import json
import sqlite3
from pathlib import Path
import numpy as np
from app.core.database import connect

MIN_EXAMPLES = 5
MIN_GENRES = 2

def extract_features(path, seconds=35):
    import librosa
    y, sr = librosa.load(str(path), sr=16000, mono=True, duration=seconds)
    if len(y) < sr * 5 or np.max(np.abs(y)) < 1e-6:
        raise ValueError('Audio insuficiente o silencioso')
    hop=512
    mfcc=librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop)
    chroma=librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop)
    centroid=librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)
    rolloff=librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop)
    zcr=librosa.feature.zero_crossing_rate(y, hop_length=hop)
    rms=librosa.feature.rms(y=y, hop_length=hop)
    def stats(x):
        return np.concatenate([np.mean(x,axis=1),np.std(x,axis=1)])
    vec=np.concatenate([stats(mfcc),stats(chroma),stats(centroid),stats(rolloff),stats(zcr),stats(rms)])
    return vec.astype(float).tolist()

def ensure_tables(con):
    con.executescript('''
    CREATE TABLE IF NOT EXISTS genre_features(
        path TEXT PRIMARY KEY, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
        vector TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS genre_predictions(
        path TEXT PRIMARY KEY, predicted_genre TEXT NOT NULL,
        similarity REAL NOT NULL, model_version TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')

def feature_for(path, con=None):
    p=Path(path)
    stat=p.stat()
    owned=con is None
    if owned: con=connect()
    try:
        ensure_tables(con)
        row=con.execute('SELECT size,mtime_ns,vector FROM genre_features WHERE path=?',(str(p),)).fetchone()
        if row and row['size']==stat.st_size and row['mtime_ns']==stat.st_mtime_ns:
            return np.asarray(json.loads(row['vector']),dtype=float)
        vector=extract_features(p)
        con.execute('INSERT OR REPLACE INTO genre_features(path,size,mtime_ns,vector) VALUES(?,?,?,?)',
                    (str(p),stat.st_size,stat.st_mtime_ns,json.dumps(vector)))
        con.commit()
        return np.asarray(vector,dtype=float)
    finally:
        if owned: con.close()

def train_from_library(con=None):
    """Use ONLY manually tagged genres; exclude unknown and automatic predictions."""
    owned=con is None
    if owned: con=connect()
    try:
        ensure_tables(con)
        rows=con.execute('''SELECT t.path,t.genre FROM tracks t
          WHERE t.genre IS NOT NULL AND trim(t.genre) != ''
          AND lower(trim(t.genre)) NOT IN ('unknown','desconocido','por clasificar','otros')
          ORDER BY t.id''').fetchall()
        groups={}
        failures=0
        for row in rows:
            if len(groups.get(row['genre'].strip(),[]))>=20: continue
            if not Path(row['path']).is_file(): continue
            try: vec=feature_for(row['path'],con)
            except Exception: failures+=1; continue
            groups.setdefault(row['genre'].strip(),[]).append(vec)
        groups={name:v for name,v in groups.items() if len(v)>=MIN_EXAMPLES}
        if len(groups)<MIN_GENRES:
            raise ValueError('Se necesitan al menos 2 géneros con 5 canciones etiquetadas cada uno.')
        allvec=np.stack([v for group in groups.values() for v in group])
        mean=np.mean(allvec,axis=0)
        std=np.maximum(np.std(allvec,axis=0),1e-5)
        prototypes={name:np.mean((np.stack(v)-mean)/std,axis=0).tolist() for name,v in groups.items()}
        model={'version':'user-trained-v1','mean':mean.tolist(),'std':std.tolist(),
               'prototypes':prototypes,'counts':{k:len(v) for k,v in groups.items()}}
        from app.core.database import APP_DIR
        target=APP_DIR/'genre_model.json'
        tmp=target.with_suffix('.tmp')
        tmp.write_text(json.dumps(model,ensure_ascii=False),encoding='utf-8')
        tmp.replace(target)
        return {'genres':model['counts'],'failures':failures,'path':str(target)}
    finally:
        if owned: con.close()

def predict(path, threshold=0.70):
    from app.core.database import APP_DIR
    model_path=APP_DIR/'genre_model.json'
    if not model_path.is_file():
        return {'status':'model_missing','genre':None,'similarity':0.0}
    model=json.loads(model_path.read_text(encoding='utf-8'))
    vec=feature_for(path)
    mean=np.asarray(model['mean']); std=np.asarray(model['std'])
    x=(vec-mean)/std
    distances={name:float(np.linalg.norm(x-np.asarray(proto))/np.sqrt(len(x)))
               for name,proto in model['prototypes'].items()}
    name=min(distances,key=distances.get)
    # Heuristic similarity, not a calibrated confidence probability.
    sim=float(np.exp(-distances[name]/2))
    if sim<threshold:
        return {'status':'uncertain','genre':None,'similarity':sim}
    return {'status':'classified','genre':name,'similarity':sim}

def save_prediction(path,result):
    con=connect()
    try:
        ensure_tables(con)
        con.execute('INSERT OR REPLACE INTO genre_predictions(path,predicted_genre,similarity,model_version) VALUES(?,?,?,?)',
                    (path,result.get('genre') or 'POR CLASIFICAR',result['similarity'],'user-trained-v1'))
        con.commit()
    finally: con.close()

def prediction_map():
    con=connect()
    try:
        ensure_tables(con)
        return {r['path']:(r['predicted_genre'],r['similarity']) for r in con.execute('SELECT * FROM genre_predictions')}
    finally: con.close()
