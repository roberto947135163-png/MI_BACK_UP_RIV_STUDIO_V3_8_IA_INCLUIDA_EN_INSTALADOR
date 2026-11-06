"""Virtual folders: never copy/move physical audio for playlists or genres."""
import json
from pathlib import Path
from app.core.database import connect, APP_DIR

SETTINGS_FILE = APP_DIR / 'settings.json'
DEFAULTS = {'app_name':'MI BACK UP', 'owner':'RIV STUDIO', 'accent':'#8b5cf6'}

def settings():
    try: return {**DEFAULTS, **json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))}
    except (OSError, ValueError): return dict(DEFAULTS)

def save_settings(data):
    allowed={k:str(v) for k,v in data.items() if k in DEFAULTS}
    tmp=SETTINGS_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps({**settings(),**allowed},ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(SETTINGS_FILE)

def ensure():
    con=connect()
    con.executescript('''
    CREATE TABLE IF NOT EXISTS dj_folders (
      id INTEGER PRIMARY KEY, name TEXT NOT NULL, parent_id INTEGER,
      FOREIGN KEY(parent_id) REFERENCES dj_folders(id));
    CREATE TABLE IF NOT EXISTS dj_folder_tracks (
      folder_id INTEGER NOT NULL, path TEXT NOT NULL,
      PRIMARY KEY(folder_id,path));
    CREATE TABLE IF NOT EXISTS dj_favorites (path TEXT PRIMARY KEY);
    CREATE TABLE IF NOT EXISTS dj_genre_overrides (path TEXT PRIMARY KEY, genre TEXT NOT NULL, subgenre TEXT NOT NULL DEFAULT 'General');
    ''')
    con.commit(); return con

def create_folder(name,parent_id=None):
    name=name.strip()
    if not name or len(name)>100: raise ValueError('Nombre de carpeta no válido')
    con=ensure()
    try:
        cur=con.execute('INSERT INTO dj_folders(name,parent_id) VALUES(?,?)',(name,parent_id))
        con.commit();return cur.lastrowid
    finally: con.close()

def folders():
    con=ensure()
    try: return [dict(r) for r in con.execute('SELECT * FROM dj_folders ORDER BY name')]
    finally: con.close()

def add_tracks(folder_id,paths):
    con=ensure()
    try:
        if not con.execute('SELECT 1 FROM dj_folders WHERE id=?',(folder_id,)).fetchone():raise ValueError('Carpeta no existe')
        con.executemany('INSERT OR IGNORE INTO dj_folder_tracks(folder_id,path) VALUES(?,?)',[(folder_id,p) for p in paths])
        con.commit()
    finally: con.close()

def remove_tracks(folder_id,paths):
    con=ensure()
    try:
        con.executemany('DELETE FROM dj_folder_tracks WHERE folder_id=? AND path=?',[(folder_id,p) for p in paths]);con.commit()
    finally: con.close()

def folder_paths(folder_id):
    con=ensure()
    try: return {r[0] for r in con.execute('SELECT path FROM dj_folder_tracks WHERE folder_id=?',(folder_id,))}
    finally: con.close()

def toggle_favorite(path):
    con=ensure()
    try:
        if con.execute('SELECT 1 FROM dj_favorites WHERE path=?',(path,)).fetchone():
            con.execute('DELETE FROM dj_favorites WHERE path=?',(path,));new=False
        else:
            con.execute('INSERT INTO dj_favorites(path) VALUES(?)',(path,));new=True
        con.commit();return new
    finally: con.close()

def favorites():
    con=ensure()
    try: return {r[0] for r in con.execute('SELECT path FROM dj_favorites')}
    finally: con.close()

def genre_override(path,genre,subgenre):
    con=ensure()
    try:
        con.execute('INSERT OR REPLACE INTO dj_genre_overrides(path,genre,subgenre) VALUES(?,?,?)',(path,genre,subgenre));con.commit()
    finally: con.close()

def overrides():
    con=ensure()
    try:return {r['path']:(r['genre'],r['subgenre']) for r in con.execute('SELECT * FROM dj_genre_overrides')}
    finally:con.close()
