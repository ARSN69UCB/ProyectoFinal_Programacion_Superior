import random

class Sensor:
    """Clase Padre Abstracta para todos los sensores."""
    def __init__(self, ubicacion):
        self.ubicacion = ubicacion 
        self._valor = 0

    def leer_valor(self):
        raise NotImplementedError("Debe implementarse en subclase.")

    def __str__(self):
        return f"{self.__class__.__name__} @ {self.ubicacion}: {self._valor}"

class SensorVelocidadViento(Sensor):
    def leer_valor(self):
        # Simulacion: viento entre 0 y 35 m/s
        self._valor = random.randint(0, 35) 
        return self._valor

class SensorTemperatura(Sensor):
    def leer_valor(self):
        # Simulacion: temp entre 40 y 95 C
        self._valor = random.randint(40, 95) 
        return self._valor