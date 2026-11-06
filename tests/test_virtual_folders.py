from pathlib import Path
from app.core import library_views as lib
from app.core import database as db

def test_virtual_folders_and_favorites(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'library.sqlite3')
    monkeypatch.setattr(lib,'SETTINGS_FILE',tmp_path/'settings.json')
    folder=lib.create_folder('Set de prueba')
    sub=lib.create_folder('Reggaeton',folder)
    assert any(x['id']==sub and x['parent_id']==folder for x in lib.folders())
    path=str(tmp_path/'no-tocar.mp3')
    lib.add_tracks(sub,[path,path]);assert lib.folder_paths(sub)=={path}
    assert lib.toggle_favorite(path) is True
    assert path in lib.favorites()
    assert lib.toggle_favorite(path) is False
    assert path not in lib.favorites()
    lib.genre_override(path,'Urbano','Reggaeton')
    assert lib.overrides()[path]==('Urbano','Reggaeton')
    lib.remove_tracks(sub,[path]);assert not lib.folder_paths(sub)
    assert not Path(path).exists()

def test_settings(tmp_path,monkeypatch):
    monkeypatch.setattr(lib,'SETTINGS_FILE',tmp_path/'settings.json')
    lib.save_settings({'app_name':'MI BACK UP','accent':'#33aaff'})
    assert lib.settings()['accent']=='#33aaff'
