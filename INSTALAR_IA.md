# Modelo ONNX musical — MI BACK UP

Modelo real: Discogs-EffNet (400 estilos) de Essentia/MTG.

**Licencia importante:** los pesos MTG están publicados bajo CC BY-NC-SA 4.0 (uso no comercial). Para distribuirlos en un producto comercial RIV STUDIO es necesario solicitar una licencia apropiada al titular. Por ello **NO se incluyen los pesos** en este ZIP ni se descargan automáticamente en GitHub Actions.

## Evaluación personal no comercial

1. Instala MI BACK UP con el instalador de GitHub Actions.
2. Ejecuta `python scripts/install_discogs_model.py` desde el código fuente en tu PC (requiere conexión una sola vez), o descarga manualmente el ONNX y JSON desde el sitio oficial de Essentia.
3. El script guarda los dos archivos en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/models`.
4. Reinicia la aplicación y pulsa IA: Géneros → Clasificar con ONNX. El análisis local no requiere Internet.

**Limitación de precisión:** el preprocesamiento mel de esta integración está aproximado con librosa; NO está validado aún contra el preprocesamiento de referencia Essentia. Por tanto los resultados son experimentales y no deben considerarse géneros exactos. Se requiere una comparación contra inferencia de referencia y pruebas con canciones etiquetadas por un DJ antes de organizar automáticamente miles de canciones.

No se utilizan nombres, carpetas ni etiquetas ID3 para predecir géneros. Las carpetas de géneros son virtuales. Nunca se modifican los originales.
