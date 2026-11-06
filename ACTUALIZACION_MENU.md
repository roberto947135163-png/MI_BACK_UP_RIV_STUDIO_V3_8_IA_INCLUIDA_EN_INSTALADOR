# BACK UP V2.2 - Corrección del menú lateral

## Error confirmado
En `app/ui/main_window.py`, el menú anterior creaba botones mediante `sv.addWidget(QPushButton(name))`, sin conectar sus señales `clicked` a funciones. Por ello eran botones inertes.

## Corrección
- Inicio / Todos los temas: restablecen la biblioteca completa.
- Géneros: selector y filtro por género existente.
- Playlists: permite agregar/quitar canciones seleccionadas y mostrar listas guardadas en SQLite.
- Favoritos: permite agregar/quitar canciones seleccionadas y filtrar favoritos.
- Analizar disco: abre el selector de carpeta.
- Duplicados: muestra los grupos con hashes SHA-256 ya registrados; avisa explícitamente cuando no hay hashes calculados. **No realiza búsqueda exhaustiva ni borra archivos**.
- Configuración: muestra ubicación de la base de datos y las opciones operativas actuales. No es aún una pantalla completa de preferencias.

## Precauciones
Haz una copia de seguridad de `Documentos/BACKUP_DJ_ROBERTO_RIVERA` antes de actualizar. No borres `library.sqlite3` ni los archivos `-wal` y `-shm` mientras la aplicación esté abierta. No es necesario volver a escanear G:.

## Pruebas
Las pruebas automatizadas y de sintaxis se ejecutan en Linux. Falta validar el ejecutable y la interfaz real en Windows, y probar el arrastre con VirtualDJ tras esta actualización. La clasificación de géneros sigue basada en entrenamiento local, NO en un modelo universal preentrenado.
