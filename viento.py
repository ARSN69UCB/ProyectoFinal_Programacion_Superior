class CondicionViento:
    def __init__(self, velocidad):
        self.velocidad = velocidad
    
    def aplicar_efecto(self, aerogenerador):
        raise NotImplementedError

class VientoExtremo(CondicionViento):
    def aplicar_efecto(self, ag): return "stop"

class VientoInsuficiente(CondicionViento):
    def aplicar_efecto(self, ag): return "pausado"

class VientoOptimo(CondicionViento):
    def aplicar_efecto(self, ag): return "generando"

class VientoMinimo(CondicionViento):
    def aplicar_efecto(self, ag): return "generando"

# Factory Function
def obtener_condicion_viento(velocidad):
    if velocidad < 5: return VientoInsuficiente(velocidad)
    if 5 <= velocidad < 8: return VientoMinimo(velocidad)
    if 8 <= velocidad < 25: return VientoOptimo(velocidad)
    return VientoExtremo(velocidad)