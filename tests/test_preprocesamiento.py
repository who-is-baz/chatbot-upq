from src.preprocesamiento import limpiar_texto


def test_quita_mayusculas_acentos_y_signos():
    assert limpiar_texto("¿Cuándo INICIA el Cuatrimestre?") == "cuando inicia el cuatrimestre"


def test_conserva_numeros_y_normaliza_la_enie():
    # NFD separa la tilde de la ñ y se elimina: "año" -> "ano" (igual al entrenar y al predecir).
    assert limpiar_texto("Año 2026") == "ano 2026"


def test_colapsa_espacios():
    assert limpiar_texto("  hola    upq  ") == "hola upq"


def test_si_no_es_texto_regresa_vacio():
    assert limpiar_texto(None) == ""
    assert limpiar_texto(123) == ""
