"""Orquestador: une guardrails, caché, router, herramientas y recuperador en una sola llamada.

Flujo y 3 niveles según la confianza del router (umbrales en models/config.json):
  confianza >= umbral_alto           -> respuesta (herramienta, fragmento oficial o respuesta corta)
  umbral_bajo <= confianza < alto    -> "¿Quisiste decir…?" con el top-3
  confianza < umbral_bajo            -> fallback con datos de contacto
"""
import json
import time
from pathlib import Path

import pandas as pd

from src import guardrails, herramientas, recuperador, registro, router
from src.cache import Cache
from src.preprocesamiento import limpiar_texto

RAIZ = Path(__file__).resolve().parent.parent

# Valores de origen y nivel que devuelve responder()
ORIGEN_GUARDRAIL, ORIGEN_CACHE, ORIGEN_MODELO, ORIGEN_FALLBACK = "guardrail", "cache", "modelo", "fallback"
NIVEL_RESPUESTA, NIVEL_ACLARACION, NIVEL_FALLBACK = "respuesta", "aclaracion", "fallback"


class ChatbotUPQ:
    def __init__(self, raiz: Path = RAIZ, ruta_registro: Path | None = None):
        # Archivo donde se registran las consultas y los votos (sin datos personales).
        self.ruta_registro = ruta_registro or registro.RUTA_REGISTRO
        umbrales = json.loads((raiz / "models" / "config.json").read_text(encoding="utf-8"))
        self.umbral_alto = float(umbrales["umbral_alto"])
        self.umbral_bajo = float(umbrales["umbral_bajo"])
        self.config = json.loads((raiz / "config" / "asistente.json").read_text(encoding="utf-8"))

        corpus = pd.read_csv(raiz / "data" / "corpus_upq.csv")
        # Una sola respuesta por intención: se toma la primera que aparezca.
        cortas = corpus.drop_duplicates("intencion").set_index("intencion")
        self.respuestas = cortas[["respuesta", "fuente"]].to_dict("index")
        self.cache = Cache(capacidad=128)

    # ------------------------------------------------------------------ API pública
    def responder(self, texto) -> dict:
        """Recibe la pregunta del usuario y devuelve el dict del contrato (ver README)."""
        inicio = time.perf_counter()

        ok, texto, motivo = guardrails.validar_entrada(texto)
        if not ok:
            return self._cerrar(self._guardrail(motivo), inicio, texto)

        clave = limpiar_texto(texto)
        guardado = self.cache.get(clave)
        if guardado is not None:
            guardado["origen"] = ORIGEN_CACHE
            return self._cerrar(guardado, inicio, texto)

        prediccion = router.predecir(clave)
        intencion, confianza, top3 = prediccion["intencion"], prediccion["confianza"], prediccion["top3"]

        if confianza >= self.umbral_alto:
            resultado = self._contestar(texto, intencion)
        elif confianza >= self.umbral_bajo:
            resultado = self._aclarar(top3)
        else:
            resultado = self._fallback()
        resultado.update(intencion=intencion, confianza=confianza, top3=top3)

        if not guardrails.validar_salida(resultado["respuesta"]):
            resultado.update(self._guardrail("salida_invalida"))
        # Solo se guardan respuestas del modelo que no cambian con el día (las del calendario sí cambian).
        elif resultado["origen"] == ORIGEN_MODELO and resultado["herramienta"] != "calendario":
            self.cache.set(clave, resultado)
        return self._cerrar(resultado, inicio, texto)

    def responder_intencion(self, intencion: str, texto: str = "") -> dict:
        """Contesta una intención elegida por el usuario en el "¿Quisiste decir…?"."""
        inicio = time.perf_counter()
        resultado = self._contestar(texto, intencion)
        resultado.update(intencion=intencion, confianza=1.0, top3=[(intencion, 1.0)])
        return self._cerrar(resultado, inicio, texto)

    def registrar_voto(self, texto: str, resultado: dict, util: bool) -> bool:
        """Registra el 👍 (util=True) o 👎 (util=False) de una respuesta. Alimenta el reentrenamiento."""
        return registro.registrar({
            "texto": texto, "intencion": resultado.get("intencion"), "confianza": resultado.get("confianza"),
            "origen": resultado.get("origen"), "util": util,
        }, self.ruta_registro)

    def etiqueta(self, intencion: str) -> str:
        return self.config["etiquetas"].get(intencion, intencion.replace("_", " ").capitalize())

    # ------------------------------------------------------------------ niveles
    def _contestar(self, texto: str, intencion: str) -> dict:
        corta = self.respuestas.get(intencion)
        if corta is None:
            return self._fallback()
        eleccion = herramientas.elegir(intencion, texto) if texto else None
        if eleccion:
            nombre, args = eleccion
            return self._base(herramientas.ejecutar(nombre, **args), herramientas.FUENTES[nombre],
                              ORIGEN_MODELO, NIVEL_RESPUESTA, herramienta=nombre)
        fragmentos = recuperador.buscar(texto, intencion, k=1) if texto else []
        if fragmentos:
            f = fragmentos[0]
            return self._base(f.texto, f.fuente, ORIGEN_MODELO, NIVEL_RESPUESTA, fragmento={
                "id": f.id, "titulo": f.titulo, "imagen": f.imagen,
                "vigencia": f.vigencia, "similitud": f.similitud,
            })
        return self._base(corta["respuesta"], corta["fuente"], ORIGEN_MODELO, NIVEL_RESPUESTA)

    def _aclarar(self, top3: list) -> dict:
        return self._base(self.config["aclaracion"], "", ORIGEN_FALLBACK, NIVEL_ACLARACION,
                          es_fallback=True, sugerencias=[i for i, _ in top3])

    def _fallback(self) -> dict:
        return self._base(self.config["fallback"], self.config["fuente_fallback"],
                          ORIGEN_FALLBACK, NIVEL_FALLBACK, es_fallback=True)

    def _guardrail(self, motivo: str) -> dict:
        mensaje = self.config["motivos_guardrail"].get(motivo, self.config["fallback"])
        return self._base(mensaje, "", ORIGEN_GUARDRAIL, NIVEL_FALLBACK, es_fallback=True, motivo=motivo)

    # ------------------------------------------------------------------ utilidades
    @staticmethod
    def _base(respuesta, fuente, origen, nivel, es_fallback=False, **extra) -> dict:
        resultado = {
            "intencion": None, "confianza": 0.0, "top3": [],
            "respuesta": respuesta, "fuente": fuente, "es_fallback": es_fallback,
            "origen": origen, "nivel": nivel, "fragmento": None, "herramienta": None, "sugerencias": [],
        }
        resultado.update(extra)
        return resultado

    def _cerrar(self, resultado: dict, inicio: float, texto: str = "") -> dict:
        """Mide la latencia y registra la consulta (registro.py quita los datos personales)."""
        resultado["latencia_ms"] = round((time.perf_counter() - inicio) * 1000, 1)
        registro.registrar({"texto": texto, **resultado}, self.ruta_registro)
        return resultado
