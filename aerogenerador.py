#aerogenerador.py
from typing import List, Optional, Any
from componentes import ParteAerogenerador
from sensores import SensorVelocidadViento, SensorTemperatura
from curvas import CurvaPotencia, CurvaPotenciaBaja, CurvaPotenciaAlta
from viento import VientoFactory
from validaciones import PreFlightChecklist
from alarmas import AlarmManager

class AerogeneradorBase:
    ESTADOS = ["mantenimiento", "generando", "pausado", "stop", "stop_critico", "espera_viento"]
    
    def __init__(self, id_a: int, curva_potencia: CurvaPotencia):
        self.id_a = id_a
        self._estado: str = "pausado" #Encapsulamiento, uso de atributos protegidos
        self.curva = curva_potencia
        self.potencia_actual: float = 0.0
        
        # Variables de control internas
        self._bloqueo_manual: bool = False #Encapsulamiento, Se evita que agentes externos modifiquen el estado directamente  
        self._bloqueo_critico: bool = False #Encapsulamiento, Se obliga a usar métodos públicos 
        self._timer_rearme: int = 0         
        self.historial_potencia: List[float] = [0.0]*50 
        
        # Composicion
        self.buje = ParteAerogenerador("Buje")
        self.gondola = ParteAerogenerador("Gondola")
        self.torre = ParteAerogenerador("Torre")
        self.partes = [self.buje, self.gondola, self.torre] #Composición
        
        # Sensores
        self.buje.agregar_sensor("viento", SensorVelocidadViento("Buje"))
        self.gondola.agregar_sensor("temp", SensorTemperatura("Gondola"))

    # --- ENCAPSULAMIENTO: Getters ---
    def get_estado(self) -> str:
        return self._estado

    def es_bloqueo_critico(self) -> bool:
        return self._bloqueo_critico

    def get_timer_rearme(self) -> int:
        return self._timer_rearme

    # --- ENCAPSULAMIENTO: Metodos Publicos de Control (NO USAR _set_estado FUERA) ---
    
    def solicitar_marcha(self) -> str: #Defensibilidad
        """Intenta poner en marcha el aero. Retorna mensaje de exito/error."""
        if self._bloqueo_critico:
            return "Error: Bloqueo Critico Activo. Revise Status."
        
        self._bloqueo_manual = False
        self._cambiar_estado_interno("pausado") 
        return "OK"

    def forzar_parada_manual(self) -> None:
        """Usuario presiona boton PARAR."""
        self._bloqueo_manual = True
        self._cambiar_estado_interno("stop")

    def registrar_falla_externa(self, falla: Any) -> None:
        """Metodo para inyectar fallas de forma controlada."""
        # Buscamos la parte correspondiente o default a Buje
        self.buje.fallas_activas.append(falla) # Simplificacion
        AlarmManager.registrar_alarma(falla)
        self._bloqueo_critico = True
        self._cambiar_estado_interno("stop_critico")

    def realizar_mantenimiento(self) -> None:
        """Limpia fallas y desbloquea."""
        self._bloqueo_critico = False
        self._bloqueo_manual = False
        self._timer_rearme = 0
        for p in self.partes:
            p.fallas_activas = []
        self._cambiar_estado_interno("pausado")

    # --- Metodos Privados ---
    def _cambiar_estado_interno(self, nuevo: str) -> None:
        if nuevo in self.ESTADOS and nuevo != self._estado:
            self._estado = nuevo
            
    def obtener_viento(self) -> float: 
        return self.buje.obtener_lectura("viento")
    
    def obtener_temp(self) -> float: 
        return self.gondola.obtener_lectura("temp")

    def actualizar_sensores(self) -> None:
        for p in self.partes: p.actualizar_lecturas()

    def ejecutar_ciclo_control(self) -> None:
        """Logica principal del automata."""
        # Historial
        self.historial_potencia.pop(0)
        self.historial_potencia.append(self.potencia_actual)

        # 1. Bloqueos
        if self._bloqueo_critico:
            self._cambiar_estado_interno("stop_critico")
            self.potencia_actual = 0
            return

        if self._bloqueo_manual:
            self._cambiar_estado_interno("stop")
            self.potencia_actual = 0
            return
        
        # 2. Autodiagnostico
        if AlarmManager.hay_criticas_activas(self):
            self._bloqueo_critico = True
            self._cambiar_estado_interno("stop_critico")
            self.potencia_actual = 0
            return

        # 3. Timer Viento
        if self._timer_rearme > 0:
            self._timer_rearme -= 1
            self._cambiar_estado_interno("espera_viento")
            self.potencia_actual = 0
            return

        # 4. Logica Operativa
        v = self.obtener_viento()
        
        if v >= 25:
            self._timer_rearme = 10
            self._cambiar_estado_interno("espera_viento")
            self.potencia_actual = 0
            return

        condicion = VientoFactory.crear_condicion(v) # Usando Factory
        estado_deseado = condicion.aplicar_efecto(self)

        if estado_deseado == "generando":
            ok, _ = PreFlightChecklist.validar(self)
            if not ok:
                self._cambiar_estado_interno("pausado")
                self.potencia_actual = 0
                return
            
            self.potencia_actual = self.curva.calcular_potencia(v)
        else:
            self.potencia_actual = 0
            
        self._cambiar_estado_interno(estado_deseado)

class AG_BajaPotencia(AerogeneradorBase): #Extensibilidad
    def __init__(self, id_a: int):
        super().__init__(id_a, CurvaPotenciaBaja())
        self.MAX_TEMP = 80 

class AG_AltaPotencia(AerogeneradorBase): #Extensibilidad
    def __init__(self, id_a: int):
        super().__init__(id_a, CurvaPotenciaAlta())
        self.MAX_TEMP = 95