# controlador.py
from typing import List, Dict
from aerogenerador import AerogeneradorBase, AG_BajaPotencia, AG_AltaPotencia
from fallas import FallaMecanica

class SimuladorController: #SRP coordinar la logica de negocio
    """Clase responsable de la logica de negocio (SRP).
    La Interfaz Grafica hablara con esta clase, NO con los aerogeneradores directamente.
    """
    def __init__(self):
        self.ags: List[AerogeneradorBase] = []
        self._inicializar_parque()

    def _inicializar_parque(self):
        self.ags.append(AG_BajaPotencia(1))
        self.ags.append(AG_AltaPotencia(2))
        self.ags.append(AG_AltaPotencia(3))

    def agregar_aerogenerador(self, tipo: str) -> int: #Acoplamiento Debil
        new_id = len(self.ags) + 1
        nuevo = None
        if tipo == "BAJA":
            nuevo = AG_BajaPotencia(new_id)
        else:
            nuevo = AG_AltaPotencia(new_id)
        
        nuevo.forzar_parada_manual() # Inicia parado
        self.ags.append(nuevo)
        return new_id

    def avanzar_ciclo_simulacion(self) -> float:
        """Ejecuta un paso de tiempo en todo el parque."""
        total_kw = 0.0
        for ag in self.ags:
            ag.actualizar_sensores()
            ag.ejecutar_ciclo_control()
            total_kw += ag.potencia_actual
        return total_kw

    def provocar_falla_demo(self):
        if not self.ags: return
        target = self.ags[0]
        falla = FallaMecanica("Rotor", "RUPTURA DE PALA DETECTADA", "Critica")
        target.registrar_falla_externa(falla)