from pathlib import Path

class OfflineGenreEngine:
    # Adaptador seguro: no emite predicciones si falta el modelo o su preprocesamiento.
    def __init__(self, model_path="models/genre_classifier.onnx"):
        self.model_path=Path(model_path)
        self.session=None
        self.error=None
        if self.model_path.exists():
            try:
                import onnxruntime as ort
                self.session=ort.InferenceSession(str(self.model_path),providers=["CPUExecutionProvider"])
            except Exception as exc:
                self.error=str(exc)

    def classify(self, audio_path):
        if self.session is None:
            return {"status":"model_missing","genre":"05 - POR CLASIFICAR","confidence":0.0,
                    "message":"Modelo ONNX no instalado; no se inventa una clasificación."}
        return {"status":"preprocessing_required","genre":"05 - POR CLASIFICAR","confidence":0.0,
                "message":"Configurar preprocesamiento y etiquetas del modelo seleccionado."}
