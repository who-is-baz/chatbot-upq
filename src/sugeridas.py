"""Rotación de preguntas sugeridas: muestra N a la vez sin repetir hasta haber mostrado todas."""
import random


def siguiente_tanda(todas: list[str], vistas: list[str], n: int = 5,
                    rng: random.Random | None = None) -> tuple[list[str], list[str]]:
    """Devuelve (tanda, vistas_actualizadas).

    Toma preguntas que todavía no se han mostrado en este ciclo. Cuando se acaban, vuelve a barajar la lista
    completa (ciclo nuevo) evitando repetir las de la tanda anterior, para que el clic siempre muestre algo distinto.
    """
    rng = rng or random.Random()
    pendientes = [p for p in todas if p not in vistas]
    rng.shuffle(pendientes)
    tanda = pendientes[:n]
    vistas = vistas + tanda
    if len(tanda) < n:
        # Ciclo nuevo: se baraja todo otra vez, sin las de esta tanda ni las de la tanda anterior si se puede.
        anterior = vistas[-n - len(tanda):-len(tanda)] if tanda else vistas[-n:]
        nuevas = [p for p in todas if p not in tanda and p not in anterior]
        if len(nuevas) < n - len(tanda):
            nuevas = [p for p in todas if p not in tanda]
        rng.shuffle(nuevas)
        extra = nuevas[:n - len(tanda)]
        tanda += extra
        vistas = extra
    return tanda, vistas


def sugerencia_relacionada(por_intencion: dict[str, list[str]], top3: list, ya_hechas: set[str],
                           todas: list[str], rng: random.Random | None = None) -> str | None:
    """Una pregunta sugerida relacionada con la última respuesta, que no se haya hecho todavía.

    Busca primero en la intención de la respuesta y luego en las vecinas del top-3; si ninguna tiene
    preguntas nuevas, toma cualquiera de la lista que no se haya hecho. Devuelve None si ya se hicieron todas.
    """
    rng = rng or random.Random()
    for intencion, _ in top3:
        nuevas = [p for p in por_intencion.get(intencion, []) if p not in ya_hechas]
        if nuevas:
            return rng.choice(nuevas)
    restantes = [p for p in todas if p not in ya_hechas]
    return rng.choice(restantes) if restantes else None
