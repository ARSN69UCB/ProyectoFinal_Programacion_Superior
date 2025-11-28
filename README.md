# SIMULADOR SCADA: PARQUE EOLICO

Este proyecto es una simulacion de un sistema **SCADA (Supervisory Control and Data Acquisition)** diseñado para la gestion, monitoreo y control de un parque eolico.

Desarrollado como Proyecto Final universitario, este software aplica estrictamente los pilares de la **Programacion Orientada a Objetos (POO)** y una arquitectura **MVC (Modelo-Vista-Controlador)** para garantizar un codigo limpio, modular y escalable.

---

##  Funcionalidades Principales

### 1. Monitoreo en Tiempo Real
- **Visualizacion Grafica:** Interfaz construida con `tkinter` que muestra el estado de cada aerogenerador.
- **Animaciones:** Las turbinas giran dinamicamente cuando estan generando energia.
- **Indicadores de Estado:** Codigo de colores para identificar rapidamente la situacion:
  - **BLANCO:** Generando (Normal).
  - **NARANJA:** Pausado (Viento insuficiente).
  - **VIOLETA:** Espera/Rearme (Viento excesivo > 25 m/s).
  - **ROJO:** Stop (Falla critica o parada manual).

### 2. Logica de Control y Seguridad
- **Sistema de Bloqueos:** - **Manual:** Si el usuario detiene una turbina, esta no arranca automaticamente hasta recibir la orden explicita.
  - **Critico:** Si se detecta una falla grave, la turbina se bloquea totalmente.
- **Proteccion Climatica:** Logica automatica que detiene la turbina si el viento supera los limites de seguridad (Cut-out speed), con un temporizador de rearme automatico.

### 3. Gestion de Fallas y Mantenimiento
- **Simulacion de Caos:** Capacidad de inyectar fallas graves (ej. Ruptura de Pala) para probar la robustez del sistema.
- **Panel de Status:** Ventana emergente con graficos de curva de potencia y lista de fallas activas.
- **Mantenimiento:** Funcionalidad para corregir fallas, limpiar logs y reiniciar los sistemas bloqueados.

### 4. Escalabilidad
- **Agregar Turbinas:** El sistema permite añadir nuevos aerogeneradores (de Baja o Alta potencia) durante la ejecucion sin detener el programa.

---

##  Arquitectura del Software

El proyecto sigue una arquitectura **MVC** desacoplada:

1.  **VISTA (`interfaz.py`):** Maneja la GUI. No contiene logica de negocio, solo dibuja y recibe eventos.
2.  **CONTROLADOR (`controlador.py`):** Orquesta la simulacion, maneja la lista de turbinas y conecta la vista con el modelo.
3.  **MODELO (`aerogenerador.py`):** Contiene la logica fisica, maquina de estados y reglas de negocio.

### Estructura de Archivos
Asegurate de tener los siguientes archivos en la misma carpeta:

- `interfaz.py`        -> **ARCHIVO PRINCIPAL (EJECUTABLE)**
- `controlador.py`     -> Logica de orquestacion (Controller).
- `aerogenerador.py`   -> Logica de la turbina (Model).
- `componentes.py`     -> Definicion de partes fisicas (Buje, Torre).
- `sensores.py`        -> Clases abstractas e implementacion de sensores.
- `alarmas.py`         -> Singleton para gestion de logs.
- `validaciones.py`    -> Checklist de seguridad (Static methods).
- `viento.py`          -> Factory Pattern para condiciones climaticas.
- `curvas.py`          -> Formulas matematicas de potencia.
- `fallas.py`          -> Estructura de datos para errores.

---

##  Guia de Instalacion y Ejecucion

Este proyecto utiliza **Python puro** y librerias estandar. No requiere instalacion de paquetes externos.

### Requisitos Previos
- Tener instalado **Python 3.8** o superior.

### Pasos para Ejecutar

1. **Descargar el codigo:**
   Clona este repositorio o descarga los archivos en una carpeta local.

2. **Abrir la terminal:**
   Navega hasta la carpeta del proyecto usando la linea de comandos (CMD o Terminal).
   ```bash
   cd ruta/a/tu/carpeta

3. **Ejecutar el programa:**
   El punto de entrada es la interfaz. Ejecuta el siguiente comando:
     python interfaz.py

4. **Iniciar Sesion:**
   Aparecera una ventana de login. Usa las credenciales por defecto:
     Usuario: admin
     Contrasena: 1234
