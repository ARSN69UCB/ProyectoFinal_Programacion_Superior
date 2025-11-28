# componentes.py
from typing import List, Dict, Any, Optional

class ParteAerogenerador: #Encapsulamiento / Modularidad
    """Representa una seccion fisica (Buje, Torre, etc)."""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.sensores: Dict[str, Any] = {} 
        self.fallas_activas: List[Any] = []

    def agregar_sensor(self, key: str, sensor: Any) -> None:
        self.sensores[key] = sensor

    def actualizar_lecturas(self) -> None:
        for sensor in self.sensores.values():
            sensor.leer_valor()
            
    def obtener_lectura(self, key: str) -> Optional[float]:
        if key in self.sensores:
            # Accedemos al atributo protegido _valor de la clase Sensor
            return self.sensores[key]._valor
        return None