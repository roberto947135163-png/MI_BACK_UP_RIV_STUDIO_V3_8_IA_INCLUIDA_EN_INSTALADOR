# Google Drive — integración beta

1. En Google Cloud Console crea un proyecto y habilita Google Drive API.
2. Configura pantalla de consentimiento OAuth y añade tu usuario de prueba si está en modo pruebas.
3. Crea credenciales OAuth tipo **Desktop app**, descarga su JSON. Nunca lo subas a GitHub.
4. En MI BACK UP pulsa **Google Drive**, selecciona ese JSON y autoriza en tu navegador.
5. Navega carpetas y haz doble clic sobre un audio. La app usa una pasarela HTTP **solo en 127.0.0.1**, protegida por token aleatorio, para solicitar fragmentos `Range` a Drive. No escribe audios en disco de forma permanente.

**Límites:** se requiere Internet; la reproducción depende del códec admitido por Qt; archivos de Google Docs no son audio; el streaming consume datos de red. No existe sincronización bidireccional ni reproducción offline de Drive. Para analizar audio con IA, habría que descargar/leer temporalmente datos del audio; no está conectado aún el análisis de archivos remotos. VirtualDJ sigue usando rutas de archivos locales: no se promete arrastre de archivos de Drive sin materializarlos.

Seguridad: acceso `drive.readonly`, tokens OAuth guardados localmente en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/drive_oauth_token.json`. Protege ese archivo y nunca lo compartas. La autenticación real requiere autorización del dueño de la cuenta y no se puede probar en un entorno sin credenciales.
