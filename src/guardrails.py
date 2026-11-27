"""Guardrails de entrada y salida: reglas fijas que se aplican antes y después del modelo."""
import re

from src.preprocesamiento import limpiar_texto

LARGO_MAXIMO = 300

# El chatbot solo responde sobre la UPQ: si la pregunta nombra otra institución o habla de
# educación básica, se rechaza antes del modelo, porque el clasificador la confundiría con una
# pregunta válida (por ejemplo, "vacaciones de la SEP en primaria" se parece a calendario_escolar).
OTRAS_UNIVERSIDADES = {"unam", "uaq", "uteq", "ipn", "itesm", "upsrj", "itq", "uvm", "anahuac", "udg", "uanl", "upn"}
OTROS_NIVELES = {"primaria", "secundaria", "kinder", "preescolar", "guarderia"}
FRASES_OTRAS = ("tec de monterrey", "la salle", "universidad autonoma de queretaro", "politecnico nacional")

# Se comparan contra el texto ya limpio (sin acentos ni signos).
GROSERIAS = {"pendejo", "pendeja", "pinche", "chingada", "chingado", "chingar", "verga", "puto", "puta",
             "cabron", "cabrona", "mierda", "culero", "culera", "idiota", "estupido", "estupida", "imbecil",
             "mamon", "ptm", "alv",
             # Variantes y abreviaturas comunes
             "puito", "puita", "putito", "putita", "putos", "putas", "pndjo", "pndja", "pendejos", "pendejas",
             "cabrones", "mamona", "pinches", "ctm", "hdp", "vrga"}
FRASES_OFENSIVAS = ("ni madres", "valiendo madre", "a la madre", "hijo de tu", "chinga tu", "te odio", "te detesto", "eres inutil", "bot inutil",
                    "no sirves", "no sirve para nada", "eres un asco", "callate")
FRASES_INYECCION = ("ignora las instrucciones", "ignora tus instrucciones", "olvida tus instrucciones",
                    "olvida las instrucciones", "ignore previous", "ignore all", "actua como", "ahora eres",
                    "system prompt", "prompt del sistema", "revela tus instrucciones", "jailbreak",
                    "modo desarrollador", "olvida que eres", "olvida q eres", "dime tu prompt",
                    "muestrame tu prompt", "cual es tu prompt")

# Datos personales: se buscan en el texto original, porque limpiar_texto quita la @.
CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
TELEFONO = re.compile(r"(?<!\d)(?:\+?52[\s-]?)?(?:\d[\s-]?){9}\d(?!\d)")
CURP = re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b", re.IGNORECASE)
TARJETA = re.compile(r"(?<!\d)(?:\d[\s-]?){12,18}\d(?!\d)")

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
    """True si el texto trae un correo, un teléfono, una CURP o un número de tarjeta."""
    return bool(CORREO.search(texto) or TELEFONO.search(texto) or CURP.search(texto) or TARJETA.search(texto))


def menciona_otra_universidad(texto):
    """True si el texto nombra otra universidad o habla de educación básica (se compara ya limpio)."""
    limpio = limpiar_texto(texto)
    palabras = set(limpio.split())
    return bool(palabras & (OTRAS_UNIVERSIDADES | OTROS_NIVELES)) or any(f in limpio for f in FRASES_OTRAS)


def sin_ofuscar(limpio):
    """Une rachas de 3 o más letras sueltas: "p u t o" (de "p.u.t.o" o "p-u-t-o") -> "puto".

    No se usa distancia de edición porque "punto" quedaría a una letra de "puto".
    """
    return re.sub(r"\b(?:[a-zñ] ){2,}[a-zñ]\b", lambda m: m.group(0).replace(" ", ""), limpio)


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
    palabras = set(limpio.split()) | set(sin_ofuscar(limpio).split())
    if palabras & GROSERIAS or any(f in limpio for f in FRASES_OFENSIVAS):
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