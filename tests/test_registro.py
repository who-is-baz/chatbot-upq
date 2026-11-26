import json

from src.registro import registrar


def leer(ruta):
    return [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines()]


def test_guarda_solo_campos_permitidos(tmp_path):
    ruta = tmp_path / "logs" / "consultas.jsonl"
    assert registrar({"texto": "¿hay becas?", "intencion": "becas", "confianza": 0.8, "ip": "1.2.3.4"}, ruta)
    fila = leer(ruta)[0]
    assert fila["intencion"] == "becas"
    assert "ip" not in fila
    assert "fecha" in fila


def test_no_guarda_texto_con_datos_personales(tmp_path):
    ruta = tmp_path / "consultas.jsonl"
    registrar({"texto": "mi correo es a@b.com", "origen": "guardrail"}, ruta)
    assert leer(ruta)[0]["texto"] is None


def test_agrega_una_linea_por_evento(tmp_path):
    ruta = tmp_path / "consultas.jsonl"
    registrar({"texto": "hola"}, ruta)
    registrar({"texto": "adiós"}, ruta)
    assert len(leer(ruta)) == 2


def test_si_no_puede_escribir_regresa_false(tmp_path):
    bloqueo = tmp_path / "archivo"
    bloqueo.write_text("x")
    assert registrar({"texto": "hola"}, bloqueo / "consultas.jsonl") is False
