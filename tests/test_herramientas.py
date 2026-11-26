"""Pruebas de las herramientas deterministas."""
from datetime import date

import pytest

from src import herramientas as h

HOY = date(2026, 11, 25)


# ---------------------------------------------------------------- calendario
def test_calendario_da_las_proximas_vacaciones():
    texto = h.calendario(tema="vacaciones", hoy=HOY)
    assert "21 de diciembre de 2026" in texto and "5 de enero de 2027" in texto


def test_calendario_no_muestra_fechas_pasadas():
    texto = h.calendario(hoy=HOY)
    assert "septiembre" not in texto  # todo septiembre 2026 ya pasó
    assert "4 de diciembre de 2026" in texto


def test_calendario_marca_eventos_en_curso():
    assert "(en curso)" in h.calendario(tema="vacaciones", hoy=date(2026, 12, 28))


def test_calendario_sin_fechas_futuras():
    assert "No encontré fechas" in h.calendario(tema="inicio", hoy=date(2028, 1, 1))


def test_calendario_csv_bien_formado():
    cal = h._calendario
    assert (cal["inicio"] <= cal["fin"]).all()
    temas_validos = {t for t, _ in h.TEMAS_CALENDARIO}
    assert set(cal["tema"]) <= temas_validos


# ---------------------------------------------------------------- contacto y enlace
def test_contacto_da_extension_y_correo():
    texto = h.contacto("Titulación")
    assert "ext. 356" in texto and "tramite.titulacion@upq.edu.mx" in texto


def test_contacto_de_area_desconocida_da_conmutador():
    assert "442 101 9000" in h.contacto("Área inventada")


def test_enlace_es_oficial():
    assert "upq.mx" in h.enlace("becas")


def test_todas_las_intenciones_tienen_enlace():
    from src.chatbot import ChatbotUPQ
    sin_enlace = set(ChatbotUPQ().config["etiquetas"]) - set(h.ENLACES) - {"saludo", "despedida", "agradecimiento"}
    assert not sin_enlace


# ---------------------------------------------------------------- elegir
@pytest.mark.parametrize("texto, intencion, esperado", [
    ("cuando son las proximas vacaciones", "calendario_escolar", ("calendario", {"tema": "vacaciones"})),
    ("que fechas siguen", "calendario_escolar", ("calendario", {"tema": None})),
    ("cuando es la alta y baja de materias", "calendario_escolar", ("calendario", {"tema": "alta_baja"})),
    ("telefono de titulacion", "titulacion", ("contacto", {"area": "Titulación"})),
    ("correo de servicios estudiantiles", "contacto_horarios", ("contacto", {"area": "Servicios Estudiantiles"})),
    ("link de la pagina de becas", "becas", ("enlace", {"intencion": "becas"})),
])
def test_elegir_herramienta(texto, intencion, esperado):
    assert h.elegir(intencion, texto) == esperado


@pytest.mark.parametrize("texto, intencion", [
    ("cual es el calendario", "calendario_escolar"),          # general: lo contesta el fragmento
    ("como saco mi kardex", "servicios_escolares"),
    ("recuperar contraseña del correo institucional", "servicios_escolares"),
    ("hay becas por promedio", "becas"),
])
def test_elegir_sin_herramienta(texto, intencion):
    assert h.elegir(intencion, texto) is None


def test_ejecutar_herramienta_desconocida():
    with pytest.raises(ValueError):
        h.ejecutar("no_existe")
