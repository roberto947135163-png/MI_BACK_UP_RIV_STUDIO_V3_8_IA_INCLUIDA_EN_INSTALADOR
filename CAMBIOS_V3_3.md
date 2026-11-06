# MI BACK UP V3.3 — Local y sin Google Drive

- Se eliminó el botón Google Drive y el explorador OAuth/streaming de la interfaz.
- Se retiraron las dependencias de Google Drive del requirements.txt.
- Géneros organizados mediante taxonomía cerrada de géneros y subgéneros musicales.
- Ejemplo: ELECTRÓNICA / AFRO HOUSE.
- Nombres como «Variado», «Pack Vol 1» y etiquetas no verificadas no se convierten en géneros.
- Si no hay predicción de audio válida ni corrección manual, se muestra POR CLASIFICAR / SIN CLASIFICAR.
- La biblioteca se organiza virtualmente: no se crean carpetas físicas dentro del EXE ni se mueven canciones del disco.

## Pendiente fundamental
El motor ONNX necesita un modelo musical **real y compatible** y un archivo de clases. No están incluidos en este ZIP. Sin ellos no hay clasificación automática por sonido. La conexión opcional a Internet para verificar predicciones tampoco está implementada. No existe garantía de género exacto: toda clasificación automática tiene incertidumbre.

## Antes de instalar
Respalda Documentos/BACKUP_DJ_ROBERTO_RIVERA; conserva el disco G: y los archivos originales. El instalador Windows y el funcionamiento real en tu PC deben verificarse después de compilar.
