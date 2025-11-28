# alarmas.py
import time
from typing import List, Any # Para type hinting

class AlarmManager: #Cohesion
    """Gestiona el registro centralizado de alarmas."""
    log: List[str] = []

    @classmethod #Testeabilidad
    def registrar_alarma(cls, falla: Any) -> None:
        t_str = time.strftime('%H:%M:%S')
        mensaje = f"[{t_str}] ALARMA SYSTEM -> {falla}"
        cls.log.append(mensaje)
        print(mensaje)

    @classmethod
    def hay_criticas_activas(cls, aerogenerador: Any) -> bool:
        for parte in aerogenerador.partes:
            for falla in parte.fallas_activas:
                if falla.nivel_peligro == "Critica":
                    return True
        return False