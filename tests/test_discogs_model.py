import numpy as np
from app.core.pretrained_genre import map_discogs,select_prediction

def test_reggaeton():
    assert map_discogs('Latin---Reggaeton')==('LATINA','REGGAETÓN')
def test_tech_house():
    assert map_discogs('Electronic---Tech House')==('ELECTRÓNICA','TECH HOUSE')
def test_no_pack():
    assert map_discogs('Electronic---Pack Vol 1')[0]=='POR CLASIFICAR'
def test_multilabel_threshold():
    r=select_prediction(['Latin---Salsa','Electronic---Tech House'],[.1,.9])
    assert r['genre']=='TECH HOUSE'
def test_uncertain():
    r=select_prediction(['Latin---Salsa'],[.1])
    assert r['status']=='uncertain'
