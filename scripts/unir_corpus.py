"""Une los corpus por responsable en data/corpus_upq.csv."""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
COLUMNAS = ["texto", "intencion", "respuesta", "fuente"]


def main() -> None:
    archivos = sorted((RAIZ / "data" / "intenciones").glob("*.csv"))
    corpus = pd.concat([pd.read_csv(a) for a in archivos], ignore_index=True)
    assert list(corpus.columns) == COLUMNAS, f"Columnas inesperadas: {list(corpus.columns)}"
    corpus = corpus.drop_duplicates(subset=["texto"]).dropna()
    corpus.to_csv(RAIZ / "data" / "corpus_upq.csv", index=False)
    print(f"{len(corpus)} filas, {corpus['intencion'].nunique()} intenciones -> data/corpus_upq.csv")


if __name__ == "__main__":
    main()
