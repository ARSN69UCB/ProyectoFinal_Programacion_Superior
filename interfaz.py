import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
from controlador import SimuladorController
from alarmas import AlarmManager
from aerogenerador import AG_AltaPotencia, AG_BajaPotencia
from fallas import FallaMecanica

# --- CONFIGURACION DE COLORES ---
COLOR_BG = "#1e1e1e"
COLOR_PANEL = "#2d2d2d"
COLOR_TEXT = "#ffffff"
COLOR_ACCENT = "#007acc"
COLOR_SUCCESS = "#4caf50"
COLOR_WARNING = "#ff9800"
COLOR_DANGER = "#f44336"
COLOR_GRAPH = "#00e5ff"

class Estilos:
    @staticmethod
    def configurar():
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_PANEL, relief="flat")
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXT)
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background=COLOR_BG, foreground=COLOR_ACCENT)
        style.configure("BigNumber.TLabel", font=("Consolas", 24, "bold"), background=COLOR_BG, foreground=COLOR_SUCCESS)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background=COLOR_PANEL, foreground=COLOR_ACCENT)
        
        style.configure("TButton", font=("Segoe UI", 9, "bold"), background=COLOR_ACCENT, foreground="white", borderwidth=0)
        style.map("TButton", background=[('active', '#005f9e')])
        style.configure("Danger.TButton", background=COLOR_DANGER)
        style.map("Danger.TButton", background=[('active', '#d32f2f')])
        style.configure("Success.TButton", background=COLOR_SUCCESS)

