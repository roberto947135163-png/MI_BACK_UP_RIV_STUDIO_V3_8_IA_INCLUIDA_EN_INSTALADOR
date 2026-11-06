# BACK UP — DJ ROBERTO RIVERA · V2.1

## Funciones implementadas
- Biblioteca SQLite persistente en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/library.sqlite3`.
- Escaneo, metadatos, reproducción y drag & drop hacia VirtualDJ (confirmado por el usuario en su PC).
- Análisis BPM, tonalidad, Camelot y energía; selección, lotes de 1 a 1000 y biblioteca completa; detener después de la canción actual.
- Clasificación **offline entrenada por el usuario** a partir de características reales de audio (MFCC, chroma, espectro, RMS). No utiliza nombres de archivos como predictor.
- Vista de género sugerido sin sobrescribir las etiquetas originales.
- Organización física **solo por copia** con vista previa, detección de conflictos y verificación SHA-256.

## Uso de la IA
1. Asegúrate de que varias canciones tengan etiquetas de género **correctas** (al menos 5 por género y 2 géneros). Estas etiquetas son los ejemplos de entrenamiento.
2. Pulsa `Entrenar IA local`. Se procesan hasta 20 canciones de referencia por género para limitar consumo.
3. Selecciona canciones sin clasificar y pulsa `Clasificar selección`.
4. Las predicciones con similitud baja se guardan como `POR CLASIFICAR`. La similitud es una medida heurística, **no una probabilidad calibrada**. Comprueba manualmente resultados antes de copiar.
5. Usa `Organizar selección` para previsualizar destinos. Los archivos originales **nunca se mueven ni se eliminan**.

## Limitaciones importantes
- Esta versión **no contiene un modelo ONNX preentrenado**. Es un clasificador local entrenable con tu biblioteca, no un reconocedor universal de géneros listo para usar sin ejemplos. Los subgéneros muy parecidos pueden confundirse.
- No hay garantías de precisión de BPM, tonalidad o género; contrasta con canciones conocidas.
- El entrenamiento de IA y las copias grandes pueden tardar; haz lotes pequeños.
- La organización no escribe etiquetas en archivos de audio. Los resultados quedan en SQLite.
- No se ha probado el nuevo instalador Windows en este entorno. GitHub Actions compila y verifica el artefacto; la prueba final debe hacerse en tu PC.
- Si reinstalas Windows o cambias de PC, haz copia de `library.sqlite3` y `genre_model.json` desde Documentos.

## Instalación
Sube el contenido de la carpeta del proyecto a la raíz de GitHub. Ve a Actions > Build Windows Installer > Run workflow y descarga el instalador de Artifacts. Haz copia de seguridad de la base de datos antes de actualizar.
