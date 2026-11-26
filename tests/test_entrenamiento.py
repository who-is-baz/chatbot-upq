import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from src import router
from src.entrenamiento import C_REGULARIZACION, crear_modelo
from src.preprocesamiento import limpiar_texto


def test_crear_modelo_usa_la_configuracion_elegida():
    vectorizador, modelo = crear_modelo()
    assert isinstance(modelo, LogisticRegression)
    assert modelo.C == C_REGULARIZACION == 10
    assert vectorizador.analyzer == "char_wb"
    assert vectorizador.sublinear_tf


def test_el_modelo_conoce_todas_las_intenciones_del_corpus():
    corpus = pd.read_csv("data/corpus_upq.csv")
    assert set(router._modelo.classes_) == set(corpus.intencion)


@pytest.mark.parametrize("pregunta, intencion", [
    ("cuándo empiezan las clases", "calendario_escolar"),
    ("hola", "saludo"),
    ("muchas gracias", "agradecimiento"),
])
def test_router_predice_intenciones_claras(pregunta, intencion):
    r = router.predecir(limpiar_texto(pregunta))
    assert r["intencion"] == intencion
    assert len(r["top3"]) == 3
    assert 0 <= r["confianza"] <= 1
