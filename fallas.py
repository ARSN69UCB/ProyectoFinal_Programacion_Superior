#fallas.py
import time

class Falla:
    """Clase Padre para tipos de fallas."""
    def __init__(self, ubicacion, mensaje, nivel="Advertencia"):
        self.ubicacion = ubicacion
        self.mensaje = mensaje
        self.nivel_peligro = nivel
        self.timestamp = time.time()
        self.id_ag = None # Se asignara cuando ocurra en un AG especifico

    def __str__(self):
        return f"[{self.nivel_peligro}] AG{self.id_ag} ({self.ubicacion}): {self.mensaje}"

class FallaMecanica(Falla):
    def __init__(self, ubicacion, mensaje, nivel="Critica"):
        super().__init__(ubicacion, mensaje, nivel)

class FallaElectrica(Falla):
    def __init__(self, ubicacion, mensaje, nivel="Advertencia"):
        super().__init__(ubicacion, mensaje, nivel)