"""Discogs EffNet ONNX adapter. Predictions use audio only, never tags/filenames.

Official model expects log-mel [N,128,96] at 16 kHz. The librosa
frontend is an approximation of Essentia's frontend and must be validated
against reference predictions before production deployment.
"""
import json
import sys
from pathlib import Path
import numpy as np

MODEL_NAME='discogs-effnet-bsdynamic-1.onnx'
META_NAME='discogs-effnet-bsdynamic-1.json'
MODEL_URL='https://essentia.upf.edu/models/music-style-classification/discogs-effnet/'+MODEL_NAME
META_URL='https://essentia.upf.edu/models/music-style-classification/discogs-effnet/'+META_NAME


def model_paths(root):
    root=Path(root)
    return root/MODEL_NAME,root/META_NAME


def model_ready(root):
    a,b=model_paths(root)
    return a.is_file() and a.stat().st_size>1000000 and b.is_file()


def bundled_model_dir():
    """Model distributed with the PyInstaller executable, not downloaded by the user."""
    base=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[2]))
    return base/'models'

def active_model_dir():
    """Prefer bundled weights; retain legacy user-installed weights for compatibility."""
    bundled=bundled_model_dir()
    if model_ready(bundled):return bundled
    from app.core.database import APP_DIR
    return APP_DIR/'models'

def map_discogs(label):
    from app.core.genre_taxonomy import normalize_genre,UNKNOWN
    if '---' not in label:return UNKNOWN
    family,style=label.split('---',1)
    aliases={'Tribal House':'AFRO HOUSE','Reggaeton':'REGGAETÓN','Drum n Bass':'DRUM AND BASS',
             'Boom Bap':'HIP HOP','Contemporary R&B':'R&B','Afrobeat':'AFROBEAT'}
    # Tribal House is NOT equivalent to Afro House: never invent a specific subgenre.
    aliases.pop('Tribal House')
    if style=='Tribal House':return ('ELECTRÓNICA','TRIBAL HOUSE')
    normalized=normalize_genre(aliases.get(style,style))
    if normalized!=UNKNOWN:return normalized
    family_map={'Electronic':'ELECTRÓNICA','Latin':'LATINA','Hip Hop':'URBANA','Pop':'COMERCIAL',
                'Rock':'COMERCIAL','Reggae':'REGGAE','Jazz':'JAZZ','Funk / Soul':'FUNK / SOUL'}
    if family in family_map and style and not any(x in style.lower() for x in ['pack','varied','vol.']):
        return (family_map[family],style.upper())
    return UNKNOWN


def select_prediction(labels,scores,threshold=.28):
    """Discogs is multi-label sigmoid; do not apply softmax to outputs."""
    from app.core.genre_taxonomy import UNKNOWN
    a=np.asarray(scores,dtype=np.float32).reshape(-1)
    if len(a)!=len(labels) or not np.all(np.isfinite(a)):
        raise ValueError('Invalid output dimensions or scores')
    ranked=np.argsort(a)[::-1]
    for idx in ranked:
        genre,sub=map_discogs(labels[int(idx)])
        if (genre,sub)!=UNKNOWN:
            score=float(a[idx])
            if score>=threshold:
                return {'status':'classified','genre':sub,'main_genre':genre,'similarity':score,
                        'model_version':'discogs-effnet-onnx-v1'}
            break
    return {'status':'uncertain','genre':None,'main_genre':'POR CLASIFICAR',
            'similarity':float(a[ranked[0]]) if len(ranked) else 0.0,
            'model_version':'discogs-effnet-onnx-v1'}


def classify_audio(path,model_dir,seconds=20,threshold=.28,session=None):
    import librosa
    import onnxruntime as ort
    model,meta=model_paths(model_dir)
    if not model_ready(model_dir):
        raise FileNotFoundError('Instala el modelo ONNX y su JSON oficial; consulta INSTALAR_IA.md')
    labels=json.loads(meta.read_text(encoding='utf-8'))['classes']
    y,_=librosa.load(str(path),sr=16000,mono=True,duration=seconds)
    if len(y)<16000*3:raise ValueError('Audio demasiado corto')
    # Essentia EffNet frontend uses a 128x96 mel representation. This approximation
    # must be compared to Essentia's reference frontend before claiming accuracy.
    mel=librosa.feature.melspectrogram(y=y,sr=16000,n_fft=512,hop_length=256,
                                      n_mels=96,fmin=0,fmax=8000,power=2.0)
    logmel=np.log(np.maximum(mel,1e-6)).T.astype(np.float32)
    if len(logmel)<128:raise ValueError('Audio insuficiente para el modelo')
    frames=[]
    for start in np.linspace(0,max(0,len(logmel)-128),num=min(8,max(1,len(logmel)//128)),dtype=int):
        frames.append(logmel[start:start+128,:])
    x=np.stack(frames)
    if session is None:
        opts=ort.SessionOptions()
        opts.intra_op_num_threads=2
        opts.inter_op_num_threads=1
        sess=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
    else:
        sess=session
    inp=sess.get_inputs()[0]
    if len(inp.shape)!=3:raise ValueError('ONNX incorrecto: entrada debe ser [N,128,96]')
    outputs=sess.run(None,{inp.name:x})
    candidates=[np.asarray(o) for o in outputs if np.asarray(o).ndim==2 and np.asarray(o).shape[-1]==len(labels)]
    if not candidates:raise ValueError('No se encontró salida de 400 estilos')
    scores=np.median(candidates[0],axis=0)
    return select_prediction(labels,scores,threshold)
