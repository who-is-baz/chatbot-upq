"""Entrena el clasificador de intenciones y guarda los modelos en models/."""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.preprocesamiento import limpiar_texto

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "models"
# C=10: mejor F1 macro en el notebook; los umbrales se calibran con este mismo valor
# en scripts/calibrar_umbrales.py.
C_REGULARIZACION = 10


def crear_modelo():
    """Vectorizador y clasificador con los mismos parámetros que el notebook."""
    vectorizador = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    modelo = LogisticRegression(C=C_REGULARIZACION, max_iter=1000, random_state=42)
    return vectorizador, modelo


def main() -> None:
    corpus = pd.read_csv(RAIZ / "data" / "corpus_upq.csv")
    X_texto = corpus["texto"].map(limpiar_texto)
    y = corpus["intencion"]

    vectorizador, modelo = crear_modelo()
    X = vectorizador.fit_transform(X_texto)
    modelo.fit(X, y)

    MODELOS.mkdir(exist_ok=True)
    joblib.dump(modelo, MODELOS / "modelo.pkl")
    joblib.dump(vectorizador, MODELOS / "vectorizador.pkl")
    config = MODELOS / "config.json"
    if not config.exists():
        config.write_text(json.dumps({"umbral_alto": 0.6, "umbral_bajo": 0.35}, indent=2))
    print(f"Modelo entrenado con {len(corpus)} ejemplos y {y.nunique()} intenciones.")


if __name__ == "__main__":
    main()