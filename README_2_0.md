# BACK UP — actualización de análisis BPM/KEY

Se conserva la base SQLite en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/library.sqlite3` (ruta `Path.home()/Documents/...`). La migración agrega columnas sin borrar registros. **Antes de actualizar, copia ese archivo y los archivos `library.sqlite3-wal` / `library.sqlite3-shm` si existen, con la aplicación cerrada.**

## Uso

1. Instala la nueva versión compilada en GitHub Actions.
2. Abre la biblioteca existente; no es necesario volver a escanear.
3. Pulsa `Analizar BPM / Key` y confirma. Analiza hasta 90 segundos por canción con CPU, una a la vez, y guarda cada resultado.
4. Para detener de forma ordenada, pulsa `Detener análisis`; espera que termine la canción en curso. Al reabrir, `Analizar BPM / Key` retoma las canciones pendientes.
5. Los fallos quedan en `analysis_error` y no se repiten automáticamente. Consulta SQLite para diagnosticarlos.

## Limitaciones verificadas del código

- BPM y tonalidad son estimaciones; pueden fallar, especialmente con ritmos sincopados y cambios armónicos. No reemplazan una comprobación auditiva.
- Energía es una medida aproximada de amplitud RMS, **no** una clasificación perceptual de energía.
- La IA ONNX para géneros sigue sin modelo ni preprocesamiento; no hay clasificación automática real.
- El análisis lee 90 segundos iniciales; los formatos requieren soporte de decodificación de librosa/soundfile/audioread en Windows.
- El instalador EXE se genera mediante GitHub Actions en Windows; no se ha ejecutado ni validado en un PC Windows desde este entorno.
- Se recomienda hacer una prueba con pocos archivos antes de analizar toda la colección.
- No uses Organizar selección con toda la colección hasta verificar el organizador.
