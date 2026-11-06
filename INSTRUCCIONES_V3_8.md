# MI BACK UP V3.8 — IA integrada en el instalador

**Un único modelo:** Discogs-EffNet bsdynamic ONNX (400 estilos). No hay descarga al instalar ni botón de descarga.

1. Sube todos los archivos de este ZIP a la raíz de GitHub.
2. En Actions > Build Windows Installer > Run workflow, GitHub descarga el modelo oficial y lo empaqueta en MI_BACK_UP.exe.
3. Descarga el artefacto y ejecuta MI_BACK_UP_SETUP.exe.
4. Abre IA: Géneros > Clasificar audio con IA ONNX. Prueba primero 25 canciones.

Si GitHub no logra descargar o cargar el modelo, la compilación falla: no produce un instalador sin IA.

**Aviso:** la descarga del modelo ocurre en GitHub Actions, no en el equipo del usuario. Este ZIP fuente NO incluye los 18 MB de pesos ONNX. El ejecutable compilado sí debe incluirlos.

Licencia del modelo CC BY-NC-SA 4.0; solo uso personal no comercial. El preprocesamiento mel sigue siendo aproximado y NO ha sido validado con canciones reales. No se garantiza precisión por subgénero. El modelo puede tener dificultades con estilos especializados.
