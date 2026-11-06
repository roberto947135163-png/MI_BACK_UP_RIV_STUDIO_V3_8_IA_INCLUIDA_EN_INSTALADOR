from pathlib import Path


def test_virtual_table_source_uses_view_and_model():
    code=(Path(__file__).resolve().parents[1]/'app/ui/main_window.py').read_text(encoding='utf-8')
    assert 'class VirtualMusicModel(QAbstractTableModel)' in code
    assert 'self.table=QTableView()' in code
    assert 'self.music_model.set_tracks(rows)' in code
    assert 'page_size=100' not in code


def test_https_never_disables_certificate_verification():
    code=(Path(__file__).resolve().parents[1]/'app/core/model_install.py').read_text(encoding='utf-8')
    assert 'CERT_NONE' not in code
    assert 'secure_context()' in code
