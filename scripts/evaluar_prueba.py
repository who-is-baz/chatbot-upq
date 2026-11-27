"""Evalúa el chatbot completo con un conjunto de preguntas etiquetadas (nunca se usan para entrenar).

Uso: python scripts/evaluar_prueba.py data/prueba_adversarial.csv
El CSV necesita las columnas texto e intencion_esperada ("fuera_de_alcance" o "guardrail" para las que
no debe contestar). El registro de consultas se manda a una carpeta temporal para no ensuciar logs/.
"""
import sys
import tempfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.chatbot import ChatbotUPQ  # noqa: E402

NO_CONTESTAR = {"fuera_de_alcance", "guardrail"}


def main(ruta):
    prueba = pd.read_csv(ruta)
    with tempfile.TemporaryDirectory() as temporal:
        bot = ChatbotUPQ(ruta_registro=Path(temporal) / "consultas.jsonl")
        resultados = [bot.responder(texto) for texto in prueba.texto]

    prueba["origen"] = [r["origen"] for r in resultados]
    prueba["nivel"] = [r["nivel"] for r in resultados]
    prueba["prediccion"] = [r["intencion"] for r in resultados]
    prueba["confianza"] = [round(r["confianza"] or 0, 2) for r in resultados]
    prueba["en_top3"] = [e in [i for i, _ in (r["top3"] or [])] for e, r in zip(prueba.intencion_esperada, resultados)]

    validas = prueba[~prueba.intencion_esperada.isin(NO_CONTESTAR)]
    ajenas = prueba[prueba.intencion_esperada == "fuera_de_alcance"]
    reglas = prueba[prueba.intencion_esperada == "guardrail"]
    directas = validas[validas.nivel == "respuesta"]
    aclaradas = validas[validas.nivel == "aclaracion"]

    print(f"Preguntas: {len(prueba)} (válidas {len(validas)}, ajenas {len(ajenas)}, guardrails {len(reglas)})")
    print(f"Guardrails que rechazaron: {(reglas.origen == 'guardrail').sum()} de {len(reglas)}")
    print(f"Válidas con respuesta directa: {len(directas)} ({len(directas) / len(validas):.0%}), "
          f"correctas: {(directas.prediccion == directas.intencion_esperada).mean():.0%}")
    print(f"Válidas con '¿Quisiste decir...?': {len(aclaradas)} ({len(aclaradas) / len(validas):.0%}), "
          f"con la correcta en el top-3: {aclaradas.en_top3.mean():.0%}")
    print(f"Válidas en fallback: {(validas.nivel == 'fallback').sum()} ({(validas.nivel == 'fallback').mean():.0%})")
    print(f"Ajenas: rechazadas {(ajenas.nivel == 'fallback').sum()}, con aclaración {(ajenas.nivel == 'aclaracion').sum()}, "
          f"respondidas directo {(ajenas.nivel == 'respuesta').sum()} (de {len(ajenas)})")

    errores = prueba[(~prueba.intencion_esperada.isin(NO_CONTESTAR) & (prueba.prediccion != prueba.intencion_esperada))
                     | ((prueba.intencion_esperada == "fuera_de_alcance") & (prueba.nivel == "respuesta"))]
    print("\nCasos para el análisis de errores:")
    print(errores[["texto", "intencion_esperada", "prediccion", "confianza", "nivel"]].to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "data" / "prueba_adversarial.csv")
