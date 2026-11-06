from pathlib import Path
from app.core.pretrained_genre import bundled_model_dir,active_model_dir

def test_model_dir_resolution():
    assert isinstance(bundled_model_dir(),Path)
    assert isinstance(active_model_dir(),Path)
