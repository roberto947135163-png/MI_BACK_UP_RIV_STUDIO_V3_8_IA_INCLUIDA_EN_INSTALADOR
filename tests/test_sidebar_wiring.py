from pathlib import Path

def test_sidebar_actions_are_connected():
    code=(Path(__file__).resolve().parents[1]/'app/ui/main_window.py').read_text(encoding='utf-8')
    assert 'b.clicked.connect(lambda checked=False,page=name:self.navigate(page))' in code
    assert "['Inicio','Todos los temas','Géneros','Playlists','Favoritos','Configuración']" in code
    assert 'self.stack.setCurrentIndex(0)' in code
