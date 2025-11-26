class ParteAerogenerador:
    """Representa una seccion fisica (Buje, Torre, etc)."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.sensores = {} # Diccionario de sensores
        self.fallas_activas = []

    def agregar_sensor(self, key, sensor):
        self.sensores[key] = sensor

    def actualizar_lecturas(self):
        for sensor in self.sensores.values():
            sensor.leer_valor()
            
    def obtener_lectura(self, key):
        if key in self.sensores:
            return self.sensores[key]._valor
        return None