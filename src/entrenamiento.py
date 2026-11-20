"""Entrenamiento mínimo (versión semilla). La comparativa completa va en el notebook."""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.preprocesamiento import limpiar_texto

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "models"


def main() -> None:
    corpus = pd.read_csv(RAIZ / "data" / "corpus_upq.csv")
    X_texto = corpus["texto"].map(limpiar_texto)
    y = corpus["intencion"]

    vectorizador = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    X = vectorizador.fit_transform(X_texto)

    modelo = LogisticRegression(max_iter=1000, random_state=42)
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
