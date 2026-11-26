"""Pruebas del orquestador y del recuperador."""
import pytest

from src import recuperador, router
from src.chatbot import ChatbotUPQ

CLAVES = {"intencion", "confianza", "respuesta", "fuente", "es_fallback", "top3", "origen", "latencia_ms"}


@pytest.fixture(scope="module")
def bot():
    return ChatbotUPQ()


def fijar_prediccion(monkeypatch, intencion, confianza):
    top3 = [(intencion, confianza), ("becas", 0.1), ("admision", 0.05)]
    monkeypatch.setattr(router, "predecir",
                        lambda _: {"intencion": intencion, "confianza": confianza, "top3": top3})


# ---------------------------------------------------------------- contrato
@pytest.mark.parametrize("texto", ["hola", "hay beca", "capital de francia", "", None, "x" * 500])
def test_responder_cumple_contrato(bot, texto):
    r = bot.responder(texto)
    assert CLAVES <= r.keys()
    assert r["origen"] in {"guardrail", "cache", "modelo", "fallback"}
    assert isinstance(r["respuesta"], str) and r["respuesta"].strip()


# ---------------------------------------------------------------- tres niveles
def test_confianza_alta_responde(bot, monkeypatch):
    fijar_prediccion(monkeypatch, "becas", 0.95)
    r = bot.responder("hay becas por promedio")
    assert r["nivel"] == "respuesta" and r["origen"] == "modelo" and not r["es_fallback"]
    assert r["fuente"]


def test_confianza_media_pregunta_quisiste_decir(bot, monkeypatch):
    fijar_prediccion(monkeypatch, "becas", (bot.umbral_alto + bot.umbral_bajo) / 2)
    r = bot.responder("algo de becas")
    assert r["nivel"] == "aclaracion" and r["es_fallback"]
    assert r["sugerencias"] == ["becas", "becas", "admision"]  # el top-3 tal cual


def test_confianza_baja_da_fallback_con_contacto(bot, monkeypatch):
    fijar_prediccion(monkeypatch, "becas", bot.umbral_bajo / 2)
    r = bot.responder("cual es la capital de francia")
    assert r["nivel"] == "fallback" and r["origen"] == "fallback"
    assert "442 101 9000" in r["respuesta"]


def test_guardrail_rechaza_vacio(bot):
    r = bot.responder("   ")
    assert r["origen"] == "guardrail" and r["motivo"] == "entrada_vacia"


def test_cada_motivo_de_guardrail_tiene_mensaje(bot):
    from src import guardrails
    motivos = {v for k, v in vars(guardrails).items() if k.isupper() and isinstance(v, str) and v.islower()}
    faltan = motivos - bot.config["motivos_guardrail"].keys()
    assert not faltan, f"Faltan mensajes en config/asistente.json para: {faltan}"


def test_umbrales_vienen_de_config(bot):
    assert 0 < bot.umbral_bajo < bot.umbral_alto <= 1


# ---------------------------------------------------------------- recuperador
def test_recuperador_solo_busca_en_la_intencion():
    fragmentos = recuperador.buscar("ingenieria mecatronica", "becas", k=5)
    assert all(f.intencion == "becas" for f in fragmentos)


def test_recuperador_encuentra_fragmento_relevante():
    fragmentos = recuperador.buscar("olvide mi contraseña del sii", "servicios_escolares")
    assert fragmentos and fragmentos[0].id == "F116"


def test_recuperador_sin_parecido_regresa_vacio():
    assert recuperador.buscar("asdf qwer", "servicios_escolares") == []
    assert recuperador.buscar("hola", "saludo") == []


def test_sin_fragmento_usa_respuesta_corta(bot):
    r = bot.responder_intencion("saludo", "hola")
    assert r["fragmento"] is None
    assert r["respuesta"] == bot.respuestas["saludo"]["respuesta"]


# ---------------------------------------------------------------- registro
def leer_registro(ruta):
    import json
    return [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines()]


def test_cada_consulta_queda_registrada(tmp_path):
    ruta = tmp_path / "consultas.jsonl"
    bot = ChatbotUPQ(ruta_registro=ruta)
    bot.responder("hay becas")
    bot.responder("")
    filas = leer_registro(ruta)
    assert len(filas) == 2
    assert filas[0]["texto"] == "hay becas" and "latencia_ms" in filas[0]
    assert filas[1]["origen"] == "guardrail"


def test_registro_no_guarda_datos_personales(tmp_path):
    ruta = tmp_path / "consultas.jsonl"
    ChatbotUPQ(ruta_registro=ruta).responder("mi curp es GOMA850101HQTRRL09")
    fila = leer_registro(ruta)[0]
    assert fila["texto"] is None and fila["motivo"] == "datos_personales"


def test_voto_queda_registrado(tmp_path):
    ruta = tmp_path / "consultas.jsonl"
    bot = ChatbotUPQ(ruta_registro=ruta)
    resultado = bot.responder("hay becas")
    assert bot.registrar_voto("hay becas", resultado, util=False)
    voto = leer_registro(ruta)[-1]
    assert voto["util"] is False and voto["intencion"] == resultado["intencion"]
