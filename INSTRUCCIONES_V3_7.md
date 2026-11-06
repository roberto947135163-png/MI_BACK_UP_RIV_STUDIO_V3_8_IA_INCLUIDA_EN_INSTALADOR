# MI BACK UP V3.7 — desplazamiento y certificados

## Biblioteca
La tabla de **Todos los temas** ahora usa `QTableView` + `QAbstractTableModel`: Qt solo dibuja las filas visibles, aunque la biblioteca contenga 12,496 canciones. La rueda del ratón desplaza toda la lista y las filas anteriores dejan de estar pintadas al salir de pantalla. La selección y el arrastre a VirtualDJ siguen utilizando la ruta del archivo.

## Error CERTIFICATE_VERIFY_FAILED
Se añadió soporte para los certificados del sistema Windows (`truststore`) y para el paquete `certifi`. **No se desactiva la verificación HTTPS**.

Si la descarga sigue fallando, descarga manualmente los dos archivos desde las direcciones oficiales indicadas en `app/core/pretrained_genre.py` y cópialos en:

`%USERPROFILE%\\Documents\\BACKUP_DJ_ROBERTO_RIVERA\\models`

Nombres esperados:
- `discogs-effnet-bsdynamic-1.onnx`
- `discogs-effnet-bsdynamic-1.json`

**Limitación importante:** el adaptador de audio de V3.6 utiliza una aproximación de mel-espectrograma, no el preprocesamiento validado de Essentia. Por tanto **no está garantizado que clasifique correctamente**. Esta versión arregla el problema de navegación y mejora la descarga, pero no certifica la precisión del modelo. Si se obtiene un error al inferir, es necesario depurar la compatibilidad de entrada/salida con el modelo real.

## GitHub
Sube todo el contenido de este ZIP a la raíz del repositorio y ejecuta `Actions → Build Windows Installer → Run workflow`. El ZIP contiene el código fuente, no el instalador compilado. Guarda una copia de `Documentos/BACKUP_DJ_ROBERTO_RIVERA` antes de instalar.
