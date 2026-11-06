# BACK UP - DJ ROBERTO RIVERA

Proyecto inicial para Windows 11 x64: interfaz PySide6, biblioteca SQLite, escaneo de carpetas, metadatos, duplicados exactos, reproductor básico, organización segura y arrastrar archivos locales hacia VirtualDJ.

## Estado
Esta es una base funcional inicial. La clasificación IA offline requiere seleccionar, licenciar e integrar un modelo ONNX y su preprocesamiento. El motor incluido detecta honestamente que el modelo falta; no inventa géneros. BPM/Key quedan como campos preparados para integrar y validar el analizador.

## Ejecutar
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## GitHub
Sube todo el contenido al repositorio. En Actions ejecuta **Build Windows Installer** y descarga `BACKUP-DJ-ROBERTO-RIVERA-Windows`.

## Seguridad
El escaneo no modifica archivos. La organización muestra vista previa y copia por defecto. No elimina duplicados ni sobrescribe destinos. Haz copia de seguridad antes de reorganizar una colección irreemplazable.

## Drag & drop
Selecciona canciones en la tabla y arrástralas hacia VirtualDJ. Se envían rutas locales mediante `text/uri-list`. El destino exacto (navegador/deck) debe probarse con la versión instalada.
