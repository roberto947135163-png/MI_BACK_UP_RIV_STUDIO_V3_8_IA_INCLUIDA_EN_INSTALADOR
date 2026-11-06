import numpy as np
from app.core.audio_analysis import estimate_key, CAMELOT_MAJOR, CAMELOT_MINOR

def test_camelot_maps():
    assert len(CAMELOT_MAJOR)==12 and len(CAMELOT_MINOR)==12
    assert CAMELOT_MAJOR["C"]=="8B" and CAMELOT_MINOR["A"]=="8A"

def test_silent_chroma():
    assert estimate_key(np.zeros((12, 30))) == (None, None)

def test_c_major_template():
    from app.core.audio_analysis import MAJOR_PROFILE
    key, code = estimate_key(np.tile(MAJOR_PROFILE[:,None], (1,10)))
    assert (key,code)==("C major","8B")
