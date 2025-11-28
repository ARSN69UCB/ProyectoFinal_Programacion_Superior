#curvas.py
class CurvaPotencia:
    """Clase Base para el calculo de potencia."""
    def calcular_potencia(self, velocidad_viento):
        raise NotImplementedError

class CurvaPotenciaBaja(CurvaPotencia):
    POTENCIA_NOMINAL = 800 # kW

    def calcular_potencia(self, v): #Polimorfismo
        if v < 5 or v > 20: return 0
        if v < 12: return self.POTENCIA_NOMINAL * (v - 5) / 7
        return self.POTENCIA_NOMINAL

class CurvaPotenciaAlta(CurvaPotencia):
    POTENCIA_NOMINAL = 2500 # kW
    def calcular_potencia(self, v):
        if v < 8 or v > 25: return 0
        if v < 15: return self.POTENCIA_NOMINAL * (v - 8) / 7
        return self.POTENCIA_NOMINAL