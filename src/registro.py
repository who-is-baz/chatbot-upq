"""Registro de consultas sin datos personales (un JSON por línea en logs/consultas.jsonl)."""
import json
from datetime import datetime
from pathlib import Path

from src.guardrails import contiene_datos_personales

RUTA_REGISTRO = Path(__file__).resolve().parent.parent / "logs" / "consultas.jsonl"
LARGO_MAXIMO_TEXTO = 300
# Lista blanca: cualquier otro campo del evento se descarta.
CAMPOS_PERMITIDOS = ("texto", "intencion", "confianza", "origen", "es_fallback", "latencia_ms", "motivo", "util")


def registrar(evento, ruta=RUTA_REGISTRO):
    """Agrega el evento al registro. Devuelve True si se guardó y False si no se pudo escribir."""
    fila = {"fecha": datetime.now().isoformat(timespec="seconds")}
    for campo in CAMPOS_PERMITIDOS:
        if campo in evento:
            fila[campo] = evento[campo]
    texto = fila.get("texto")
    if isinstance(texto, str):
        fila["texto"] = None if contiene_datos_personales(texto) else texto[:LARGO_MAXIMO_TEXTO]
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False