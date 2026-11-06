"""Strict musical genre taxonomy. No filename/pack-name inference."""
import re

# (main category, subgenre): explicit musical classes only.
GENRES = {
 'afro house': ('ELECTRÓNICA','AFRO HOUSE'),
 'afrohouse': ('ELECTRÓNICA','AFRO HOUSE'),
 'tech house': ('ELECTRÓNICA','TECH HOUSE'),
 'deep house': ('ELECTRÓNICA','DEEP HOUSE'),
 'progressive house': ('ELECTRÓNICA','PROGRESSIVE HOUSE'),
 'melodic techno': ('ELECTRÓNICA','MELODIC TECHNO'),
 'techno': ('ELECTRÓNICA','TECHNO'),
 'house': ('ELECTRÓNICA','HOUSE'),
 'trance': ('ELECTRÓNICA','TRANCE'),
 'edm': ('ELECTRÓNICA','EDM'),
 'electro house': ('ELECTRÓNICA','ELECTRO HOUSE'),
 'latin house': ('ELECTRÓNICA','LATIN HOUSE'),
 'drum and bass': ('ELECTRÓNICA','DRUM AND BASS'),
 'dubstep': ('ELECTRÓNICA','DUBSTEP'),
 'reggaeton': ('LATINA','REGGAETÓN'),
 'reggaetón': ('LATINA','REGGAETÓN'),
 'dembow': ('LATINA','DEMBOW'),
 'salsa': ('LATINA','SALSA'),
 'merengue': ('LATINA','MERENGUE'),
 'bachata': ('LATINA','BACHATA'),
 'cumbia': ('LATINA','CUMBIA'),
 'latin pop': ('LATINA','LATIN POP'),
 'latin trap': ('URBANA','LATIN TRAP'),
 'trap': ('URBANA','TRAP'),
 'hip hop': ('URBANA','HIP HOP'),
 'rap': ('URBANA','RAP'),
 'r&b': ('URBANA','R&B'),
 'pop': ('COMERCIAL','POP'),
 'rock': ('COMERCIAL','ROCK'),
 'disco': ('COMERCIAL','DISCO'),
 'funk': ('COMERCIAL','FUNK'),
}

UNKNOWN=('POR CLASIFICAR','SIN CLASIFICAR')

def normalize_genre(label):
    if not isinstance(label,str) or not label.strip():
        return UNKNOWN
    key=re.sub(r'\s+',' ',label.strip().casefold())
    # Exact match only: do not invent genres from packs, filenames or combinations.
    return GENRES.get(key, UNKNOWN)
