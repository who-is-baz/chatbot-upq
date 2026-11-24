"""Une data/intenciones/*.csv en data/corpus_upq.csv y valida su calidad."""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.preprocesamiento import limpiar_texto  # noqa: E402

COLUMNAS = ["texto", "intencion", "respuesta", "fuente"]
SALIDA = RAIZ / "data" / "corpus_upq.csv"


def main():
    archivos = sorted((RAIZ / "data" / "intenciones").glob("*.csv"))
    assert archivos, "No hay CSV en data/intenciones/"

    corpus = pd.concat([pd.read_csv(a) for a in archivos], ignore_index=True)
    assert list(corpus.columns) == COLUMNAS, f"Columnas inesperadas: {list(corpus.columns)}"

    # 1) Nulos: se avisa antes de quitarlos
    nulos = corpus[corpus.isna().any(axis=1)]
    if len(nulos):
        print(f"AVISO: {len(nulos)} fila(s) con valores vacíos, se descartan:")
        print(nulos[["texto", "intencion"]].to_string())
    corpus = corpus.dropna().copy()

    # 2) Conflictos: mismo texto limpio con intenciones distintas -> error
    corpus["_limpio"] = corpus["texto"].map(limpiar_texto)
    n_intenciones = corpus.groupby("_limpio")["intencion"].nunique()
    conflictos = n_intenciones[n_intenciones > 1].index
    if len(conflictos):
        print("ERROR: textos con más de una intención:")
        detalle = corpus[corpus["_limpio"].isin(conflictos)]
        print(detalle[["texto", "intencion"]].sort_values("texto").to_string())
        sys.exit(1)

    # 3) Duplicados (por texto limpio): se quitan y se reporta cuántos
    antes = len(corpus)
    corpus = corpus.drop_duplicates(subset="_limpio")
    if antes - len(corpus):
        print(f"AVISO: {antes - len(corpus)} duplicado(s) eliminado(s) por texto limpio")

    # 4) Una intención debería tener una sola respuesta
    respuestas = corpus.groupby("intencion")["respuesta"].nunique()
    for intencion in respuestas[respuestas > 1].index:
        print(f"AVISO: '{intencion}' tiene {respuestas[intencion]} respuestas distintas")

    corpus = corpus.drop(columns="_limpio")
    corpus.to_csv(SALIDA, index=False)
    print(f"{len(corpus)} filas, {corpus['intencion'].nunique()} intenciones -> {SALIDA}")


if __name__ == "__main__":
    main()