from app.core.genre_taxonomy import normalize_genre

def test_afro_house():
    assert normalize_genre('Afro House')==('ELECTRÓNICA','AFRO HOUSE')

def test_pack_not_genre():
    assert normalize_genre('PACK VOL 1')[0]=='POR CLASIFICAR'
    assert normalize_genre('VARIADO')[0]=='POR CLASIFICAR'

def test_no_partial_match():
    assert normalize_genre('PACK TECHNO 2026')[0]=='POR CLASIFICAR'
