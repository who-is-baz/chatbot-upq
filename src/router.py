"""Router: clasifica la intención de una pregunta ya limpia."""
from pathlib import Path

import joblib

MODELOS = Path(__file__).resolve().parent.parent / "models"
_modelo = joblib.load(MODELOS / "modelo.pkl")
_vectorizador = joblib.load(MODELOS / "vectorizador.pkl")


def predecir(texto_limpio: str) -> dict:
    """Devuelve {"intencion", "confianza", "top3": [(intencion, prob), ...]}."""
    X = _vectorizador.transform([texto_limpio])
    probs = _modelo.predict_proba(X)[0]
    orden = probs.argsort()[::-1][:3]
    top3 = [(str(_modelo.classes_[i]), float(probs[i])) for i in orden]
    return {"intencion": top3[0][0], "confianza": top3[0][1], "top3": top3}
