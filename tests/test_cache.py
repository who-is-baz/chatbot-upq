"""Pruebas del caché LRU y de su uso en el orquestador."""
import pytest

from src import router
from src.cache import Cache
from src.chatbot import ChatbotUPQ


def test_get_cuenta_aciertos_y_fallos():
    c = Cache()
    assert c.get("a") is None
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.metricas() == {"aciertos": 1, "fallos": 1, "tasa_aciertos": 0.5, "tamano": 1, "capacidad": 128}


def test_saca_el_menos_usado():
    c = Cache(capacidad=2)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")          # "a" se usó hace poco; "b" es la más vieja
    c.set("c", 3)
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3
    assert len(c) == 2


def test_devuelve_copias():
    c = Cache()
    valor = {"respuesta": "hola"}
    c.set("k", valor)
    valor["respuesta"] = "cambiado"
    copia = c.get("k")
    copia["respuesta"] = "otra"
    assert c.get("k")["respuesta"] == "hola"


def test_capacidad_invalida():
    with pytest.raises(ValueError):
        Cache(capacidad=0)


# ---------------------------------------------------------------- en el orquestador
def fijar_prediccion(monkeypatch, intencion, confianza):
    monkeypatch.setattr(router, "predecir", lambda _: {
        "intencion": intencion, "confianza": confianza, "top3": [(intencion, confianza)]})


def test_segunda_pregunta_igual_sale_del_cache(monkeypatch):
    fijar_prediccion(monkeypatch, "becas", 0.99)
    bot = ChatbotUPQ()
    primera = bot.responder("¿Hay becas?")
    segunda = bot.responder("hay becas")   # mismo texto ya limpio
    assert primera["origen"] == "modelo" and segunda["origen"] == "cache"
    assert segunda["respuesta"] == primera["respuesta"]


def test_no_guarda_fallbacks(monkeypatch):
    fijar_prediccion(monkeypatch, "becas", 0.01)
    bot = ChatbotUPQ()
    bot.responder("capital de francia")
    assert bot.responder("capital de francia")["origen"] == "fallback"


def test_no_guarda_respuestas_del_calendario(monkeypatch):
    fijar_prediccion(monkeypatch, "calendario_escolar", 0.99)
    bot = ChatbotUPQ()
    assert bot.responder("cuando son las vacaciones")["herramienta"] == "calendario"
    assert bot.responder("cuando son las vacaciones")["origen"] == "modelo"
