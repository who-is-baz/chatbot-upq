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
