"""Guardrails de entrada y salida (versión mínima).

Falta agregar: groserías, datos personales e inyección de prompts.
"""

LARGO_MAXIMO = 300

# Códigos de motivo que el orquestador traduce a un mensaje para el usuario.
ENTRADA_NO_TEXTO = "entrada_no_texto"
ENTRADA_VACIA = "entrada_vacia"
ENTRADA_MUY_LARGA = "entrada_muy_larga"


def validar_entrada(texto):
    """Devuelve (ok, texto, motivo). Si ok es False, 'motivo' dice por qué se rechaza."""
    if not isinstance(texto, str):
        return False, "", ENTRADA_NO_TEXTO
    texto = texto.strip()
    if not texto:
        return False, "", ENTRADA_VACIA
    if len(texto) > LARGO_MAXIMO:
        return False, texto, ENTRADA_MUY_LARGA
    return True, texto, ""


def validar_salida(respuesta):
    """True si la respuesta es un texto no vacío."""
    return isinstance(respuesta, str) and bool(respuesta.strip())