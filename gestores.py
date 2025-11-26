import time

class AlarmManager:
    """Singleton para registro centralizado de alarmas."""
    log = []
    # ### COHESION (Alta Cohesion / SRP) ###
    # Esta clase tiene UNA sola responsabilidad: Gestionar el log de alarmas.
    # No calcula viento, no dibuja graficos, no controla motores.
    # Si falla el registro de alarmas, sabemos que el error esta AQUI.
    @classmethod
    def registrar_alarma(cls, falla):
        t_str = time.strftime('%H:%M:%S')
        mensaje = f"[{t_str}] ALARMA SYSTEM -> {falla}"
        cls.log.append(mensaje)
        print(mensaje) # Salida a consola simulando pantalla SCADA
    # ### MANTENIBILIDAD / TESTEABILIDAD ###
    # Al ser metodos estaticos puros que reciben un objeto y devuelven True/False,
    # es extremadamente facil crear un script de prueba (Unit Test) para verificar esto
    # sin necesidad de arrancar toda la interfaz grafica.
    @classmethod
    def hay_criticas_activas(cls, aerogenerador):
        for parte in aerogenerador.partes:
            for falla in parte.fallas_activas:
                if falla.nivel_peligro == "Critica":
                    return True
        return False

class PreFlightChecklist:
    """Verificaciones de seguridad antes de arrancar."""
    
    @staticmethod
    def validar(ag):
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