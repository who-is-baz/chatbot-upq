"""Pruebas de la rotación de preguntas sugeridas."""
import json
import random
from pathlib import Path

from src.sugeridas import siguiente_tanda

TODAS = [f"p{i}" for i in range(20)]


def test_no_repite_hasta_mostrar_todas():
    rng, vistas, mostradas = random.Random(1), [], []
    for _ in range(4):
        tanda, vistas = siguiente_tanda(TODAS, vistas, rng=rng)
        assert len(tanda) == 5
        mostradas += tanda
    assert sorted(mostradas) == sorted(TODAS)  # 4 tandas = las 20, ninguna repetida


def test_al_acabarse_vuelve_a_barajar():
    rng, vistas = random.Random(2), []
    for _ in range(4):
        _, vistas = siguiente_tanda(TODAS, vistas, rng=rng)
    tanda, vistas = siguiente_tanda(TODAS, vistas, rng=rng)
    assert len(tanda) == 5 and len(set(tanda)) == 5
    assert vistas == tanda  # empieza un ciclo nuevo


def test_lista_que_no_es_multiplo_de_5():
    todas = [f"p{i}" for i in range(7)]
    rng = random.Random(3)
    tanda1, vistas = siguiente_tanda(todas, [], rng=rng)
    tanda2, vistas = siguiente_tanda(todas, vistas, rng=rng)
    assert len(tanda2) == 5 and len(set(tanda2)) == 5
    assert set(todas) - set(tanda1) <= set(tanda2)  # las 2 que faltaban salen en la segunda tanda


def test_config_tiene_al_menos_15_preguntas_distintas():
    config = json.loads(Path("config/asistente.json").read_text(encoding="utf-8"))
    preguntas = config["preguntas_sugeridas"]
    assert len(preguntas) >= 15 and len(set(preguntas)) == len(preguntas)


def test_ciclo_nuevo_no_repite_la_tanda_anterior():
    for semilla in range(30):
        rng, vistas, tanda = random.Random(semilla), [], []
        for _ in range(4):
            tanda, vistas = siguiente_tanda(TODAS, vistas, rng=rng)
        nueva, _ = siguiente_tanda(TODAS, vistas, rng=rng)
        assert not set(nueva) & set(tanda)


# ---------------------------------------------------------------- sugerencia relacionada (placeholder)
from src.sugeridas import sugerencia_relacionada  # noqa: E402

POR_INTENCION = {"becas": ["¿Qué tipos de becas hay?"], "costos_pagos": ["¿Cuánto cuesta la reinscripción?"],
                 "titulacion": ["¿Cuánto cuesta titularme?"]}
LISTA = [p for ps in POR_INTENCION.values() for p in ps]


def test_sugiere_de_la_misma_intencion():
    top3 = [("becas", 0.9), ("costos_pagos", 0.05), ("admision", 0.01)]
    assert sugerencia_relacionada(POR_INTENCION, top3, set(), LISTA) == "¿Qué tipos de becas hay?"


def test_si_ya_se_hizo_sugiere_una_vecina_del_top3():
    top3 = [("becas", 0.9), ("costos_pagos", 0.05), ("admision", 0.01)]
    ya = {"¿Qué tipos de becas hay?"}
    assert sugerencia_relacionada(POR_INTENCION, top3, ya, LISTA) == "¿Cuánto cuesta la reinscripción?"


def test_sin_relacionadas_toma_cualquiera_nueva_y_none_al_final():
    top3 = [("admision", 0.9)]
    assert sugerencia_relacionada(POR_INTENCION, top3, set(LISTA[:2]), LISTA) == LISTA[2]
    assert sugerencia_relacionada(POR_INTENCION, top3, set(LISTA), LISTA) is None
