# Diagnóstico técnico — BACK UP - DJ ROBERTO RIVERA

## Error de inicio observado

El mensaje `No module named 'app.ui.main_window'` indica que el ejecutable no encuentra el módulo de interfaz al iniciar.

## Defectos comprobados en el ZIP recibido

1. `app/ui/main_window.py` tenía una cadena de texto partida por un salto de línea dentro de comillas dobles. Esto producía `SyntaxError: unterminated string literal` al compilar/importar el módulo.
2. El archivo `.spec` no declaraba explícitamente los submódulos de `app`. Se reforzó la recopilación de imports para que PyInstaller incluya el paquete de interfaz y sus módulos.
3. El workflow original no ejecutaba pruebas ni verificaba explícitamente la importación de `app.ui.main_window` antes de empaquetar.

## Correcciones aplicadas

- Se corrigió la cadena multilínea usando `\n`.
- El `.spec` usa `collect_submodules("app")` y conserva la recopilación de recursos de las dependencias.
- GitHub Actions ahora compila todos los `.py`, prueba la importación de la ventana, ejecuta pytest y comprueba la existencia del EXE y del instalador antes de subirlos.

## Verificación ejecutada en este entorno

- `python -m compileall -q`: correcto.
- `python -m pytest -q`: 2 pruebas aprobadas.
- No se pudo ejecutar PyInstaller ni probar Qt/instalador aquí: este entorno no tiene PySide6 instalado y no es Windows. La validación final de compilación debe realizarse en el runner Windows de GitHub Actions.

## Funciones que todavía NO están terminadas

Esta entrega es una corrección de la base recibida, no una aplicación final con todas las funciones del prompt maestro.

- IA musical: no hay modelo ONNX incluido; el motor es solamente un adaptador y no predice géneros.
- BPM, tonalidad Camelot y energía: no implementados.
- SHA-256: existe una utilidad, pero el escáner no calcula ni guarda el hash.
- Playlists, favoritos, filtros avanzados, portadas y visualizador: no implementados.
- Escáner: recorre archivos y lee metadatos, pero no tiene pausa/reanudación persistente ni detección robusta de desconexión.
- Organización: copia a `05 - POR CLASIFICAR`; no implementa toda la taxonomía ni historial/restauración de operaciones.
- Reproductor: controles básicos; no hay cola, anterior/siguiente ni visualizador.
- Drag & drop: envía rutas locales con `QMimeData.setUrls`; debe probarse en el VirtualDJ instalado para confirmar el destino real.
- La instalación de Windows y su desinstalación aún requieren validación en una máquina Windows.

## Siguiente paso recomendado

Subir el contenido de esta carpeta al repositorio GitHub (manteniendo `main.py`, `app/`, el `.spec`, `requirements.txt`, `installer/` y `.github/` en la raíz del repositorio) y ejecutar Actions. Si falla, compartir el log completo del primer paso rojo.
