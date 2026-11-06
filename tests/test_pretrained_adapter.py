from app.core.pretrained_genre import model_ready,classify_audio
import pytest

def test_model_absent(tmp_path):
    assert not model_ready(tmp_path)
    with pytest.raises((FileNotFoundError,ImportError)):
        classify_audio(tmp_path/'track.mp3',tmp_path)
