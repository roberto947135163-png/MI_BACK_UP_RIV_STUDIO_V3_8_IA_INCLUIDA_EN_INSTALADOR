from app.core.safe_organizer import genre_folder
from app.core.audio_analysis import estimate_key
import numpy as np

def test_folders():
    assert str(genre_folder('Afro House')).startswith('01 - ELECTRONICA')
    assert str(genre_folder('Reggaetón')).startswith('02 - LATIN MUSIC')
    assert str(genre_folder('No existe'))=='05 - POR CLASIFICAR'

def test_silent_key():
    assert estimate_key(np.zeros((12,5)))==(None,None)

def test_copy_no_overwrite(tmp_path):
    from app.core.safe_organizer import copy_verified
    src=tmp_path/'a.mp3'; src.write_bytes(b'test')
    dst=tmp_path/'out'/'a.mp3'
    copy_verified([(src,dst)])
    assert dst.read_bytes()==src.read_bytes()
    try:copy_verified([(src,dst)])
    except FileExistsError:pass
    else:assert False
