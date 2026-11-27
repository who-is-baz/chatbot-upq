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
