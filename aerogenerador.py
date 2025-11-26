from partes import ParteAerogenerador
from sensores import SensorVelocidadViento, SensorTemperatura
from curvas import CurvaPotenciaBaja, CurvaPotenciaAlta
from viento import obtener_condicion_viento
from fallas import FallaMecanica
from gestores import AlarmManager, PreFlightChecklist

class AerogeneradorBase:
    # ### REUSABILIDAD (DRY - Don't Repeat Yourself) ###
    # Al definir los estados y logica aqui, evitamos escribirlo
    # en cada tipo de aerogenerador nuevo.
    ESTADOS = ["mantenimiento", "generando", "pausado", "stop", "stop_critico", "espera_viento"]
    MAX_TEMP = 85
    
    def __init__(self, id_a, curva_potencia):
        self.id_a = id_a
        # ### ENCAPSULAMIENTO ###
        # Usamos el guion bajo (_) para indicar que '_estado' es privado/protegido.
        # Nadie deberia hacer 'ag._estado = "algo"' desde fuera.
        # Se debe usar los metodos controlados.
        self._estado = "pausado" # Arranca en pausa listo para operar
        # ### ACOPLAMIENTO DEBIL (Inyeccion de Dependencia) ###
        # No estamos "casados" con una formula matematica fija dentro de la clase.
        # Le pasamos el objeto 'curva_potencia' desde fuera. Si manana cambia la fisica,
        # solo cambiamos el objeto curva, no esta clase.
        self.curva = curva_potencia
        self.potencia_actual = 0
        self.energia_acumulada = 0
        
        # --- NUEVAS VARIABLES DE CONTROL ---
        self.bloqueo_manual = False   # True si el usuario dio CLICK en PARAR
        self.bloqueo_critico = False  # True si hay falla grave (incendio, rotura)
        self.timer_rearme = 0         # Contador para esperar 10s tras viento extremo
        self.historial_potencia = [0]*50 # Ultimos 50 valores para el grafico
        
        # Composicion
        self.buje = ParteAerogenerador("Buje")
        self.gondola = ParteAerogenerador("Gondola")
        self.torre = ParteAerogenerador("Torre")
        self.partes = [self.buje, self.gondola, self.torre]
        
        # Sensores
        self.buje.agregar_sensor("viento", SensorVelocidadViento("Buje"))
        self.gondola.agregar_sensor("temp", SensorTemperatura("Gondola"))
        
    def _set_estado(self, nuevo):
        # ### DEFENSIBILIDAD (Programacion Defensiva) ###
        # Validamos que el estado exista antes de asignarlo.
        # Protegemos al objeto de entrar en un estado invalido/corrupto.
        if nuevo in self.ESTADOS and nuevo != self._estado:
            # print(f"AG{self.id_a}: Estado {self._estado} -> {nuevo}") # Debug opcional
            self._estado = nuevo
            
    def obtener_viento(self): return self.buje.obtener_lectura("viento")
    def obtener_temp(self): return self.gondola.obtener_lectura("temp")

    def actualizar(self):
        for p in self.partes: p.actualizar_lecturas()
        
    def corregir_fallas(self):
        """El usuario llama a esto para arreglar el aero."""
        self.bloqueo_critico = False
        self.bloqueo_manual = False
        self.timer_rearme = 0
        # Limpiar listas de fallas
        for p in self.partes:
            p.fallas_activas = []
        self._set_estado("pausado")
        print(f"AG{self.id_a}: Mantenimiento realizado. Fallas corregidas.")

    def controlador(self):
        # 0. Actualizar historial para graficos
        self.historial_potencia.pop(0)
        self.historial_potencia.append(self.potencia_actual)

        # ### DEFENSIBILIDAD ###
        # El sistema se defiende a si mismo. Si hay bloqueo critico, 
        # se niega a ejecutar logica de generacion.
        # 1. PRIORIDAD MAXIMA: Bloqueo Critico (Fallas Graves)
        if self.bloqueo_critico:
            self._set_estado("stop_critico")
            self.potencia_actual = 0
            return

        # 2. PRIORIDAD ALTA: Bloqueo Manual (Usuario lo detuvo)
        if self.bloqueo_manual:
            self._set_estado("stop") # Stop simple
            self.potencia_actual = 0
            return
        
        # 3. Detectar nuevas fallas criticas (Autodiagnostico)
        if AlarmManager.hay_criticas_activas(self):
            self.bloqueo_critico = True
            self._set_estado("stop_critico")
            self.potencia_actual = 0
            return

        # 4. PRIORIDAD MEDIA: Timer de seguridad por Viento
        if self.timer_rearme > 0:
            self.timer_rearme -= 1
            self._set_estado("espera_viento")
            self.potencia_actual = 0
            return

        # --- LOGICA NORMAL DE OPERACION ---
        
        v = self.obtener_viento()
        
        # Regla: Si el viento es extremo (>25), parar y esperar 10 segundos
        if v >= 25:
            self.timer_rearme = 10 # 10 ciclos de espera
            self._set_estado("espera_viento")
            self.potencia_actual = 0
            return

        # Obtener condicion y aplicar
        condicion = obtener_condicion_viento(v)
        estado_deseado = condicion.aplicar_efecto(self)

        # Validacion final de arranque
        if estado_deseado == "generando":
            ok, msg = PreFlightChecklist.validar(self)
            if not ok:
                self._set_estado("pausado")
                self.potencia_actual = 0
                return
            
            self.potencia_actual = self.curva.calcular_potencia(v)
        else:
            self.potencia_actual = 0
            
        self._set_estado(estado_deseado)

# ### EXTENSIBILIDAD (Open/Closed Principle) ###
# Podemos crear infinitos tipos nuevos (MediaPotencia, Offshore, Nuclear, etc.)
# sin tocar ni una linea de la clase 'AerogeneradorBase'.
# El sistema esta abierto a extension, cerrado a modificacion.
class AG_BajaPotencia(AerogeneradorBase):
    def __init__(self, id_a):
        super().__init__(id_a, CurvaPotenciaBaja())
        self.MAX_TEMP = 80 

class AG_AltaPotencia(AerogeneradorBase):
    def __init__(self, id_a):
        super().__init__(id_a, CurvaPotenciaAlta())
        self.MAX_TEMP = 95