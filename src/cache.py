"""Caché LRU de respuestas con métrica de aciertos.

Guarda las últimas `capacidad` respuestas por pregunta limpia. Cuando se llena, saca la
que se usó hace más tiempo (Least Recently Used).
"""
import copy
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad: int = 128):
        if capacidad < 1:
            raise ValueError("La capacidad debe ser al menos 1")
        self.capacidad = capacidad
        self._datos: OrderedDict = OrderedDict()
        self.aciertos = 0
        self.fallos = 0

    def get(self, clave):
        """Devuelve una copia del valor guardado o None. Cuenta acierto o fallo."""
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self.aciertos += 1
            return copy.deepcopy(self._datos[clave])
        self.fallos += 1
        return None

    def set(self, clave, valor) -> None:
        """Guarda una copia del valor; si se pasa de la capacidad, saca el menos usado."""
        self._datos[clave] = copy.deepcopy(valor)
        self._datos.move_to_end(clave)
        if len(self._datos) > self.capacidad:
            self._datos.popitem(last=False)

    def metricas(self) -> dict:
        consultas = self.aciertos + self.fallos
        return {
            "aciertos": self.aciertos,
            "fallos": self.fallos,
            "tasa_aciertos": self.aciertos / consultas if consultas else 0.0,
            "tamano": len(self._datos),
            "capacidad": self.capacidad,
        }

    def __len__(self):
        return len(self._datos)
