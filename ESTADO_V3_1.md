# MI BACK UP V3.1 — Drive hacia VirtualDJ

## Implementado
- Selección múltiple de audios en el navegador Google Drive.
- Botón **Preparar selección para VirtualDJ**: descarga solo los audios seleccionados en una caché local de la app; no descarga toda la biblioteca.
- Arrastre nativo desde la lista de Drive de los archivos ya preparados, mediante QDrag y QUrl.fromLocalFile.
- Cancelación de preparación, validación de tamaño, nombres de archivo saneados y limpieza de archivos incompletos.
- Botón **Limpiar caché temporal** con confirmación; **no limpiar mientras VirtualDJ use esos archivos**.
- La clasificación IA sigue limitada a los audios locales. No se ejecuta IA sobre Drive.

## Limitaciones verificables
- VirtualDJ no acepta de forma garantizada URLs privadas de Google Drive; es necesaria una copia temporal local de las canciones que se arrastren.
- El código de Drive necesita autorización OAuth real. No se pudo probar con una cuenta del usuario.
- No se ha incorporado el modelo musical preentrenado: el adaptador ONNX existente requiere pesos y manifiesto compatibles, ver MODELO_IA.md. No debe anunciarse clasificación automática universal.
- La descarga por lotes usa el hilo de interfaz con processEvents para permitir cancelar: con conexiones lentas puede bloquear brevemente. Conviene migrar a un trabajador QThread.
- No se ha validado la compatibilidad con VirtualDJ para pistas de Drive en Windows; se requiere prueba manual.
- Las canciones preparadas ocupan espacio en el disco hasta que el usuario borre la caché. No hay sincronización offline de Drive.
