"""Herramientas deterministas: respuestas exactas que no dependen del modelo.

- calendario: próximas fechas del calendario escolar a partir de hoy (o de un tema).
- contacto:   extensión y correo de un área (directorio oficial).
- enlace:     enlace oficial de la página de un tema.

El orquestador llama a elegir(intencion, texto) y, si regresa algo, a ejecutar(nombre, **args).
"""
from datetime import date
from pathlib import Path

import pandas as pd

from src.preprocesamiento import limpiar_texto

DATOS = Path(__file__).resolve().parent.parent / "data" / "herramientas"

_calendario = pd.read_csv(DATOS / "calendario_escolar.csv", parse_dates=["inicio", "fin"])
_calendario["inicio"] = _calendario["inicio"].dt.date
_calendario["fin"] = _calendario["fin"].dt.date
_directorio = pd.read_csv(DATOS / "directorio.csv", dtype=str).fillna("")

FUENTES = {
    "calendario": "https://www.upq.mx/ServiciosEstudiantiles#/ | Calendario Escolar SEP26-AGO27",
    "contacto": "https://www.upq.mx/Institucion/Directorio#/ | Directorio",
    "enlace": "https://www.upq.mx",
}

ENLACES = {
    "admision": "https://sistemaintegral.upq.edu.mx/admisiones.php",
    "oferta_educativa": "https://www.upq.mx/carreras/informes/",
    "costos_pagos": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "becas": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "calendario_escolar": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "reinscripcion": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "estadias": "https://www.upq.mx/estancias-estadias/",
    "servicio_social": "https://www.upq.mx/Institucion/MarcoJuridico",
    "titulacion": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "ingles_idiomas": "https://www.upq.mx/FormacionIntegral/LenguaExtranjera#/",
    "movilidad_intercambio": "https://www.upq.mx/Vinculacion#/",
    "servicios_escolares": "https://www.upq.mx/ServiciosEstudiantiles#/",
    "ubicacion_transporte": "https://www.upq.mx/Institucion/Ubicacion#/",
    "contacto_horarios": "https://www.upq.mx/Institucion/Directorio#/",
    "biblioteca_actividades": "https://www.upq.mx/FormacionIntegral/Representativos#/",
}

# Palabras (ya limpias) que llevan a cada tema del calendario. El orden importa:
# "alta y baja" se revisa antes que "baja".
TEMAS_CALENDARIO = [
    ("cambio_carrera", ("cambio de carrera", "cambiar de carrera", "cambiarme de carrera")),
    ("alta_baja", ("alta y baja", "dar de alta", "baja de materia", "baja de asignatura", "alta de materia")),
    ("baja", ("baja temporal", "baja voluntaria", "darme de baja", "dar de baja")),
    ("reinscripcion", ("reinscrip", "reinscribir")),
    ("vacaciones", ("vacacion", "descanso")),
    ("no_laborable", ("no laborable", "festivo", "feriado", "puente", "no hay clases", "inhabil")),
    ("becas", ("beca",)),
    ("pago", ("recursamiento", "etc", "fecha limite de pago")),
    ("final", ("calificacion final", "calificaciones finales", "actas")),
    ("parcial", ("parcial", "examenes", "evaluacion")),
    ("inicio", ("inici", "empiez", "empieza", "comienz", "regreso a clases", "entrada a clases")),
    ("fin", ("termin", "acaba", "fin de cuatrimestre", "fin del cuatrimestre")),
]
PALABRAS_PROXIMO = ("proxim", "siguiente", "sigue", "cuanto falta", "esta semana", "hoy", "fechas importantes")
PALABRAS_CONTACTO = ("telefono", "extension", "ext ", "correo", "contacto", "comunico", "marco", "hablo",
                     "numero", "mail", "email")
PALABRAS_ENLACE = ("link", "liga", "enlace", "pagina", "sitio", "url", "web")

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre")


