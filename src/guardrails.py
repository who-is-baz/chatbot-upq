"""Guardrails de entrada y salida: reglas fijas que se aplican antes y después del modelo."""
import re

from src.preprocesamiento import limpiar_texto

LARGO_MAXIMO = 300

# El chatbot solo responde sobre la UPQ: si la pregunta nombra otra institución, se rechaza
# antes del modelo, porque el clasificador la confundiría con una pregunta válida.
OTRAS_UNIVERSIDADES = {"unam", "uaq", "uteq", "ipn", "itesm", "upsrj", "itq", "uvm", "anahuac", "udg", "uanl", "upn"}
FRASES_OTRAS = ("tec de monterrey", "la salle", "universidad autonoma de queretaro", "politecnico nacional")

# Se comparan contra el texto ya limpio (sin acentos ni signos).
GROSERIAS = {"pendejo", "pendeja", "pinche", "chingada", "chingado", "chingar", "verga", "puto", "puta",
             "cabron", "cabrona", "mierda", "culero", "culera", "idiota", "estupido", "estupida", "imbecil",
             "mamon", "ptm", "alv"}
FRASES_INYECCION = ("ignora las instrucciones", "ignora tus instrucciones", "olvida tus instrucciones",
                    "olvida las instrucciones", "ignore previous", "ignore all", "actua como", "ahora eres",
                    "system prompt", "prompt del sistema", "revela tus instrucciones", "jailbreak",
                    "modo desarrollador")

# Datos personales: se buscan en el texto original, porque limpiar_texto quita la @.
CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
TELEFONO = re.compile(r"(?<!\d)(?:\+?52[\s-]?)?(?:\d[\s-]?){9}\d(?!\d)")
CURP = re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b", re.IGNORECASE)

# Marcas de datos sin verificar que nunca deben llegar al usuario.
MARCAS_SIN_VERIFICAR = ("[SEMILLA]", "[PENDIENTE]")

# Códigos de motivo que el orquestador traduce a un mensaje para el usuario.
ENTRADA_NO_TEXTO = "entrada_no_texto"
ENTRADA_VACIA = "entrada_vacia"
ENTRADA_MUY_LARGA = "entrada_muy_larga"
DATOS_PERSONALES = "datos_personales"
LENGUAJE_OFENSIVO = "lenguaje_ofensivo"
INYECCION = "inyeccion"
OTRA_UNIVERSIDAD = "otra_universidad"


def contiene_datos_personales(texto):
    """True si el texto trae un correo, un teléfono de 10 dígitos o una CURP."""
    return bool(CORREO.search(texto) or TELEFONO.search(texto) or CURP.search(texto))


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
    if contiene_datos_personales(texto):
        return False, texto, DATOS_PERSONALES
    limpio = limpiar_texto(texto)
    if set(limpio.split()) & GROSERIAS:
        return False, texto, LENGUAJE_OFENSIVO
    if any(f in limpio for f in FRASES_INYECCION):
        return False, texto, INYECCION
    if menciona_otra_universidad(texto):
        return False, texto, OTRA_UNIVERSIDAD
    return True, texto, ""


def validar_salida(respuesta):
    """True si la respuesta es un texto no vacío y sin datos marcados como no verificados."""
    if not isinstance(respuesta, str) or not respuesta.strip():
        return False
    return not any(marca in respuesta for marca in MARCAS_SIN_VERIFICAR)