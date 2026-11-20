"""Limpieza de texto para el clasificador de intenciones."""
import re
import unicodedata


def limpiar_texto(texto: str) -> str:
    """Normaliza una pregunta: minúsculas, sin acentos, sin signos y sin espacios de sobra."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    # Quita acentos: "inscripción" -> "inscripcion"
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    # Deja solo letras, números y espacios
    texto = re.sub(r"[^a-z0-9ñ\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()