# ---------------------------------------------------------------- API pública
def elegir(intencion: str, texto: str):
    """Decide si la pregunta la contesta mejor una herramienta. Devuelve (nombre, args) o None."""
    limpio = f" {limpiar_texto(texto)} "

    if any(p in limpio for p in PALABRAS_ENLACE) and intencion in ENLACES:
        return "enlace", {"intencion": intencion}

    areas = _buscar_areas(limpio)
    if areas and (intencion == "contacto_horarios" or any(p in limpio for p in PALABRAS_CONTACTO)):
        return "contacto", {"area": areas[0]}

    if intencion == "calendario_escolar":
        tema = _buscar_tema(limpio)
        if tema or any(p in limpio for p in PALABRAS_PROXIMO):
            return "calendario", {"tema": tema}
    return None


def ejecutar(nombre: str, **args) -> str:
    """Ejecuta una herramienta por nombre y devuelve el texto de la respuesta."""
    herramientas = {"calendario": calendario, "contacto": contacto, "enlace": enlace}
    if nombre not in herramientas:
        raise ValueError(f"Herramienta desconocida: {nombre}")
    return herramientas[nombre](**args)


# ---------------------------------------------------------------- herramientas
def calendario(tema: str | None = None, hoy: date | None = None, n: int = 3) -> str:
    """Fechas en curso o próximas del calendario escolar, de un tema o en general."""
    hoy = hoy or date.today()
    eventos = _calendario[_calendario["fin"] >= hoy]
    if tema:
        eventos = eventos[eventos["tema"] == tema]
    eventos = eventos.sort_values("inicio").head(n if not tema else 2)

    if eventos.empty:
        return ("No encontré fechas próximas para eso en el calendario escolar sep 2026 - ago 2027. "
                "Consulta el calendario vigente en Servicios Estudiantiles.")

    lineas = []
    for _, e in eventos.iterrows():
        en_curso = " (en curso)" if e["inicio"] <= hoy else ""
        lineas.append(f"- {_rango(e['inicio'], e['fin'])}: {e['evento']}, cuatrimestre {e['cuatrimestre']}{en_curso}.")
    encabezado = "Estas son las próximas fechas del calendario escolar:" if not tema else "Según el calendario escolar:"
    return encabezado + "\n" + "\n".join(lineas)


def contacto(area: str) -> str:
    """Extensión y correo de un área del directorio."""
    fila = _directorio[_directorio["area"] == area]
    if fila.empty:
        return "Puedes comunicarte al conmutador 442 101 9000 o escribir a servicios.estudiantiles@upq.edu.mx."
    fila = fila.iloc[0]
    partes = []
    if fila["extension"]:
        partes.append(f"teléfono 442 101 9000, ext. {fila['extension']}")
    if fila["correo"]:
        partes.append(f"correo {fila['correo']}")
    return f"{fila['area']}: " + " · ".join(partes) + "."


def enlace(intencion: str) -> str:
    """Enlace oficial de la página del tema."""
    url = ENLACES.get(intencion, "https://www.upq.mx")
    return f"Puedes consultarlo en la página oficial: {url}"


# ---------------------------------------------------------------- utilidades
def _buscar_tema(limpio: str) -> str | None:
    for tema, palabras in TEMAS_CALENDARIO:
        if any(p in limpio for p in palabras):
            return tema
    return None


def _buscar_areas(limpio: str) -> list[str]:
    """Áreas cuyas palabras clave aparecen en el texto, de la coincidencia más larga a la más corta."""
    encontradas = []
    for _, fila in _directorio.iterrows():
        claves = [limpiar_texto(c) for c in fila["palabras_clave"].split("|") if c]
        largo = max((len(c) for c in claves if f" {c}" in limpio), default=0)
        if largo:
            encontradas.append((largo, fila["area"]))
    return [area for _, area in sorted(encontradas, key=lambda x: -x[0])]


def _fecha(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def _rango(inicio: date, fin: date) -> str:
    if inicio == fin:
        return f"El {_fecha(inicio)}"
    if inicio.year == fin.year:
        mes = "" if inicio.month == fin.month else f" de {MESES[inicio.month - 1]}"
        return f"Del {inicio.day}{mes} al {_fecha(fin)}"
    return f"Del {_fecha(inicio)} al {_fecha(fin)}"
