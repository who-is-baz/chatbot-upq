"""Calibra los umbrales de confianza con validación cruzada y preguntas fuera de alcance.

- umbral_bajo: por debajo, el chatbot da el mensaje de no reconocido (fallback).
- umbral_alto: desde aquí responde directo; entre los dos pregunta "¿Quisiste decir...?".
Las preguntas fuera de alcance nunca se usan para entrenar: solo para elegir y medir los umbrales.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_predict  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.entrenamiento import crear_modelo  # noqa: E402
from src.guardrails import validar_entrada  # noqa: E402
from src.preprocesamiento import limpiar_texto  # noqa: E402

META_RECHAZO = 0.80      # fracción de preguntas ajenas que el fallback debe rechazar
PRECISION_MINIMA = 0.95  # acierto mínimo de las respuestas directas
MINIMO_CASOS = 5         # casos mínimos sobre umbral_alto para confiar en esa precisión


def main():
    corpus = pd.read_csv(RAIZ / "data" / "corpus_upq.csv")
    fuera = pd.read_csv(RAIZ / "data" / "fuera_de_alcance.csv")
    # Las que ya rechazan los guardrails nunca llegan al modelo.
    fuera = fuera[[validar_entrada(t)[0] for t in fuera.texto]]

    X, y = corpus.texto.map(limpiar_texto), corpus.intencion.to_numpy()
    vectorizador, modelo = crear_modelo()
    pipe = Pipeline([("tfidf", vectorizador), ("clf", modelo)])
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    proba = cross_val_predict(pipe, X, y, cv=folds, method="predict_proba")
    clases = np.unique(y)
    conf, acierto = proba.max(axis=1), clases[proba.argmax(axis=1)] == y
    conf_fuera = pipe.fit(X, y).predict_proba(fuera.texto.map(limpiar_texto)).max(axis=1)

    bajo = round(float(np.quantile(conf_fuera, META_RECHAZO)), 2)
    candidatos = [t for t in np.round(np.arange(bajo, 1.0, 0.01), 2)
                  if (conf >= t).sum() >= MINIMO_CASOS and acierto[conf >= t].mean() >= PRECISION_MINIMA
                  and not (conf_fuera >= t).any()]
    alto = float(candidatos[0]) if candidatos else 1.0

    directo, medio = conf >= alto, (conf >= bajo) & (conf < alto)
    print(f"Preguntas válidas: {len(y)} (validación cruzada) | fuera de alcance: {len(conf_fuera)}")
    print(f"umbral_bajo = {bajo} | umbral_alto = {alto}")
    print(f"Respuesta directa: {directo.mean():.0%} de las válidas, con {acierto[directo].mean():.0%} de acierto")
    print(f"¿Quisiste decir...?: {medio.mean():.0%} | Fallback: {(conf < bajo).mean():.0%} de las válidas")
    print(f"Fuera de alcance rechazadas: {(conf_fuera < bajo).mean():.0%} | "
          f"con respuesta directa: {(conf_fuera >= alto).mean():.0%}")

    config = {"umbral_alto": alto, "umbral_bajo": bajo}
    (RAIZ / "models" / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    umbrales = np.linspace(0, 1, 101)
    plt.figure(figsize=(8, 4.5))
    plt.plot(umbrales, [(conf >= t).mean() for t in umbrales], label="Válidas que pasan el umbral")
    plt.plot(umbrales, [(conf_fuera >= t).mean() for t in umbrales], label="Fuera de alcance que pasan el umbral")
    plt.axvline(bajo, color="gray", linestyle="--", label=f"umbral_bajo = {bajo}")
    plt.axvline(alto, color="black", linestyle=":", label=f"umbral_alto = {alto}")
    plt.xlabel("Umbral de confianza")
    plt.ylabel("Proporción")
    plt.title("Calibración del umbral")
    plt.legend()
    plt.tight_layout()
    (RAIZ / "docs").mkdir(exist_ok=True)
    plt.savefig(RAIZ / "docs" / "curva_umbral.png", dpi=120)
    print("Guardado: models/config.json y docs/curva_umbral.png")


if __name__ == "__main__":
    main()