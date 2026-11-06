"""Verified HTTPS downloads for personal/noncommercial Essentia models.
Never bypass TLS verification or trust arbitrary certificates.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import ssl
import json
from app.core.pretrained_genre import MODEL_URL, META_URL, MODEL_NAME, META_NAME, model_ready


def secure_context():
    # Prefer Windows certificate store when available; certifi handles frozen Python
    # distributions that otherwise cannot find their CA bundle.
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except (ImportError, OSError):
        pass
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def install_model(destination, progress=None):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    for url, filename in ((META_URL,META_NAME),(MODEL_URL,MODEL_NAME)):
        target=destination/filename
        if target.is_file() and target.stat().st_size>(1000000 if filename.endswith('.onnx') else 100):
            continue
        partial=target.with_name(target.name+'.part')
        try:
            request=Request(url,headers={'User-Agent':'MI-BACK-UP-Personal/3.7'})
            try:
                response=urlopen(request,timeout=90,context=secure_context())
            except ssl.SSLCertVerificationError as exc:
                raise RuntimeError('Windows no pudo verificar el certificado HTTPS. Actualiza los certificados del sistema o descarga manualmente los archivos oficiales en la carpeta: '+str(destination)) from exc
            except Exception as exc:
                if 'CERTIFICATE_VERIFY_FAILED' in str(exc):
                    raise RuntimeError('Error de certificado HTTPS. Descarga manualmente los archivos oficiales en: '+str(destination)) from exc
                raise
            with response, partial.open('wb') as output:
                while block:=response.read(1024*1024):
                    output.write(block)
                    if progress:progress(filename,output.tell())
            if partial.stat().st_size<(1000000 if filename.endswith('.onnx') else 100):
                raise ValueError('Descarga incompleta: '+filename)
            if filename.endswith('.json'):
                data=json.loads(partial.read_text(encoding='utf-8'))
                if not isinstance(data,dict) or not isinstance(data.get('classes'),list):
                    raise ValueError('Metadatos del modelo incompatibles')
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
    if not model_ready(destination):
        raise RuntimeError('No se pudo verificar la instalación del modelo')
    return destination
