# IA musical preentrenada — estado real

El proyecto incluye **un adaptador ONNX** que analiza muestras de audio, no nombres ni etiquetas.
No se distribuye ningún modelo entrenado dentro del ZIP. **No clasifica hasta instalar uno compatible.**

Coloca en `Documentos/BACKUP_DJ_ROBERTO_RIVERA/models/`:
- `genre_model.onnx` (modelo preentrenado compatible con entrada float32 `[1, sample_rate * input_seconds]` y salida `[1, n_labels]`)
- `genre_labels.json` por ejemplo `{"labels":["House","Techno"],"sample_rate":16000,"input_seconds":20,"output":"logits","version":"identificador-real-del-modelo"}`

**Importante:** modelos conocidos como Discogs-EffNet suelen utilizar entradas de espectrograma o arquitecturas distintas y **NO** son compatibles directamente con este adaptador. Requieren un preprocesador específico, conversión y validación. No renombres cualquier ONNX y esperes que funcione.

Los resultados son predicciones, no verdades garantizadas. Confianza baja: `POR CLASIFICAR`. No se cambian los originales. El clasificador experimental entrenado por etiquetas sigue disponible separadamente, pero **no se usa en el botón de clasificación preentrenada**.

Para cumplir el requisito de IA lista para todos los géneros se necesita adquirir e integrar un modelo con licencia apropiada, formato de entrada documentado y evaluación sobre música real. Esa fase está pendiente.
