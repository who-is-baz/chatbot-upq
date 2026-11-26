"""Guardrails de entrada y salida.

Falta agregar: groserías, datos personales e inyección de prompts.
"""
from src.preprocesamiento import limpiar_texto

LARGO_MAXIMO = 300

# El chatbot solo responde sobre la UPQ: si la pregunta nombra otra institución, se rechaza
# antes del modelo, porque el clasificador la confundiría con una pregunta válida.
OTRAS_UNIVERSIDADES = {"unam", "uaq", "uteq", "ipn", "itesm", "upsrj", "itq", "uvm", "anahuac", "udg", "uanl", "upn"}
FRASES_OTRAS = ("tec de monterrey", "la salle", "universidad autonoma de queretaro", "politecnico nacional")

# Códigos de motivo que el orquestador traduce a un mensaje para el usuario.
ENTRADA_NO_TEXTO = "entrada_no_texto"
ENTRADA_VACIA = "entrada_vacia"
ENTRADA_MUY_LARGA = "entrada_muy_larga"
OTRA_UNIVERSIDAD = "otra_universidad"


def menciona_otra_universidad(texto):
    """True si el texto nombra otra universidad (se compara ya limpio)."""
    limpio = limpiar_texto(texto)
    return bool(set(limpio.split()) & OTRAS_UNIVERSIDADES) or any(f in limpio for f in FRASES_OTRAS)


def validar_entrada(texto):
    """Devuelve (ok, texto, motivo). Si ok es False, 'motivo' dice por qué se rechaza."""
    if not isinstance(texto, str):
        return False, "", ENTRADA_NO_TEXTO
    texto = texto.strip()
    if not texto:
        return False, "", ENTRADA_VACIA
    if len(texto) > LARGO_MAXIMO:
        return False, texto, ENTRADA_MUY_LARGA
    if menciona_otra_universidad(texto):
        return False, texto, OTRA_UNIVERSIDAD
    return True, texto, ""


def validar_salida(respuesta):
    """True si la respuesta es un texto no vacío."""
    return isinstance(respuesta, str) and bool(respuesta.strip())