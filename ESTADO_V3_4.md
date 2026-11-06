# MI BACK UP V3.4 — corrección de interfaz

## Corregido
- Carga inicial de SQLite, predicciones y géneros en QThread, sin bloquear el hilo gráfico.
- Tabla de canciones limitada a 100 filas visibles, renderizada por tandas de 20.
- Columnas con ancho interactivo: elimina ResizeToContents, que recorría muchas celdas.
- Carpetas virtuales muestran máximo 100 registros por vista.
- Relectura de biblioteca después de analizar géneros.

## IA ONNX: estado real
- El motor `app/core/pretrained_genre.py` usa onnxruntime y audio PCM, no nombres ni etiquetas.
- NO se incluye un modelo preentrenado compatible con sus pesos, etiquetas y preprocesamiento verificados.
- El botón IA: Géneros advertirá que falta el modelo en vez de fingir resultados.
- Un modelo cualquiera `.onnx` no es intercambiable: hay que adaptar frecuencia de muestreo, entrada, ventanas y salida.
- No hay precisión de género exacta garantizada; las predicciones inciertas deben quedar en Por clasificar.

## Pruebas
- `python -m compileall -q main.py app tests`
- `python -m pytest -q` (15 aprobadas en entorno Linux sin PySide6)
- No se ha ejecutado Windows, VirtualDJ ni un modelo real de clasificación.

## Instalación
- Respaldar `Documentos/BACKUP_DJ_ROBERTO_RIVERA` antes de actualizar.
- Recompilar en GitHub Actions.
- No eliminar la biblioteca SQLite ni los archivos del disco G:.