# --- VENTANA DE LOGIN (RECUPERADA) ---
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Acceso Seguro - SCADA")
        self.geometry("300x250")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.on_success = on_success
        
        # Centrar
        x = (self.winfo_screenwidth() // 2) - 150
        y = (self.winfo_screenheight() // 2) - 125
        self.geometry(f"+{x}+{y}")

        ttk.Label(self, text="INICIAR SESION", style="Title.TLabel").pack(pady=20)
        
        ttk.Label(self, text="Usuario:", background=COLOR_BG, foreground=COLOR_TEXT).pack(anchor="w", padx=20)
        self.entry_user = ttk.Entry(self)
        self.entry_user.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(self, text="Contrasena:", background=COLOR_BG, foreground=COLOR_TEXT).pack(anchor="w", padx=20)
        self.entry_pass = ttk.Entry(self, show="*")
        self.entry_pass.pack(fill="x", padx=20, pady=5)
        
        ttk.Button(self, text="ACCEDER", command=self.verificar).pack(pady=20, fill="x", padx=20)

        # Protocolo para cerrar app si cierran login
        self.protocol("WM_DELETE_WINDOW", parent.destroy)

    def verificar(self):
        # Credenciales Hardcodeadas (KISS)
        if self.entry_user.get() == "admin" and self.entry_pass.get() == "1234":
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

# --- VENTANA POPUP: DETALLES Y GRAFICO ---
class VentanaDetalle(tk.Toplevel):
    def __init__(self, parent, aerogenerador):
        super().__init__(parent)
        self.ag = aerogenerador
        self.title(f"Detalles Tecnicos AG-{self.ag.id_a}")
        self.geometry("600x500")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        
        ttk.Label(self, text="Curva de Generacion (Tiempo Real)", style="TLabel", font=("Segoe UI", 12)).pack(pady=10)
        self.canvas_graph = tk.Canvas(self, width=500, height=200, bg="black", highlightthickness=1, highlightbackground=COLOR_PANEL)
        self.canvas_graph.pack()
        
        ttk.Label(self, text="Catalogo de Fallas / Mantenimiento", style="TLabel", font=("Segoe UI", 12)).pack(pady=(20,5))
        
        frame_fallas = ttk.Frame(self, style="TFrame")
        frame_fallas.pack(fill="both", expand=True, padx=20)
        
        self.listbox_fallas = tk.Listbox(frame_fallas, bg=COLOR_PANEL, fg="white", height=6)
        self.listbox_fallas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame_fallas, orient="vertical", command=self.listbox_fallas.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox_fallas.config(yscrollcommand=scrollbar.set)
        
        btn_corregir = ttk.Button(self, text="CORREGIR FALLAS Y REINICIAR SISTEMA", style="Success.TButton", command=self.accion_corregir)
        btn_corregir.pack(pady=20, fill="x", padx=50)

        self.actualizar_popup()

    def dibujar_grafico(self):
        self.canvas_graph.delete("all")
        data = self.ag.historial_potencia
        w = 500
        h = 200
        max_val = 2600 
        step = w / len(data)
        
        self.canvas_graph.create_line(0, h/2, w, h/2, fill="#333", dash=(2,2))

        points = []
        for i, val in enumerate(data):
            x = i * step
            y = h - (val / max_val * h)
            points.append(x)
            points.append(y)
        
        if len(points) >= 4:
            self.canvas_graph.create_line(points, fill=COLOR_GRAPH, width=2, smooth=True)

    def actualizar_lista_fallas(self):
        self.listbox_fallas.delete(0, tk.END)
        encontradas = False
        for parte in self.ag.partes:
            for falla in parte.fallas_activas:
                encontradas = True
                estado_txt = "[ACTIVO]" if self.ag.es_bloqueo_critico() else "[HISTORICO]"
                self.listbox_fallas.insert(tk.END, f"{estado_txt} {parte.nombre}: {falla.mensaje}")
        
        if not encontradas:
            self.listbox_fallas.insert(tk.END, "Sin fallas registradas. Sistema nominal.")

    def accion_corregir(self):
        self.ag.realizar_mantenimiento()
        messagebox.showinfo("Mantenimiento", "Fallas corregidas. El aerogenerador ha sido desbloqueado.\nPuede ponerlo en marcha nuevamente.")
        self.actualizar_lista_fallas()

    def actualizar_popup(self):
        if self.winfo_exists():
            self.dibujar_grafico()
            self.actualizar_lista_fallas()
            self.after(1000, self.actualizar_popup)

# --- WIDGET AEROGENERADOR ---
class WidgetAerogenerador(ttk.Frame):
    def __init__(self, parent, aerogenerador):
        super().__init__(parent, style="Card.TFrame", padding=10)
        self.ag = aerogenerador
        
        self.lbl_titulo = ttk.Label(self, text=f"AG-{self.ag.id_a}", style="Header.TLabel")
        self.lbl_titulo.pack(anchor="w")
        
        tipo = "Alta Potencia" if isinstance(self.ag, AG_AltaPotencia) else "Baja Potencia"
        self.lbl_tipo = ttk.Label(self, text=tipo, style="Card.TLabel", font=("Segoe UI", 8))
        self.lbl_tipo.pack(anchor="w")

        self.canvas = tk.Canvas(self, width=150, height=150, bg=COLOR_PANEL, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.dibujar_base()

        self.frame_datos = ttk.Frame(self, style="Card.TFrame")
        self.frame_datos.pack(fill="x", pady=5)
        
        self.var_estado = tk.StringVar(value="---")
        self.var_potencia = tk.StringVar(value="0 kW")
        
        self._crear_fila_dato("Estado:", self.var_estado)
        self._crear_fila_dato("Potencia:", self.var_potencia)

        self.frame_btns = ttk.Frame(self, style="Card.TFrame")
        self.frame_btns.pack(fill="x", pady=5)
        
        ttk.Button(self.frame_btns, text="MARCHA", command=self.accion_marcha).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(self.frame_btns, text="PARAR", style="Danger.TButton", command=self.accion_parada).pack(side="right", fill="x", expand=True, padx=2)
        
        ttk.Button(self, text="STATUS / GRAFICO", command=self.abrir_detalles).pack(fill="x", pady=(5,0))

        self.angulo = 0

    def _crear_fila_dato(self, label, variable):
        f = ttk.Frame(self.frame_datos, style="Card.TFrame")
        f.pack(fill="x")
        ttk.Label(f, text=label, style="Card.TLabel").pack(side="left")
        ttk.Label(f, textvariable=variable, style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(side="right")

    def dibujar_base(self):
        self.canvas.create_rectangle(70, 80, 80, 150, fill="#7f8c8d", outline="")
        self.canvas.create_oval(65, 70, 85, 90, fill="#ecf0f1", outline="")

    def actualizar_animacion(self):
        self.canvas.delete("palas")
        color_palas = "#ecf0f1" 
        
        estado_actual = self.ag.get_estado()
        
        if "stop" in estado_actual: 
            color_palas = "#c0392b" 
        elif "espera" in estado_actual:
            color_palas = "#9b59b6" 
        elif estado_actual == "pausado":
            color_palas = "#f39c12" 
        
        cx, cy = 75, 80
        radio = 60
        
        if estado_actual == "generando":
            self.angulo = (self.angulo + 20) % 360
        
        for i in range(3):
            theta = math.radians(self.angulo + (i * 120))
            x_end = cx + radio * math.cos(theta)
            y_end = cy + radio * math.sin(theta)
            self.canvas.create_line(cx, cy, x_end, y_end, width=5, fill=color_palas, tags="palas", capstyle="round")

    def actualizar_datos_ui(self):
        estado_display = self.ag.get_estado().upper()
        timer = self.ag.get_timer_rearme()
        
        if timer > 0:
            estado_display = f"REARME ({timer}s)"
        
        self.var_estado.set(estado_display)
        self.var_potencia.set(f"{self.ag.potencia_actual:.1f} kW")
        self.actualizar_animacion()

    def accion_marcha(self):
        res = self.ag.solicitar_marcha()
        if res != "OK":
             messagebox.showerror("Error", res)
    
    def accion_parada(self):
        self.ag.forzar_parada_manual()

    def abrir_detalles(self):
        VentanaDetalle(self.winfo_toplevel(), self.ag)

# --- VENTANA PRINCIPAL ---
class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        Estilos.configurar()
        self.title("SCADA Eolico - Control Avanzado (SRP)")
        self.geometry("1200x800")
        self.configure(bg=COLOR_BG)
        
        # 1. OCULTAMOS LA VENTANA PRINCIPAL AL INICIO
        self.withdraw()

        # 2. INICIALIZAMOS EL CONTROLADOR
        self.controller = SimuladorController()
        
        self.widgets_ag = []
        
        # 3. LANZAMOS LA VENTANA DE LOGIN
        # Pasamos 'self.mostrar_dashboard' como la funcion a ejecutar si el login es correcto
        LoginWindow(self, self.mostrar_dashboard)

    def mostrar_dashboard(self):
        """Este metodo solo se ejecuta si el usuario pone bien la clave"""
        self.deiconify() # Volvemos a mostrar la ventana principal
        self._construir_interfaz()
        self._loop_simulacion()

    def _construir_interfaz(self):
        frame_top = ttk.Frame(self, style="TFrame")
        frame_top.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(frame_top, text="DASHBOARD PARQUE EOLICO", style="Title.TLabel").pack(side="left")
        
        frame_total = ttk.Frame(frame_top, style="Card.TFrame", padding=10)
        frame_total.pack(side="right")
        ttk.Label(frame_total, text="POTENCIA TOTAL", style="Card.TLabel").pack()
        self.lbl_total_potencia = ttk.Label(frame_total, text="0.0 kW", style="BigNumber.TLabel", background=COLOR_PANEL)
        self.lbl_total_potencia.pack()

        frame_toolbar = ttk.Frame(self, style="TFrame")
        frame_toolbar.pack(fill="x", padx=20, pady=5)
        
        ttk.Button(frame_toolbar, text="+ AGREGAR AEROGENERADOR", command=self.agregar_nuevo_aero).pack(side="left")
        ttk.Button(frame_toolbar, text="! PROVOCAR FALLA GRAVE (DEMO)", style="Danger.TButton", command=self.demo_falla).pack(side="right")

        canvas_scroll = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas_scroll.xview)
        self.frame_grid = ttk.Frame(canvas_scroll, style="TFrame")

        self.frame_grid.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=self.frame_grid, anchor="nw")
        canvas_scroll.configure(xscrollcommand=scrollbar.set)

        scrollbar.pack(side="bottom", fill="x")
        canvas_scroll.pack(side="bottom", fill="both", expand=True, padx=20)
        
        self.refrescar_grid()

    def refrescar_grid(self):
        for w in self.frame_grid.winfo_children():
            w.destroy()
        self.widgets_ag = []
        
        for ag in self.controller.ags:
            w = WidgetAerogenerador(self.frame_grid, ag)
            w.pack(side="left", padx=10, pady=10, anchor="n")
            self.widgets_ag.append(w)

    def agregar_nuevo_aero(self):
        resp = simpledialog.askinteger("Nuevo Aero", "Ingrese potencia esperada (kW):\n< 1000 para Baja Potencia\n> 1000 para Alta Potencia", minvalue=100, maxvalue=5000)
        if resp:
            tipo = "BAJA" if resp < 1000 else "ALTA"
            new_id = self.controller.agregar_aerogenerador(tipo)
            self.refrescar_grid()
            messagebox.showinfo("Exito", f"AG-{new_id} agregado correctamente.\nEstado inicial: STOP MANUAL.")

    def demo_falla(self):
        self.controller.provocar_falla_demo()
        messagebox.showwarning("Simulacion", "Se ha forzado una ruptura en AG-1.\nEl sistema debe bloquearse.")

    def _loop_simulacion(self):
        total_kw = self.controller.avanzar_ciclo_simulacion()
        self.lbl_total_potencia.config(text=f"{total_kw:.1f} kW")
        
        for w in self.widgets_ag:
            w.actualizar_datos_ui()
            
        self.after(1000, self._loop_simulacion)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()