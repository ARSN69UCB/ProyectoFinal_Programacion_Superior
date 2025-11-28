# validaciones.py
from typing import Tuple, Any
from alarmas import AlarmManager

class PreFlightChecklist: #Cohesion
    """Validaciones de seguridad."""
    
    @staticmethod #Testeabilidad
    def validar(ag: Any) -> Tuple[bool, str]:
        # 1. Fallas
        if AlarmManager.hay_criticas_activas(ag):
            return False, "Fallas Criticas detectadas."
        
        # 2. Viento
        v = ag.obtener_viento()
        if v is None or v < 5:
            return False, f"Viento insuficiente ({v} m/s)."

        # 3. Temperatura
        t = ag.obtener_temp()
        if t is None or t > ag.MAX_TEMP:
            return False, f"Temperatura alta ({t} C)."

        return True, "OK"