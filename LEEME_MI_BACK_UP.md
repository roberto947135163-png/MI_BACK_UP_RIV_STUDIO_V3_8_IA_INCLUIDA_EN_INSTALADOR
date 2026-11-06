# MI BACK UP — RIV STUDIO · Actualización 2.3

Esta es una actualización del proyecto BACK UP - DJ ROBERTO RIVERA, no una aplicación nueva desde cero. Conserva la base SQLite anterior en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/library.sqlite3` y las rutas reales de las canciones en G:.

## Antes de instalar
1. Cerrar la versión anterior.
2. Copiar la carpeta `Documentos/BACKUP_DJ_ROBERTO_RIVERA` a un lugar seguro (incluye SQLite, modelo entrenado y otros archivos).
3. No borrar ni mover los archivos originales de G:.
4. Subir los archivos del ZIP a la raíz del repositorio de GitHub y ejecutar `Build Windows Installer`.
5. El instalador se genera como `MI_BACK_UP_SETUP.exe`; el ejecutable se llama `MI_BACK_UP.exe`.

## Uso
- **Inicio:** comienza vacío, busca canción/artista/género y muestra coincidencias mientras escribes.
- **Todos los temas:** muestra toda la biblioteca, permite selección múltiple y arrastrar a VirtualDJ.
- **BPM / Key:** analiza selección, primer lote o pendientes, y permite detener después de la canción en curso.
- **IA: Géneros:** primero entrenar con géneros ya etiquetados, luego clasificar selección o lotes de 25/100. Los resultados se guardan en SQLite y aparecen en Géneros.
- **Géneros:** carpetas **virtuales** agrupadas por género y subgénero, sin mover ni copiar archivos físicos. Los subgéneros se pueden corregir con clic derecho.
- **Playlists:** crear carpetas y subcarpetas; desde Todos los temas usar clic derecho > Agregar a playlist, o arrastrar archivos a una carpeta en el árbol. Se guardan referencias, no duplicados de audio.
- **Favoritos:** seleccionar canciones y usar la estrella; aparecen agrupadas en carpetas virtuales por género.
- **Clic derecho:** copiar referencia, pegar en carpeta de playlist, agregar a playlist, mover referencia entre playlists, corregir género/subgénero y marcar favoritos. **Mover** no mueve el archivo real.
- **Configuración:** cambiar nombre visible, propietario y color de acento. Los cambios se guardan localmente.

## Limitaciones declaradas
- El clasificador offline es un modelo entrenado con ejemplos etiquetados del usuario; **no** se incluye un modelo universal preentrenado de géneros. Necesita al menos 2 géneros y 5 canciones etiquetadas por género; las predicciones no son garantía de género correcto.
- Google Drive **NO** está integrado todavía: requiere implementar OAuth 2.0, gestionar consentimiento, tokens y sincronización de archivos. La aplicación funciona offline sin Drive.
- No se crean carpetas físicas de géneros dentro del EXE: una aplicación instalada no es una ubicación adecuada para almacenar miles de archivos musicales. Géneros, playlists y favoritos son carpetas virtuales persistentes en SQLite.
- No se ha probado la ejecución gráfica ni el instalador en Windows desde este entorno. Las pruebas Python unitarias no equivalen a pruebas de interfaz en Windows.
- La clasificación de subgéneros no es automática: por defecto aparece `General` salvo corrección manual. Para clasificación automática fiable por subgénero se necesita un modelo entrenado con esas clases.
- La vista de inicio limita la tabla de coincidencias a 1000 filas por rendimiento; refina la búsqueda para encontrar una canción.

## Seguridad
Los archivos musicales originales nunca se borran ni se renombran por las acciones de playlists, favoritos, géneros, ni por el análisis. Mantén siempre una copia de seguridad de la base de datos antes de actualizar.

## Propiedad
RIV STUDIO
