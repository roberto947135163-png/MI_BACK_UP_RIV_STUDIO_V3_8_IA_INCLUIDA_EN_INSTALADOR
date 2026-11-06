"""Opt-in downloader for non-commercial evaluation; no credentials required."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import urllib.request
from app.core.pretrained_genre import MODEL_URL,META_URL,MODEL_NAME,META_NAME
from app.core.database import APP_DIR

def download():
    target=APP_DIR/'models';target.mkdir(parents=True,exist_ok=True)
    for url,name in [(MODEL_URL,MODEL_NAME),(META_URL,META_NAME)]:
        dest=target/name
        print('Downloading',name)
        temp=dest.with_suffix(dest.suffix+'.part')
        try:
            urllib.request.urlretrieve(url,temp)
            temp.replace(dest)
        finally:
            temp.unlink(missing_ok=True)
    print('Installed in',target)

if __name__=='__main__':
    print('Models are CC BY-NC-SA 4.0: non-commercial evaluation only.')
    if input('Type YES to accept and download: ').strip()=='YES':download()
