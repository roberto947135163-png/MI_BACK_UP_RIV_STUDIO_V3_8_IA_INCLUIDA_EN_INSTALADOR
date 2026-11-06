# MI BACK UP V3.6 PERSONAL — IA ONNX bajo demanda

## Uso
1. Sube todo el contenido del ZIP (incluida la carpeta `.github`) a la raíz del repositorio GitHub.
2. GitHub → Actions → Build Windows Installer → Run workflow. Descarga el artefacto y ejecuta `MI_BACK_UP_SETUP.exe`.
3. Abre MI BACK UP → `IA: Géneros` → `Instalar IA gratuita para uso personal`. Confirma la licencia **CC BY-NC-SA 4.0**. La aplicación descarga los pesos oficiales una sola vez desde Essentia y los guarda en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/models`.
4. `IA: Géneros` → `Clasificar audio con IA ONNX`; selecciona canciones o lotes de 25/100. Los resultados quedan en la base de datos y los archivos originales no se mueven.

## Límites importantes
- Los pesos ONNX **no están incluidos** en el ZIP ni en el instalador. La descarga inicial requiere Internet; el análisis posterior funciona offline.
- El frontend de audio es una aproximación con librosa al de Essentia. **No se ha validado la precisión con canciones reales**. No garantiza distinguir Afro House de Tribal House ni géneros exactos.
- El análisis ONNX usa 2 hilos CPU y se realiza en segundo plano. La interfaz usa carga progresiva; no se garantiza ausencia total de lag en todas las máquinas.
- Los pesos tienen licencia no comercial CC BY-NC-SA 4.0; no vender ni redistribuir los pesos sin autorización.
- GitHub Actions y la instalación Windows no se han ejecutado aquí. Compilar y verificar en GitHub antes de usar.
