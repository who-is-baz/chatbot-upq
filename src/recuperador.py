"""Recuperador de fragmentos oficiales dentro de la intención predicha.

Busca en data/fragmentos/fragmentos_upq.csv con TF-IDF + similitud coseno, pero solo
entre los fragmentos de la intención que dio el router. Si ninguno se parece lo
suficiente, regresa una lista vacía y el orquestador usa la respuesta corta.
"""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocesamiento import limpiar_texto

RAIZ = Path(__file__).resolve().parent.parent
FRAGMENTOS = RAIZ / "data" / "fragmentos" / "fragmentos_upq.csv"

# Similitud mínima para considerar que un fragmento responde la pregunta.
UMBRAL_SIMILITUD = 0.10


@dataclass
class Fragmento:
    id: str
    intencion: str
    titulo: str
    texto: str
    fuente: str
    imagen: str | None
    vigencia: str
    similitud: float


_df = pd.read_csv(FRAGMENTOS).fillna({"imagen": "", "vigencia": ""})
# El título pesa: se repite para que cuente más que el cuerpo del fragmento.
_documentos = (_df["titulo"] + " " + _df["titulo"] + " " + _df["texto"]).map(limpiar_texto)
_vectorizador = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
_matriz = _vectorizador.fit_transform(_documentos)


def buscar(texto: str, intencion: str, k: int = 1, umbral: float = UMBRAL_SIMILITUD) -> list[Fragmento]:
    """Devuelve hasta k fragmentos de la intención con similitud >= umbral, del más parecido al menos."""
    indices = _df.index[_df["intencion"] == intencion]
    if len(indices) == 0:
        return []
    consulta = _vectorizador.transform([limpiar_texto(texto)])
    similitudes = cosine_similarity(consulta, _matriz[indices])[0]
    orden = similitudes.argsort()[::-1][:k]

    resultado = []
    for pos in orden:
        if similitudes[pos] < umbral:
            break
        fila = _df.loc[indices[pos]]
        resultado.append(Fragmento(
            id=fila["id"], intencion=fila["intencion"], titulo=fila["titulo"], texto=fila["texto"],
            fuente=fila["fuente"], imagen=fila["imagen"] or None, vigencia=fila["vigencia"],
            similitud=float(similitudes[pos]),
        ))
    return resultado
