# viento.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aerogenerador import AerogeneradorBase

class CondicionViento(ABC): #Abstraccion
    def __init__(self, velocidad: float):
        self.velocidad = velocidad
    
    @abstractmethod
    def aplicar_efecto(self, aerogenerador: 'AerogeneradorBase') -> str: #Polimorfismo
        pass

class VientoExtremo(CondicionViento): #Herencia
    def aplicar_efecto(self, aerogenerador: 'AerogeneradorBase') -> str: 
        return "espera_viento"

class VientoInsuficiente(CondicionViento):
    def aplicar_efecto(self, aerogenerador: 'AerogeneradorBase') -> str: 
        return "pausado"

class VientoOptimo(CondicionViento):
    def aplicar_efecto(self, aerogenerador: 'AerogeneradorBase') -> str: 
        return "generando"

class VientoFactory: #Patron Factory
    """Fabrica estatica para eliminar metodos globales."""
    @staticmethod
    def crear_condicion(velocidad: float) -> CondicionViento:
        if velocidad < 5: return VientoInsuficiente(velocidad)
        if 5 <= velocidad < 25: return VientoOptimo(velocidad)
        return VientoExtremo(velocidad)