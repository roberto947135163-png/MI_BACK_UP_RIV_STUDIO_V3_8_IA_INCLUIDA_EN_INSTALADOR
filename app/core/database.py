import sqlite3
from pathlib import Path

APP_DIR = Path.home() / "Documents" / "BACKUP_DJ_ROBERTO_RIVERA"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "library.sqlite3"

SCHEMA = '''
CREATE TABLE IF NOT EXISTS tracks (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 path TEXT NOT NULL UNIQUE, filename TEXT NOT NULL, title TEXT, artist TEXT,
 album TEXT, genre TEXT, duration REAL, bitrate INTEGER, sample_rate INTEGER,
 file_size INTEGER, sha256 TEXT, bpm REAL, musical_key TEXT,
 ai_confidence REAL, analyzed INTEGER DEFAULT 0,
 added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
'''

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    existing = {r[1] for r in con.execute("PRAGMA table_info(tracks)")}
    for name, typ in (("camelot", "TEXT"), ("energy", "REAL"), ("analysis_error", "TEXT"), ("analyzed_at", "TEXT")):
        if name not in existing:
            con.execute(f"ALTER TABLE tracks ADD COLUMN {name} {typ}")
    con.commit()
    return con

def upsert_track(d):
    con = connect()
    con.execute('''INSERT INTO tracks(path,filename,title,artist,album,genre,duration,bitrate,sample_rate,file_size,sha256)
    VALUES(:path,:filename,:title,:artist,:album,:genre,:duration,:bitrate,:sample_rate,:file_size,:sha256)
    ON CONFLICT(path) DO UPDATE SET filename=excluded.filename,title=excluded.title,
    artist=excluded.artist,album=excluded.album,genre=excluded.genre,duration=excluded.duration,
    bitrate=excluded.bitrate,sample_rate=excluded.sample_rate,file_size=excluded.file_size''', d)
    con.commit()
    con.close()

def all_tracks():
    con = connect()
    rows = con.execute("SELECT * FROM tracks ORDER BY artist,title").fetchall()
    con.close()
    return rows


def update_analysis(path, result):
    con = connect()
    try:
        con.execute("""UPDATE tracks SET bpm=?, musical_key=?, camelot=?, energy=?,
            analyzed=1, analysis_error=NULL, analyzed_at=CURRENT_TIMESTAMP WHERE path=?""",
            (result["bpm"], result["musical_key"], result["camelot"], result["energy"], path))
        con.commit()
    finally:
        con.close()

def mark_analysis_error(path, message):
    con = connect()
    try:
        con.execute("UPDATE tracks SET analysis_error=? WHERE path=?", (str(message)[:400], path))
        con.commit()
    finally:
        con.close()

def pending_analysis(limit=None):
    con = connect()
    try:
        query = "SELECT path FROM tracks WHERE analyzed=0 AND (analysis_error IS NULL OR analysis_error='') ORDER BY id"
        if limit is not None:
            return [r[0] for r in con.execute(query+" LIMIT ?", (limit,))]
        return [r[0] for r in con.execute(query)]
    finally:
        con.close()
