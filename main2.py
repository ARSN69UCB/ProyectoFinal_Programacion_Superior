import os
import time
import json
from aerogenerador import AG_BajaPotencia, AG_AltaPotencia
from gestores import AlarmManager
from fallas import FallaElectrica, FallaMecanica

class SistemaEconomico:
    PRECIO_KWH = 0.15  # USD por kWh generado
    COSTO_MANTENIMIENTO = 50 # USD por ciclo si esta en mantenimiento

    @staticmethod
    def calcular_balance(ags):
        ingresos = 0
        gastos = 0
        for ag in ags.values():
            # Ingreso por generacion actual
            ingresos += ag.potencia_actual * SistemaEconomico.PRECIO_KWH
            
            # Gasto si esta en mantenimiento
            if ag._estado == "mantenimiento":
                gastos += SistemaEconomico.COSTO_MANTENIMIENTO
        
        return ingresos - gastos

class ParqueEolicoSCADA:
    def __init__(self, nombre):
        self.nombre = nombre
        self.ags = {}
        self.dinero_total = 0.0

    def agregar(self, ag):
        ag.id_a = len(self.ags) + 1
        self.ags[ag.id_a] = ag

    def guardar_estado(self):
        """Persistencia: Guarda datos basicos en JSON (KISS)"""
        datos = {
            "nombre": self.nombre,
            "dinero": self.dinero_total,
            "ags_count": len(self.ags)
        }
        try:
            with open("estado_parque.json", "w") as f:
                json.dump(datos, f)
            print(" [DISK] Estado guardado correctamente.")
        except Exception as e:
            print(f" [ERROR] No se pudo guardar: {e}")

    def renderizar_dashboard(self, ciclo):
        # Limpiar pantalla para efecto "Tiempo Real"
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"========================================")
        print(f" SCADA SYSTEM: {self.nombre.upper()}")
        print(f" Ciclo: {ciclo} | Balance: ${self.dinero_total:,.2f}")
        print(f"========================================")
        print(f"{'ID':<4} {'TIPO':<15} {'ESTADO':<15} {'VIENTO':<10} {'TEMP':<8} {'POTENCIA':<10}")
        print("-" * 70)

        total_kw = 0
        for ag in self.ags.values():
            nombre_corto = "AG-Alta" if isinstance(ag, AG_AltaPotencia) else "AG-Baja"
            viento = ag.obtener_viento()
            temp = ag.obtener_temp()
            
            # Formato de colores simple usando strings (Opcional, aqui texto plano)
            print(f"{ag.id_a:<4} {nombre_corto:<15} {ag._estado.upper():<15} {viento}m/s      {temp}C      {ag.potencia_actual:.1f} kW")
            total_kw += ag.potencia_actual
        
        print("-" * 70)
        print(f"TOTAL GENERACION: {total_kw:.2f} kW")
        
        # Mostrar ultimas 3 alarmas
        print("\n [!] ULTIMOS EVENTOS / ALARMAS:")
        for log in AlarmManager.log[-3:]:
            print(f" {log}")

    def simular_operacion_continua(self):
        ciclo = 1
        try:
            while True:
                # 1. Actualizar logica fisica
                for ag in self.ags.values():
                    ag.actualizar()
                    ag.controlador()
                
                # 2. Calcular Economia
                balance_ciclo = SistemaEconomico.calcular_balance(self.ags)
                self.dinero_total += balance_ciclo
                
                # 3. Dibujar interfaz
                self.renderizar_dashboard(ciclo)
                
                # 4. Input simulado (Aleatoriedad para que pasen cosas)
                import random
                if random.randint(0, 100) > 95: # 5% prob de evento random
                    self.evento_aleatorio()

                # Guardado automatico cada 10 ciclos
                if ciclo % 10 == 0:
                    self.guardar_estado()

                print("\n(Presiona Ctrl+C para salir y detener simulacion)")
                time.sleep(2) # Pausa de 2 segundos para ver datos
                ciclo += 1
                
        except KeyboardInterrupt:
            print("\n\n [STOP] Simulacion detenida por usuario.")

    def evento_aleatorio(self):
        """Genera caos aleatorio para probar robustez"""
        target_id = random.randint(1, len(self.ags))
        ag = self.ags[target_id]
        
        # Simulamos rafaga de viento fuerte
        ag.buje.sensores['viento']._valor = 45 
        AlarmManager.registrar_alarma(f"Simulacion: Rafaga detectada en AG{target_id}")

def main():
    sistema = ParqueEolicoSCADA("Parque Universitario")
    
    # Configuracion Inicial
    sistema.agregar(AG_BajaPotencia(0))
    sistema.agregar(AG_AltaPotencia(0))
    sistema.agregar(AG_AltaPotencia(0))
    
    # Arranque inicial manual
    for ag in sistema.ags.values():
        ag._set_estado("pausado")

    # Iniciar Loop Infinito
    sistema.simular_operacion_continua()

if __name__ == "__main__":
    import random # Necesario para el evento aleatorio dentro de main
    main()