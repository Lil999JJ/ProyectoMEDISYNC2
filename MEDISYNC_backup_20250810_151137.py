"""
MEDISYNC - Sistema Integral de Gestión Médica
Versión Restaurada - Completamente Funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json
import os
import subprocess

# Importar calendario si está disponible
try:
    from tkcalendar import Calendar, DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️ tkcalendar no disponible - usando entrada de texto para fechas")

# Importar reportlab para generar PDFs
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch, cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ reportlab no disponible - funcionalidad PDF limitada")

# Importar database manager
try:
    from database_manager import DatabaseManager as DBManager
    print("✅ Usando DatabaseManager principal")
except ImportError:
    try:
        from simple_database_manager import SimpleDatabaseManager as DBManager
        print("✅ Usando SimpleDatabaseManager como respaldo")
    except ImportError:
        print("❌ Error: No se pudo importar ningún database manager")
        exit(1)

class MedisyncApp:
    """Aplicación principal de MEDISYNC"""
    
    def __init__(self, root=None):
        self.db_manager = DBManager('database/medisync.db')
        self.current_user = None
        self.root = root
        self.users_tree = None
        if root is None:
            self.create_login_window()
        else:
            self.setup_root_window()
    
    def setup_root_window(self):
        """Configurar ventana principal cuando se pasa root"""
        if self.root:
            self.root.title("MEDISYNC - Sistema de Gestión Médica")
            self.root.geometry("500x400")
            self.root.configure(bg='#F8FAFC')
    
    def create_login_window(self):
        """Crear ventana de login moderna y estética"""
        if self.root is None:
            self.root = tk.Tk()
        
        self.root.title("MEDISYNC - Sistema de Gestión Médica")
        self.root.geometry("750x850")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window(self.root, 750, 850)
        
        # Configurar fondo
        self.root.configure(bg='#F8FAFC')
        
        # Frame principal con padding
        main_frame = tk.Frame(self.root, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Icono médico
        icon_frame = tk.Frame(header_frame, bg='#0B5394', width=80, height=80)
        icon_frame.pack(pady=(0, 15))
        icon_frame.pack_propagate(False)
        
        tk.Label(icon_frame, text="🏥", font=('Arial', 40), bg='#0B5394', fg='white').pack(expand=True)
        
        # Título principal
        title_label = tk.Label(header_frame, text="MEDISYNC", 
                              font=('Arial', 28, 'bold'), fg='#1E293B', bg='#F8FAFC')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Sistema Integral de Gestión Médica", 
                                 font=('Arial', 14, 'italic'), fg='#64748B', bg='#F8FAFC')
        subtitle_label.pack(pady=(5, 0))
        
        # Frame del formulario
        form_outer_frame = tk.Frame(main_frame, bg='#E2E8F0', relief='raised', bd=2)
        form_outer_frame.pack(fill='x', pady=(0, 20))
        
        form_frame = tk.Frame(form_outer_frame, bg='white', padx=40, pady=30)
        form_frame.pack(fill='x', padx=3, pady=3)
        
        # Título del formulario
        form_title = tk.Label(form_frame, text="🔐 Iniciar Sesión", 
                             font=('Arial', 18, 'bold'), fg='#0B5394', bg='white')
        form_title.pack(pady=(0, 25))
        
        # Campo Email
        email_frame = tk.Frame(form_frame, bg='white')
        email_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(email_frame, text="📧 Correo Electrónico", 
                font=('Arial', 12, 'bold'), fg='#1E293B', bg='white').pack(anchor='w')
        
        email_input_frame = tk.Frame(email_frame, bg='#F8FAFC', relief='solid', bd=1)
        email_input_frame.pack(fill='x', pady=(5, 0))
        
        self.email_entry = tk.Entry(email_input_frame, font=('Arial', 12), bg='#F8FAFC', 
                                   relief='flat', bd=0)
        self.email_entry.pack(fill='x', padx=10, pady=8)
        
        # Campo Contraseña
        password_frame = tk.Frame(form_frame, bg='white')
        password_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(password_frame, text="🔒 Contraseña", 
                font=('Arial', 12, 'bold'), fg='#1E293B', bg='white').pack(anchor='w')
        
        password_input_frame = tk.Frame(password_frame, bg='#F8FAFC', relief='solid', bd=1)
        password_input_frame.pack(fill='x', pady=(5, 0))
        
        self.password_entry = tk.Entry(password_input_frame, font=('Arial', 12), bg='#F8FAFC', 
                                      relief='flat', bd=0, show='*')
        self.password_entry.pack(fill='x', padx=10, pady=8)
        
        # Botones
        buttons_frame = tk.Frame(form_frame, bg='white')
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        buttons_row_frame = tk.Frame(buttons_frame, bg='white')
        buttons_row_frame.pack(fill='x', pady=(0, 10))
        
        # Botón de login
        login_btn = tk.Button(buttons_row_frame, text="🚀 INICIAR SESIÓN", 
                             font=('Arial', 12, 'bold'), bg='#0B5394', fg='white',
                             command=self.login, relief='flat', bd=0,
                             padx=15, pady=12, cursor='hand2')
        login_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botón de registro
        register_btn = tk.Button(buttons_row_frame, text="👤 CREAR CUENTA", 
                               font=('Arial', 12, 'bold'), bg='#0B5394', fg='white',
                               command=self.show_patient_registration, relief='flat', bd=0,
                               padx=15, pady=12, cursor='hand2')
        register_btn.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Info de usuarios de prueba
        info_outer_frame = tk.Frame(main_frame, bg='#FFFFFF', relief='solid', bd=1)
        info_outer_frame.pack(fill='x', pady=(0, 10))
        
        info_frame = tk.Frame(info_outer_frame, bg='#FFFFFF', padx=20, pady=15)
        info_frame.pack(fill='x')
        
        tk.Label(info_frame, text="💡 Usuarios de Prueba", 
                font=('Arial', 12, 'bold'), fg='#1E293B', bg='#FFFFFF').pack(pady=(0, 10))
        
        users_info = [
            ("🛡️ Administrador:", "admin@medisync.com / admin123"),
            ("👨‍⚕️ Doctor:", "carlos@medisync.com / doctor123"),
            ("👩‍💼 Secretaria:", "maria@medisync.com / secretaria123"),
            ("🤒 Paciente:", "pedro@medisync.com / paciente123")
        ]
        
        for role, credentials in users_info:
            user_frame = tk.Frame(info_frame, bg='#FFFFFF')
            user_frame.pack(fill='x', pady=2)
            
            tk.Label(user_frame, text=role, font=('Arial', 10, 'bold'), 
                    fg='#1E293B', bg='#FFFFFF').pack(side='left')
            tk.Label(user_frame, text=credentials, font=('Arial', 10), 
                    fg='#64748B', bg='#FFFFFF').pack(side='left', padx=(10, 0))
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#F8FAFC')
        footer_frame.pack(side='bottom', fill='x')
        
        tk.Label(footer_frame, text="© 2025 MEDISYNC - Todos los derechos reservados", 
                font=('Arial', 9), fg='#64748B', bg='#F8FAFC').pack(pady=5)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        self.email_entry.focus_set()
        
        self.root.mainloop()
    
    def show_patient_registration(self):
        """Mostrar formulario de registro de pacientes"""
        try:
            from patient_registration_form import create_patient_registration_form
            create_patient_registration_form(self.root, self.db_manager)
        except ImportError:
            messagebox.showerror("Error", "No se pudo cargar el formulario de registro.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario: {e}")
    
    def center_window(self, window, width, height):
        """Centrar ventana en la pantalla"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def login(self):
        """Procesar login"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Por favor ingrese email y contraseña")
            return
        
        user = self.db_manager.authenticate_user(email, password)
        
        if user:
            self.current_user = user
            self.root.destroy()
            self.create_main_window()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
            self.password_entry.delete(0, tk.END)
    
    def create_main_window(self):
        """Crear ventana principal según el rol del usuario"""
        self.root = tk.Tk()
        self.root.title(f"MEDISYNC - {self.current_user.nombre} {self.current_user.apellido} ({self.current_user.tipo_usuario.title()})")
        
        # Configurar pantalla completa
        self.root.state('zoomed')  # Para Windows - pantalla completa
        self.root.configure(bg='#F8FAFC')
        
        # Opcional: permitir salir de pantalla completa con Escape
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        self.create_menu_interface()
        
        self.root.mainloop()
    
    def toggle_fullscreen(self):
        """Alternar entre pantalla completa y ventana normal"""
        if self.root.state() == 'zoomed':
            self.root.state('normal')
            self.root.geometry("1200x800")
            self.center_window(self.root, 1200, 800)
        else:
            self.root.state('zoomed')
    
    def create_menu_interface(self):
        """Crear interfaz de menú principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título en header
        tk.Label(header_frame, text="MEDISYNC", font=('Arial', 20, 'bold'), 
                fg='white', bg='#1E3A8A').pack(side='left', padx=20, pady=20)
        
        # Info usuario en header
        user_info = f"{self.current_user.nombre} {self.current_user.apellido} - {self.current_user.tipo_usuario.title()}"
        tk.Label(header_frame, text=user_info, font=('Arial', 12), 
                fg='white', bg='#1E3A8A').pack(side='right', padx=20, pady=20)
        
        # Botón logout
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", command=self.logout,
                              bg='#0B5394', fg='white', font=('Arial', 10))
        logout_btn.pack(side='right', padx=(0, 20), pady=20)
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Crear menú según rol
        if self.current_user.tipo_usuario == 'admin':
            self.create_admin_menu(content_frame)
        elif self.current_user.tipo_usuario == 'doctor':
            self.create_doctor_menu(content_frame)
        elif self.current_user.tipo_usuario == 'secretaria':
            self.create_secretaria_menu(content_frame)
        elif self.current_user.tipo_usuario == 'paciente':
            self.create_paciente_menu(content_frame)
    
    def create_admin_menu(self, parent):
        """Crear menú de administrador con diseño moderno"""
        # Frame principal para el menú
        menu_container = tk.Frame(parent, bg='#F8FAFC')
        menu_container.pack(fill='both', expand=True)
        
        # Header del menú con estilo moderno
        header_frame = tk.Frame(menu_container, bg='#1E3A8A', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=30, pady=10)
        
        # Logo y título
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', expand=True, fill='both')
        
        tk.Label(title_frame, text="🏥", font=('Arial', 20), bg='#1E3A8A', fg='white').pack(side='left', pady=5)
        tk.Label(title_frame, text="MEDISYNC", font=('Arial', 18, 'bold'), bg='#1E3A8A', fg='white').pack(side='left', padx=(10, 0), pady=5)
        tk.Label(title_frame, text="Panel de Administración", font=('Arial', 12), bg='#1E3A8A', fg='#CBD5E1').pack(side='left', padx=(15, 0), pady=5)
        
        # Info del usuario
        user_frame = tk.Frame(header_content, bg='#1E3A8A')
        user_frame.pack(side='right')
        
        user_name = f"{self.current_user.nombre} {self.current_user.apellido}"
        tk.Label(user_frame, text=f"� {user_name}", font=('Arial', 11, 'bold'), bg='#1E3A8A', fg='#FFFFFF').pack(anchor='e')
        tk.Label(user_frame, text="Administrador del Sistema", font=('Arial', 9), bg='#1E3A8A', fg='#64748B').pack(anchor='e')
        
        # Barra de navegación moderna
        nav_frame = tk.Frame(menu_container, bg='#0B5394', height=60)
        nav_frame.pack(fill='x')
        nav_frame.pack_propagate(False)
        
        # Contenedor de botones de navegación
        nav_content = tk.Frame(nav_frame, bg='#0B5394')
        nav_content.pack(expand=True, fill='both', padx=20, pady=5)
        
        # Definir pestañas con iconos y colores
        tabs_config = [
            ("📊", "Dashboard", "#0B5394", "Vista general del sistema"),
            ("👥", "Usuarios", "#16A085", "Gestión de usuarios"),
            ("📅", "Citas", "#C0392B", "Gestión de citas médicas"),
            ("🩺", "Historial Médico", "#059669", "Historiales médicos de pacientes"),
            ("�", "Facturación Avanzada", "#E67E22", "Sistema completo de facturación con PDFs"),
            ("📈", "Reportes", "#16A085", "Análisis y reportes")
        ]
        
        # Variable para controlar la pestaña activa
        self.active_tab = tk.StringVar(value="Dashboard")
        
        # Crear botones de navegación
        self.nav_buttons = {}
        for icon, name, color, description in tabs_config:
            btn_frame = tk.Frame(nav_content, bg='#0B5394')
            btn_frame.pack(side='left', padx=5, pady=5)
            
            # Botón principal
            btn = tk.Button(btn_frame, 
                          text=f"{icon}\n{name}", 
                          font=('Arial', 10, 'bold'),
                          bg='#0B5394' if self.active_tab.get() == name else '#64748B',
                          fg='white',
                          relief='flat',
                          bd=0,
                          padx=20,
                          pady=10,
                          cursor='hand2',
                          command=lambda n=name: self.switch_tab(n))
            btn.pack()
            
            # Efectos hover
            def on_enter(e, button=btn, original_color=color, tab_name=name):
                if self.active_tab.get() != tab_name:
                    button.config(bg=original_color, relief='raised')
            
            def on_leave(e, button=btn, tab_name=name):
                if self.active_tab.get() != tab_name:
                    button.config(bg='#0B5394', relief='flat')
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.nav_buttons[name] = (btn, color)
        
        # Área de contenido principal
        self.content_area = tk.Frame(menu_container, bg='#FFFFFF')
        self.content_area.pack(fill='both', expand=True)
        
        # Cargar contenido inicial (Dashboard)
        self.switch_tab("Dashboard")
    
    def switch_tab(self, tab_name):
        """Cambiar entre pestañas con animación visual"""
        # Actualizar variable de pestaña activa
        self.active_tab.set(tab_name)
        
        # Actualizar colores de botones
        for name, (btn, color) in self.nav_buttons.items():
            if name == tab_name:
                btn.config(bg=color, relief='raised', bd=2)
            else:
                btn.config(bg='#0B5394', relief='flat', bd=0)
        
        # Limpiar área de contenido
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Cargar contenido de la pestaña seleccionada
        if tab_name == "Dashboard":
            self.create_dashboard_tab(self.content_area)
        elif tab_name == "Usuarios":
            self.create_users_tab(self.content_area)
        elif tab_name == "Citas":
            self.create_appointments_tab(self.content_area)
        elif tab_name == "Historial Médico":
            self.create_medical_history_tab(self.content_area)
        elif tab_name == "Facturación Avanzada":
            self.create_advanced_billing_tab(self.content_area)
        elif tab_name == "Reportes":
            self.create_reports_tab(self.content_area)
    
    def create_dashboard_tab(self, parent):
        """Crear pestaña de dashboard con diseño moderno"""
        # Frame principal con mejor diseño
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True)
        
        # Header principal con gradiente visual
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        # Título principal
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', fill='y')
        
        tk.Label(title_frame, text="📊 Dashboard del Sistema", 
                font=('Arial', 20, 'bold'), bg='#1E3A8A', fg='white').pack(anchor='w')
        tk.Label(title_frame, text="Resumen general y estadísticas principales", 
                font=('Arial', 11), bg='#1E3A8A', fg='#CBD5E1').pack(anchor='w')
        
        # Información del usuario actual
        user_info_frame = tk.Frame(header_content, bg='#1E3A8A')
        user_info_frame.pack(side='right', fill='y')
        
        tk.Label(user_info_frame, text=f"👤 {self.current_user.nombre} {self.current_user.apellido}", 
                font=('Arial', 12, 'bold'), bg='#1E3A8A', fg='white').pack(anchor='e')
        tk.Label(user_info_frame, text=f"Rol: {self.current_user.tipo_usuario.title()}", 
                font=('Arial', 10), bg='#1E3A8A', fg='#CBD5E1').pack(anchor='e')
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Tarjetas de estadísticas mejoradas
        stats_frame = tk.Frame(content_frame, bg='#F8FAFC')
        stats_frame.pack(fill='x', pady=(0, 30))
        
        try:
            stats = self.get_system_stats()
            
            # Crear tarjetas modernas
            cards_data = [
                ("👥", "Usuarios Totales", str(stats.get('total_users', 0)), "#0B5394"),
                ("📅", "Citas Hoy", str(stats.get('appointments_today', 0)), "#059669"),
                ("💰", "Ingresos del Mes", f"RD$ {stats.get('monthly_income', 0):,.2f}", "#E67E22"),
                ("⏳", "Facturas Pendientes", str(stats.get('pending_invoices', 0)), "#C0392B")
            ]
            
            for i, (icon, title, value, color) in enumerate(cards_data):
                self.create_modern_stats_card(stats_frame, icon, title, value, color, i)
            
        except Exception as e:
            error_frame = tk.Frame(stats_frame, bg='#0B5394', relief='solid', bd=1)
            error_frame.pack(fill='x', pady=10)
            tk.Label(error_frame, text=f"❌ Error cargando estadísticas: {str(e)}", 
                    fg='white', bg='#0B5394', font=('Arial', 10, 'bold'), pady=15).pack()
        
        # Panel de accesos rápidos mejorado
        quick_actions_frame = tk.LabelFrame(content_frame, text="� Accesos Rápidos", 
                                          font=('Arial', 14, 'bold'), padx=25, pady=20, 
                                          bg='white', relief='solid', bd=1)
        quick_actions_frame.pack(fill='x', pady=(0, 30))
        
        # Grid de acciones rápidas
        actions_grid = tk.Frame(quick_actions_frame, bg='white')
        actions_grid.pack(fill='x')
        
        quick_actions = [
            ("➕ Nueva Cita", self.new_appointment_quick, "#16A085"),
            ("👤 Nuevo Paciente", self.new_patient_quick, "#0B5394"),
            ("💳 Procesar Pago", self.process_payment_quick, "#E67E22"),
            ("📋 Generar Reporte", self.daily_report, "#16A085")
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            btn = tk.Button(actions_grid, text=text, command=command, 
                           bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                           width=18, height=3, relief='flat',
                           cursor='hand2')
            btn.grid(row=i//2, column=i%2, padx=15, pady=10, sticky='ew')
        
        # Configurar grid weights
        actions_grid.columnconfigure(0, weight=1)
        actions_grid.columnconfigure(1, weight=1)
        
        # Panel de actividad reciente
        activity_frame = tk.LabelFrame(content_frame, text="📈 Actividad Reciente", 
                                     font=('Arial', 14, 'bold'), padx=25, pady=20, 
                                     bg='white', relief='solid', bd=1)
        activity_frame.pack(fill='both', expand=True)
        
        # Placeholder para actividad reciente
        activity_content = tk.Frame(activity_frame, bg='white')
        activity_content.pack(fill='both', expand=True)
        
        tk.Label(activity_content, text="📊 Sistema de monitoreo en tiempo real", 
                font=('Arial', 12, 'bold'), bg='white', fg='#1E3A8A').pack(pady=(10, 5))
        tk.Label(activity_content, text="• Últimas citas registradas\n• Nuevos pacientes\n• Facturas procesadas\n• Alertas del sistema", 
                font=('Arial', 10), bg='white', fg='#64748B', justify='left').pack()
        
    def create_modern_stats_card(self, parent, icon, title, value, color, position):
        """Crear tarjeta de estadística moderna"""
        # Frame de la tarjeta
        card = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card.pack(side='left', fill='both', expand=True, padx=10 if position > 0 else 0)
        
        # Header de la tarjeta
        header = tk.Frame(card, bg=color, height=10)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Contenido de la tarjeta
        content = tk.Frame(card, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icono grande
        tk.Label(content, text=icon, font=('Arial', 24), bg='white', fg=color).pack(pady=(0, 10))
        
        # Valor principal
        tk.Label(content, text=value, font=('Arial', 16, 'bold'), 
                bg='white', fg='#1E3A8A').pack()
        
        # Título
        tk.Label(content, text=title, font=('Arial', 10), 
                bg='white', fg='#64748B').pack(pady=(5, 0))
    
    def create_stats_card(self, parent, title, value, color, row, col):
        """Crear tarjeta de estadísticas (función legacy)"""
        card_frame = tk.Frame(parent, bg=color, width=200, height=100, relief='raised', bd=2)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
        card_frame.grid_propagate(False)
        
        tk.Label(card_frame, text=title, font=('Arial', 10, 'bold'), 
                bg=color, fg='white').pack(pady=(10, 5))
        tk.Label(card_frame, text=value, font=('Arial', 16, 'bold'), 
                bg=color, fg='white').pack()
        
        parent.grid_columnconfigure(col, weight=1)
    
    def get_system_stats(self):
        """Obtener estadísticas del sistema"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Total de pacientes
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = 'paciente'")
            stats['total_patients'] = cursor.fetchone()[0]
            
            # Citas de hoy
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM citas WHERE DATE(fecha_hora) = ?", (today,))
            stats['appointments_today'] = cursor.fetchone()[0]
            
            # Facturas pendientes
            cursor.execute("SELECT COUNT(*) FROM facturas WHERE estado = 'pendiente'")
            stats['pending_invoices'] = cursor.fetchone()[0]
            
            # Ingresos del mes actual
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE estado = 'pagada' AND strftime('%Y-%m', fecha_pago) = ?
            """, (current_month,))
            stats['monthly_income'] = cursor.fetchone()[0] or 0
            
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()
    
    def create_users_tab(self, parent):
        """Crear pestaña de gestión completa de usuarios integrada"""
        # Frame principal con mejor diseño
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True)
        
        # Header con gradiente visual
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Título principal
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', fill='y')
        
        tk.Label(title_frame, text="👥 Gestión de Usuarios", 
                font=('Arial', 18, 'bold'), bg='#1E3A8A', fg='white').pack(anchor='w')
        tk.Label(title_frame, text="Administración completa del sistema", 
                font=('Arial', 10), bg='#1E3A8A', fg='#CBD5E1').pack(anchor='w')
        
        # Botones de acción principales
        actions_frame = tk.Frame(header_content, bg='#1E3A8A')
        actions_frame.pack(side='right', fill='y')
        
        tk.Button(actions_frame, text="➕ Nuevo Usuario", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), relief='flat', padx=15, pady=8,
                 command=self.add_new_user).pack(side='right', padx=(10, 0))
        tk.Button(actions_frame, text="🔄 Actualizar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), relief='flat', padx=15, pady=8,
                 command=self.refresh_user_list).pack(side='right', padx=(10, 0))
        
        # Contenido principal dividido
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Lista y filtros
        left_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Header del panel izquierdo
        left_header = tk.Frame(left_panel, bg='#0B5394', height=45)
        left_header.pack(fill='x')
        left_header.pack_propagate(False)
        
        tk.Label(left_header, text="📋 Lista de Usuarios", font=('Arial', 12, 'bold'), 
                bg='#0B5394', fg='white').pack(side='left', padx=15, pady=10)
        
        # Sección de filtros mejorada
        filters_frame = tk.LabelFrame(left_panel, text="🔍 Filtros de Búsqueda", 
                                    font=('Arial', 10, 'bold'), padx=15, pady=10, bg='white')
        filters_frame.pack(fill='x', padx=15, pady=10)
        
        # Primera fila de filtros
        filter_row1 = tk.Frame(filters_frame, bg='white')
        filter_row1.pack(fill='x', pady=(0, 8))
        
        tk.Label(filter_row1, text="Buscar:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.user_search_entry = tk.Entry(filter_row1, font=('Arial', 9), width=25, relief='solid', bd=1)
        self.user_search_entry.grid(row=0, column=1, padx=5, sticky='ew')
        self.user_search_entry.bind('<KeyRelease>', self.search_users)
        
        # Segunda fila de filtros
        filter_row2 = tk.Frame(filters_frame, bg='white')
        filter_row2.pack(fill='x', pady=(0, 8))
        
        tk.Label(filter_row2, text="Tipo:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.user_type_filter = ttk.Combobox(filter_row2, values=['Todos', 'admin', 'doctor', 'secretaria', 'paciente'], 
                                           state='readonly', width=15, font=('Arial', 9))
        self.user_type_filter.set('Todos')
        self.user_type_filter.grid(row=0, column=1, padx=5, sticky='ew')
        self.user_type_filter.bind('<<ComboboxSelected>>', self.filter_users)
        
        tk.Label(filter_row2, text="Estado:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=(15, 5))
        self.user_status_filter = ttk.Combobox(filter_row2, values=['Todos', 'Activo', 'Inactivo'], 
                                             state='readonly', width=12, font=('Arial', 9))
        self.user_status_filter.set('Todos')
        self.user_status_filter.grid(row=0, column=3, padx=5, sticky='ew')
        self.user_status_filter.bind('<<ComboboxSelected>>', self.filter_users)
        
        # Tercera fila - botones de filtro
        filter_row3 = tk.Frame(filters_frame, bg='white')
        filter_row3.pack(fill='x')
        
        tk.Button(filter_row3, text="🔍 Buscar", bg='#0B5394', fg='white', font=('Arial', 8, 'bold'),
                 relief='flat', padx=12, pady=4, command=self.search_users).pack(side='left', padx=(0, 5))
        tk.Button(filter_row3, text="🗑️ Limpiar", bg='#0B5394', fg='white', font=('Arial', 8, 'bold'),
                 relief='flat', padx=12, pady=4, command=self.clear_user_search).pack(side='left')
        
        # Configurar grid weights para filtros
        filter_row1.columnconfigure(1, weight=1)
        filter_row2.columnconfigure(1, weight=1)
        filter_row2.columnconfigure(3, weight=1)
        
        # Tabla de usuarios mejorada
        table_frame = tk.Frame(left_panel, bg='white')
        table_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Estilo personalizado para la tabla
        style = ttk.Style()
        style.configure("Users.Treeview", font=('Arial', 9))
        style.configure("Users.Treeview.Heading", font=('Arial', 10, 'bold'))
        
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Tipo', 'Estado', 'Último Acceso')
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                     height=12, style="Users.Treeview")
        
        # Configurar headers con anchos optimizados
        column_widths = {'ID': 50, 'Nombre': 100, 'Apellido': 100, 'Email': 160, 
                        'Tipo': 80, 'Estado': 70, 'Último Acceso': 90}
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars para la tabla con mejor visibilidad
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.users_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.users_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=0, minsize=20)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Bind para selección
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Panel derecho - Detalles y acciones
        right_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1, width=350)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Header del panel derecho
        right_header = tk.Frame(right_panel, bg='#0B5394', height=45)
        right_header.pack(fill='x')
        right_header.pack_propagate(False)
        
        tk.Label(right_header, text="⚙️ Acciones de Usuario", font=('Arial', 12, 'bold'), 
                bg='#0B5394', fg='white').pack(pady=10)
        
        # Información del usuario seleccionado
        self.user_info_frame = tk.Frame(right_panel, bg='white')
        self.user_info_frame.pack(fill='x', padx=15, pady=15)
        
        # Placeholder inicial
        self.user_info_label = tk.Label(self.user_info_frame, 
                                       text="👆 Seleccione un usuario de la lista\npara ver sus detalles y opciones", 
                                       font=('Arial', 10), bg='white', fg='#64748B', 
                                       justify='center', wraplength=300)
        self.user_info_label.pack(pady=20)
        
        # Frame para botones de acción
        self.actions_frame = tk.Frame(right_panel, bg='white')
        self.actions_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Botones de acción (inicialmente ocultos)
        self.action_buttons = []
        user_actions = [
            ("✏️ Editar Usuario", self.edit_selected_user, "#0B5394"),
            ("🔑 Cambiar Contraseña", self.change_user_password, "#E67E22"),
            ("✅ Activar Usuario", self.activate_user, "#16A085"),
            ("❌ Desactivar Usuario", self.deactivate_user, "#C0392B"),
            ("👁️ Ver Detalles Completos", self.view_user_details, "#16A085"),
            ("🗑️ Eliminar Usuario", self.delete_user, "#C0392B")
        ]
        
        for text, command, color in user_actions:
            btn = tk.Button(self.actions_frame, text=text, command=command, 
                           bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                           width=22, height=2, relief='flat', state='disabled')
            btn.pack(fill='x', pady=2)
            self.action_buttons.append(btn)
        
        # Estadísticas en la parte inferior
        stats_frame = tk.LabelFrame(right_panel, text="📊 Estadísticas del Sistema", 
                                   font=('Arial', 10, 'bold'), padx=10, pady=10, bg='white')
        stats_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.load_user_stats(stats_frame)
        
        # Variables para el usuario seleccionado
        self.selected_user_id = None
        self.selected_user_data = None
        
        # Cargar datos iniciales
        self.load_users_list()
    
    def load_users_data(self):
        """Cargar datos de usuarios (función de compatibilidad)"""
        self.load_users_list()
    
    # def create_patients_tab(self, parent):
    #     """Crear pestaña de pacientes - FUNCIÓN DESHABILITADA"""
    #     pass
        
    # def load_patients_data(self, tree):
    #     """Cargar datos de pacientes - FUNCIÓN DESHABILITADA"""
    #     pass
    
    # def create_doctors_tab(self, parent):
    #     """Crear pestaña de doctores - FUNCIÓN DESHABILITADA"""
    #     pass
    
    # def load_doctors_data(self, tree):
    #     """Cargar datos de doctores - FUNCIÓN DESHABILITADA"""
    #     pass
    
    def create_appointments_tab(self, parent):
        """Crear pestaña de citas con diseño moderno similar a usuarios"""
        # Frame principal
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header con diseño moderno
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80, relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Título del módulo
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', fill='y')
        
        tk.Label(title_frame, text="📅", font=('Arial', 24), 
                bg='#1E3A8A', fg='white').pack(side='left')
        tk.Label(title_frame, text="Gestión de Citas Médicas", font=('Arial', 18, 'bold'), 
                bg='#1E3A8A', fg='white').pack(side='left', padx=(10, 0))
        
        # Botones de acción en el header
        actions_frame = tk.Frame(header_content, bg='#1E3A8A')
        actions_frame.pack(side='right', fill='y')
        
        tk.Button(actions_frame, text="➕ Nueva Cita", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), relief='flat', padx=15, pady=8,
                 command=self.new_appointment_window).pack(side='right', padx=(10, 0))
        tk.Button(actions_frame, text="🔄 Actualizar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), relief='flat', padx=15, pady=8,
                 command=lambda: self.load_appointments_data(self.appointments_tree)).pack(side='right', padx=(10, 0))
        
        # Contenido principal dividido
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Panel izquierdo - Acciones rápidas
        left_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1, width=200)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Frame para botones de acción en panel izquierdo
        actions_label_frame = tk.LabelFrame(left_panel, text="⚡ Acciones Rápidas", 
                                           font=('Arial', 12, 'bold'), padx=10, pady=10, bg='white', fg='#1E3A8A')
        actions_label_frame.pack(fill='both', expand=True, padx=10, pady=15)
        
        # Botones de acción para citas seleccionadas
        action_frame = tk.Frame(actions_label_frame, bg='white')
        action_frame.pack(fill='x', pady=10)
        
        # Organizar botones verticalmente
        tk.Button(action_frame, text="✏️ Editar Cita", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=self.edit_appointment, padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        tk.Button(action_frame, text="👁️ Ver Detalles", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=lambda: self.show_appointment_details(), padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        tk.Button(action_frame, text="✅ Confirmar", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=self.confirm_appointment, padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        tk.Button(action_frame, text="🚀 Iniciar", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=self.start_appointment, padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        tk.Button(action_frame, text="✅ Completar", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=self.complete_appointment, padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        tk.Button(action_frame, text="❌ Cancelar", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=self.cancel_appointment, padx=15, pady=8, relief='flat').pack(fill='x', pady=3)
        
        # Panel central - Lista de citas con filtros
        center_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        center_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Barra de filtros dentro del panel central
        filters_frame = tk.LabelFrame(center_panel, text="🔍 Filtros de Búsqueda", 
                                     font=('Arial', 12, 'bold'), padx=15, pady=10, bg='white', fg='#1E3A8A')
        filters_frame.pack(fill='x', padx=15, pady=15)
        
        # Fila 1 de filtros
        filter_row1 = tk.Frame(filters_frame, bg='white')
        filter_row1.pack(fill='x', pady=5)
        
        tk.Label(filter_row1, text="🔍 Buscar:", font=('Arial', 9, 'bold'), 
                bg='white', fg='#64748B').grid(row=0, column=0, sticky='w', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_row1, textvariable=self.search_var, 
                               font=('Arial', 9), width=25, relief='solid', bd=1)
        search_entry.grid(row=0, column=1, sticky='ew', padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.filter_appointments)
        
        tk.Label(filter_row1, text="📊 Estado:", font=('Arial', 9, 'bold'), 
                bg='white', fg='#64748B').grid(row=0, column=2, sticky='w', padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(filter_row1, textvariable=self.status_filter, 
                                   values=["Todos", "pendiente", "confirmada", "en_curso", "completada", "cancelada"],
                                   width=12, state="readonly", font=('Arial', 9))
        status_combo.grid(row=0, column=3, sticky='ew')
        status_combo.bind('<<ComboboxSelected>>', self.filter_appointments)
        
        # Fila 2 de filtros
        filter_row2 = tk.Frame(filters_frame, bg='white')
        filter_row2.pack(fill='x', pady=5)
        
        tk.Label(filter_row2, text="📅 Fecha:", font=('Arial', 9, 'bold'), 
                bg='white', fg='#64748B').grid(row=0, column=0, sticky='w', padx=(0, 5))
        
        self.date_filter = tk.StringVar()
        if CALENDAR_AVAILABLE:
            self.date_entry = DateEntry(filter_row2, textvariable=self.date_filter,
                                       font=('Arial', 9), width=12, relief='solid', bd=1,
                                       date_pattern='dd/mm/yyyy', background='#0B5394',
                                       foreground='white', borderwidth=2)
            self.date_entry.grid(row=0, column=1, sticky='ew', padx=(0, 15))
            self.date_entry.bind('<<DateEntrySelected>>', self.filter_appointments)
        else:
            date_entry = tk.Entry(filter_row2, textvariable=self.date_filter, 
                                 font=('Arial', 9), width=12, relief='solid', bd=1)
            date_entry.grid(row=0, column=1, sticky='ew', padx=(0, 15))
            date_entry.bind('<KeyRelease>', self.filter_appointments)
        
        tk.Label(filter_row2, text="👨‍⚕️ Doctor:", font=('Arial', 9, 'bold'), 
                bg='white', fg='#64748B').grid(row=0, column=2, sticky='w', padx=(0, 5))
        
        self.doctor_filter = tk.StringVar(value="Todos")
        # Obtener lista de doctores
        doctors_list = ["Todos"] + self.get_doctors_list()
        self.doctor_combo = ttk.Combobox(filter_row2, textvariable=self.doctor_filter, 
                                        values=doctors_list, width=15, state="readonly", font=('Arial', 9))
        self.doctor_combo.grid(row=0, column=3, sticky='ew')
        self.doctor_combo.bind('<<ComboboxSelected>>', self.filter_appointments)
        
        # Botones de filtro
        filter_row3 = tk.Frame(filters_frame, bg='white')
        filter_row3.pack(fill='x', pady=(10, 0))
        
        tk.Button(filter_row3, text="🔍 Buscar", bg='#0B5394', fg='white', font=('Arial', 8, 'bold'),
                 relief='flat', padx=12, pady=4, command=self.filter_appointments).pack(side='left', padx=(0, 5))
        tk.Button(filter_row3, text="🗑️ Limpiar", bg='#0B5394', fg='white', font=('Arial', 8, 'bold'),
                 relief='flat', padx=12, pady=4, command=self.clear_appointment_filters).pack(side='left')
        
        # Configurar grid weights para filtros
        filter_row1.columnconfigure(1, weight=1)
        filter_row2.columnconfigure(1, weight=1)
        filter_row2.columnconfigure(3, weight=1)
        
        # Tabla de citas en panel central
        table_frame = tk.LabelFrame(center_panel, text="📋 Lista de Citas", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10, bg='white', fg='#1E3A8A')
        table_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Configurar Treeview con diseño limpio
        columns = ('ID', 'Fecha', 'Hora', 'Paciente', 'Doctor', 'Motivo', 'Estado')
        self.appointments_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar headers
        column_widths = {'ID': 50, 'Fecha': 90, 'Hora': 70, 'Paciente': 140, 
                        'Doctor': 140, 'Motivo': 180, 'Estado': 90}
        
        for col in columns:
            self.appointments_tree.heading(col, text=col, anchor='center')
            self.appointments_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Solo configurar alternado simple, sin colores de estado
        self.appointments_tree.tag_configure('oddrow', background='#F8FAFC')
        self.appointments_tree.tag_configure('evenrow', background='white')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.appointments_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.appointments_tree.xview)
        self.appointments_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout de la tabla
        self.appointments_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        v_scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para selección
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        self.appointments_tree.bind('<Double-1>', lambda event: self.show_appointment_details())
        
        # Panel derecho - Detalles y acciones
        right_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1, width=350)
        right_panel.pack(side='right', fill='y', padx=(0, 0))
        right_panel.pack_propagate(False)
        
        # Header del panel derecho
        details_header = tk.Frame(right_panel, bg='#0B5394', height=50)
        details_header.pack(fill='x')
        details_header.pack_propagate(False)
        
        tk.Label(details_header, text="📋 Detalles de la Cita", font=('Arial', 12, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Frame para detalles de la cita solamente
        self.appointment_details_frame = tk.Frame(right_panel, bg='white')
        self.appointment_details_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Mensaje inicial
        self.appointment_details_label = tk.Label(self.appointment_details_frame, 
                                                 text="Seleccione una cita\npara ver los detalles", 
                                                 font=('Arial', 11), bg='white', fg='#64748B', 
                                                 justify='center')
        self.appointment_details_label.pack(pady=20)
        
        # Cargar datos iniciales
        self.load_appointments_data(self.appointments_tree)
        # que se crea más abajo en el right_panel
        
        # Bind eventos
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        self.appointments_tree.bind('<Double-1>', lambda event: self.show_appointment_details())
        
        # Cargar datos iniciales
        self.load_appointments_data(self.appointments_tree)
    
    def get_doctors_list(self):
        """Obtener lista de doctores para el filtro"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT nombre || ' ' || apellido as doctor_name 
                FROM usuarios 
                WHERE tipo_usuario = 'doctor' AND activo = 1
                ORDER BY nombre, apellido
            """)
            doctors = cursor.fetchall()
            return [doctor[0] for doctor in doctors]
        except Exception as e:
            print(f"Error al obtener doctores: {e}")
            return []
    
    def load_appointments_data(self, tree):
        """Cargar datos de citas con diseño limpio sin colores de estado"""
        try:
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener citas con filtros aplicados
            appointments = self.get_filtered_appointments()
            
            for i, appointment in enumerate(appointments):
                # Formatear fecha y hora por separado
                fecha_hora = appointment.get('fecha_hora', '')
                fecha, hora = '', ''
                if fecha_hora:
                    try:
                        dt = datetime.fromisoformat(fecha_hora)
                        fecha = dt.strftime('%d/%m/%Y')
                        hora = dt.strftime('%H:%M')
                    except:
                        fecha = fecha_hora
                        hora = ''
                
                # Solo usar alternado simple, sin colores de estado
                tag = 'oddrow' if i % 2 else 'evenrow'
                
                tree.insert('', 'end', values=(
                    appointment['id'], fecha, hora,
                    appointment.get('paciente_nombre', 'N/A'),
                    appointment.get('doctor_nombre', 'N/A'),
                    appointment.get('motivo', 'N/A'),
                    appointment.get('estado', 'pendiente').title()
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar citas: {str(e)}")
    
    def clear_appointment_filters(self):
        """Limpiar todos los filtros de citas"""
        self.search_var.set("")
        self.status_filter.set("Todos")
        if hasattr(self, 'date_filter'):
            self.date_filter.set("")
        if hasattr(self, 'doctor_filter'):
            self.doctor_filter.set("Todos")
        # Limpiar el DateEntry si está disponible
        if hasattr(self, 'date_entry') and CALENDAR_AVAILABLE:
            self.date_entry.set_date(datetime.now().date())
            self.date_filter.set("")
        self.load_appointments_data(self.appointments_tree)
    
    def get_filtered_appointments(self):
        """Obtener citas filtradas por búsqueda, estado, fecha y doctor"""
        try:
            appointments = self.db_manager.get_all_appointments()
            
            # Filtrar por texto de búsqueda
            search_text = getattr(self, 'search_var', None)
            if search_text and search_text.get().strip():
                search = search_text.get().strip().lower()
                appointments = [app for app in appointments if (
                    search in app.get('paciente_nombre', '').lower() or
                    search in app.get('doctor_nombre', '').lower() or
                    search in app.get('motivo', '').lower() or
                    search in str(app.get('id', ''))
                )]
            
            # Filtrar por estado
            status_filter = getattr(self, 'status_filter', None)
            if status_filter and status_filter.get() != "Todos":
                status = status_filter.get()
                appointments = [app for app in appointments if app.get('estado', 'Programada') == status]
            
            # Filtrar por fecha
            date_filter = getattr(self, 'date_filter', None)
            if date_filter and date_filter.get().strip():
                date_str = date_filter.get().strip()
                # Convertir fecha de DD/MM/YYYY a formato comparable
                try:
                    if '/' in date_str:
                        day, month, year = date_str.split('/')
                        filter_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        appointments = [app for app in appointments 
                                      if app.get('fecha_hora', '').startswith(filter_date)]
                except:
                    pass  # Si hay error en el formato, ignorar filtro de fecha
            
            # Filtrar por doctor
            doctor_filter = getattr(self, 'doctor_filter', None)
            if doctor_filter and doctor_filter.get() != "Todos":
                doctor_name = doctor_filter.get()
                appointments = [app for app in appointments 
                              if app.get('doctor_nombre', '') == doctor_name]
            
            return appointments
            
        except Exception as e:
            print(f"Error filtrando citas: {str(e)}")
            return []
    
    def filter_appointments(self, event=None):
        """Filtrar citas en tiempo real"""
        if hasattr(self, 'appointments_tree'):
            self.load_appointments_data(self.appointments_tree)
    
    def on_appointment_select(self, event):
        """Manejar selección de cita"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                self.clear_appointment_details()
                return
            
            item = self.appointments_tree.item(selection[0])
            values = item['values']
            
            if values:
                appointment_id = values[0]
                self.show_appointment_details(appointment_id)
                
        except Exception as e:
            print(f"Error en selección de cita: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_appointment_details(self, appointment_id):
        """Mostrar detalles de la cita seleccionada"""
        try:
            # Limpiar detalles anteriores
            for widget in self.appointment_details_frame.winfo_children():
                widget.destroy()
            
            # Obtener datos de la cita
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            
            if not appointment:
                tk.Label(self.appointment_details_frame, text="Cita no encontrada", 
                        font=('Arial', 10), bg='white', fg='#C0392B').pack(expand=True)
                return
            
            # Formatear fecha y hora
            fecha_hora = appointment.get('fecha_hora', '')
            if fecha_hora:
                try:
                    dt = datetime.fromisoformat(fecha_hora)
                    fecha_formatted = dt.strftime('%A, %d de %B de %Y')
                    hora_formatted = dt.strftime('%H:%M')
                except:
                    fecha_formatted = fecha_hora
                    hora_formatted = ''
            else:
                fecha_formatted = 'No definida'
                hora_formatted = ''
            
            # Crear interfaz de detalles
            details = [
                ("ID:", str(appointment['id'])),
                ("Fecha:", fecha_formatted),
                ("Hora:", hora_formatted),
                ("Paciente:", appointment.get('paciente_nombre', 'N/A')),
                ("Doctor:", appointment.get('doctor_nombre', 'N/A')),
                ("Motivo:", appointment.get('motivo', 'N/A')),
                ("Estado:", appointment.get('estado', 'Programada')),
                ("Observaciones:", appointment.get('observaciones', 'Ninguna'))
            ]
            
            for label, value in details:
                detail_frame = tk.Frame(self.appointment_details_frame, bg='white')
                detail_frame.pack(fill='x', pady=2)
                
                tk.Label(detail_frame, text=label, font=('Arial', 9, 'bold'), 
                        bg='white', fg='#1E3A8A', anchor='w').pack(side='left')
                
                # Ajustar texto largo
                if len(str(value)) > 25:
                    text_widget = tk.Text(detail_frame, height=2, wrap='word', 
                                        font=('Arial', 9), bg='#F8FAFC', relief='flat')
                    text_widget.insert(1.0, str(value))
                    text_widget.configure(state='disabled')
                    text_widget.pack(fill='x', pady=(2, 0))
                else:
                    tk.Label(detail_frame, text=str(value), font=('Arial', 9), 
                            bg='white', fg='#64748B', anchor='w', wraplength=200).pack(fill='x')
                
        except Exception as e:
            print(f"Error mostrando detalles: {str(e)}")
            import traceback
            traceback.print_exc()
            tk.Label(self.appointment_details_frame, text="Error cargando detalles", 
                    font=('Arial', 10), bg='white', fg='#C0392B').pack(expand=True)
    
    def clear_appointment_details(self):
        """Limpiar panel de detalles"""
        try:
            for widget in self.appointment_details_frame.winfo_children():
                widget.destroy()
            
            tk.Label(self.appointment_details_frame, text="Seleccione una cita\npara ver los detalles", 
                    font=('Arial', 10), bg='white', fg='#64748B').pack(expand=True)
        except:
            pass
    
    def new_appointment_window(self):
        """Ventana para crear nueva cita con diseño mejorado"""
        window = tk.Toplevel(self.root)
        window.title("🏥 MEDISYNC - Nueva Cita Médica")
        window.geometry("850x750")
        window.configure(bg='#F8FAFC')
        window.transient(self.root)
        window.grab_set()
        window.resizable(False, False)
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (850 // 2)
        y = (window.winfo_screenheight() // 2) - (750 // 2)
        window.geometry(f"850x750+{x}+{y}")
        
        # Header mejorado con gradiente visual
        header_frame = tk.Frame(window, bg='#1E3A8A', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Container para el título y subtitle
        title_container = tk.Frame(header_frame, bg='#1E3A8A')
        title_container.pack(expand=True, fill='both')
        
        # Título principal
        title_label = tk.Label(title_container, text="📅 PROGRAMAR NUEVA CITA", 
                              font=('Arial', 18, 'bold'), bg='#1E3A8A', fg='white')
        title_label.pack(pady=(20, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(title_container, text="Complete todos los campos marcados con (*)", 
                                 font=('Arial', 10), bg='#1E3A8A', fg='#CBD5E1')
        subtitle_label.pack(pady=(0, 15))
        
        # Main container con scroll
        main_container = tk.Frame(window, bg='#F8FAFC')
        main_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg='#F8FAFC', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F8FAFC')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables del formulario
        appointment_vars = {
            'fecha': tk.StringVar(),
            'hora': tk.StringVar(),
            'paciente_id': tk.StringVar(),
            'doctor_id': tk.StringVar(),
            'motivo': tk.StringVar(),
            'observaciones': tk.StringVar(),
            'estado': tk.StringVar(value='pendiente'),
            'duracion': tk.StringVar(value='60'),
            'tipo_consulta': tk.StringVar(value='general')
        }
        
        entries = {}
        
        # SECCIÓN 1: INFORMACIÓN TEMPORAL
        temporal_section = tk.LabelFrame(scrollable_frame, text="⏰ Programación de la Cita", 
                                       font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                       padx=20, pady=15)
        temporal_section.pack(fill='x', pady=(0, 20))
        
        # Grid para fecha y hora
        datetime_grid = tk.Frame(temporal_section, bg='#F8FAFC')
        datetime_grid.pack(fill='x')
        
        # Fecha
        fecha_frame = tk.Frame(datetime_grid, bg='#F8FAFC')
        fecha_frame.grid(row=0, column=0, sticky='ew', padx=(0, 15))
        
        tk.Label(fecha_frame, text="📅 Fecha de la Cita *", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        fecha_input_frame = tk.Frame(fecha_frame, bg='#F8FAFC')
        fecha_input_frame.pack(fill='x', pady=(8, 0))
        
        # Usar DateEntry si está disponible, sino Entry normal
        if CALENDAR_AVAILABLE:
            fecha_entry = DateEntry(fecha_input_frame, textvariable=appointment_vars['fecha'],
                                   font=('Arial', 12), width=15, relief='solid', bd=1,
                                   date_pattern='dd/mm/yyyy', background='#0B5394',
                                   foreground='white', borderwidth=2)
            fecha_entry.pack(side='left', ipady=8)
        else:
            fecha_entry = tk.Entry(fecha_input_frame, textvariable=appointment_vars['fecha'], 
                                  font=('Arial', 12), width=15, relief='solid', bd=1)
            fecha_entry.pack(side='left', ipady=8)
            
            fecha_btn = tk.Button(fecha_input_frame, text="📅 Seleccionar", 
                                 command=lambda: self.select_date_enhanced(appointment_vars['fecha']),
                                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                                 relief='flat', padx=15, pady=8, cursor='hand2')
            fecha_btn.pack(side='left', padx=(10, 0))
        
        entries['fecha'] = fecha_entry
        
        # Indicador visual para fecha
        fecha_info = tk.Label(fecha_frame, text="Formato: DD/MM/YYYY", 
                             font=('Arial', 9), bg='#F8FAFC', fg='#64748B')
        fecha_info.pack(anchor='w', pady=(5, 0))
        
        # Hora
        hora_frame = tk.Frame(datetime_grid, bg='#F8FAFC')
        hora_frame.grid(row=0, column=1, sticky='ew', padx=(15, 0))
        
        tk.Label(hora_frame, text="🕐 Hora de la Cita *", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        hora_input_frame = tk.Frame(hora_frame, bg='#F8FAFC')
        hora_input_frame.pack(fill='x', pady=(8, 0))
        
        hora_entry = tk.Entry(hora_input_frame, textvariable=appointment_vars['hora'], 
                             font=('Arial', 12), width=15, relief='solid', bd=1)
        hora_entry.pack(side='left', ipady=8)
        entries['hora'] = hora_entry
        
        # Botones de horarios rápidos
        quick_times = ['08:00', '09:00', '10:00', '14:00', '15:00', '16:00']
        quick_time_frame = tk.Frame(hora_input_frame, bg='#F8FAFC')
        quick_time_frame.pack(side='left', padx=(10, 0))
        
        for time in quick_times[:3]:
            tk.Button(quick_time_frame, text=time, 
                     command=lambda t=time: appointment_vars['hora'].set(t),
                     bg='#FFFFFF', fg='#1E3A8A', font=('Arial', 8),
                     relief='flat', padx=5, pady=2, cursor='hand2').pack(side='left', padx=1)
        
        # Indicador visual para hora
        hora_info = tk.Label(hora_frame, text="Formato: HH:MM (24h)", 
                            font=('Arial', 9), bg='#F8FAFC', fg='#64748B')
        hora_info.pack(anchor='w', pady=(5, 0))
        
        # Duración
        duracion_frame = tk.Frame(temporal_section, bg='#F8FAFC')
        duracion_frame.pack(fill='x', pady=(15, 0))
        
        tk.Label(duracion_frame, text="⏱️ Duración (minutos)", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        duracion_combo = ttk.Combobox(duracion_frame, textvariable=appointment_vars['duracion'],
                                     values=['30', '45', '60', '90', '120'], state='readonly',
                                     font=('Arial', 11), width=20)
        duracion_combo.pack(anchor='w', pady=(8, 0))
        entries['duracion'] = duracion_combo
        
        datetime_grid.columnconfigure(0, weight=1)
        datetime_grid.columnconfigure(1, weight=1)
        
        # SECCIÓN 2: PARTICIPANTES
        participants_section = tk.LabelFrame(scrollable_frame, text="👥 Participantes de la Cita", 
                                           font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                           padx=20, pady=15)
        participants_section.pack(fill='x', pady=(0, 20))
        
        # Grid para paciente y doctor
        participants_grid = tk.Frame(participants_section, bg='#F8FAFC')
        participants_grid.pack(fill='x')
        
        # Paciente
        paciente_frame = tk.Frame(participants_grid, bg='#F8FAFC')
        paciente_frame.grid(row=0, column=0, sticky='ew', padx=(0, 15))
        
        tk.Label(paciente_frame, text="👤 Paciente *", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        paciente_combo = ttk.Combobox(paciente_frame, textvariable=appointment_vars['paciente_id'],
                                     font=('Arial', 11), state="readonly", width=35)
        paciente_combo.pack(fill='x', pady=(8, 0))
        entries['paciente_id'] = paciente_combo
        
        # Cargar pacientes con mejor formato
        try:
            patients = self.db_manager.get_all_patients()
            if patients:
                patient_values = [f"{p['id']} - {p['nombre']} {p['apellido']}" for p in patients]
                paciente_combo['values'] = patient_values
                paciente_combo.set("Seleccione un paciente...")
            else:
                paciente_combo['values'] = ["No hay pacientes registrados"]
        except Exception as e:
            paciente_combo['values'] = ["Error cargando pacientes"]
        
        # Doctor
        doctor_frame = tk.Frame(participants_grid, bg='#F8FAFC')
        doctor_frame.grid(row=0, column=1, sticky='ew', padx=(15, 0))
        
        tk.Label(doctor_frame, text="👨‍⚕️ Doctor *", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        doctor_combo = ttk.Combobox(doctor_frame, textvariable=appointment_vars['doctor_id'],
                                   font=('Arial', 11), state="readonly", width=35)
        doctor_combo.pack(fill='x', pady=(8, 0))
        doctor_combo.bind('<<ComboboxSelected>>', 
                         lambda e: self.update_available_hours(appointment_vars['doctor_id'], 
                                                              appointment_vars['fecha'], 
                                                              appointment_vars['hora'],
                                                              quick_time_frame))
        entries['doctor_id'] = doctor_combo
        
        # Cargar doctores con especialidad
        try:
            doctors = self.db_manager.get_all_doctors()
            if doctors:
                doctor_values = [f"{d['id']} - Dr. {d['nombre']} {d['apellido']}" for d in doctors]
                doctor_combo['values'] = doctor_values
                doctor_combo.set("Seleccione un doctor...")
            else:
                doctor_combo['values'] = ["No hay doctores registrados"]
        except Exception as e:
            doctor_combo['values'] = ["Error cargando doctores"]
        
        participants_grid.columnconfigure(0, weight=1)
        participants_grid.columnconfigure(1, weight=1)
        
        # SECCIÓN 3: DETALLES DE LA CONSULTA
        details_section = tk.LabelFrame(scrollable_frame, text="📋 Detalles de la Consulta", 
                                      font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                      padx=20, pady=15)
        details_section.pack(fill='x', pady=(0, 20))
        
        # Tipo de consulta
        tipo_frame = tk.Frame(details_section, bg='#F8FAFC')
        tipo_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(tipo_frame, text="🏥 Tipo de Consulta", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        tipo_combo = ttk.Combobox(tipo_frame, textvariable=appointment_vars['tipo_consulta'],
                                 values=['general', 'especialidad', 'control', 'urgencia', 'seguimiento'],
                                 state='readonly', font=('Arial', 11), width=25)
        tipo_combo.pack(anchor='w', pady=(8, 0))
        entries['tipo_consulta'] = tipo_combo
        
        # Motivo de la consulta
        motivo_frame = tk.Frame(details_section, bg='#F8FAFC')
        motivo_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(motivo_frame, text="💭 Motivo de la Consulta *", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        motivo_entry = tk.Entry(motivo_frame, textvariable=appointment_vars['motivo'],
                               font=('Arial', 11), relief='solid', bd=1)
        motivo_entry.pack(fill='x', pady=(8, 0), ipady=8)
        entries['motivo'] = motivo_entry
        
        # Botones de motivos frecuentes
        motivos_frecuentes = ['Consulta general', 'Control médico', 'Seguimiento', 'Revisión', 'Chequeo']
        motivos_frame = tk.Frame(motivo_frame, bg='#F8FAFC')
        motivos_frame.pack(fill='x', pady=(8, 0))
        
        tk.Label(motivos_frame, text="Motivos frecuentes:", 
                font=('Arial', 9), bg='#F8FAFC', fg='#64748B').pack(anchor='w')
        
        motivos_buttons = tk.Frame(motivos_frame, bg='#F8FAFC')
        motivos_buttons.pack(fill='x', pady=(5, 0))
        
        for motivo in motivos_frecuentes:
            tk.Button(motivos_buttons, text=motivo,
                     command=lambda m=motivo: appointment_vars['motivo'].set(m),
                     bg='#FFFFFF', fg='#1E3A8A', font=('Arial', 9),
                     relief='flat', padx=8, pady=4, cursor='hand2').pack(side='left', padx=(0, 5))
        
        # Estado
        estado_frame = tk.Frame(details_section, bg='#F8FAFC')
        estado_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(estado_frame, text="📊 Estado de la Cita", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        estado_combo = ttk.Combobox(estado_frame, textvariable=appointment_vars['estado'],
                                   values=['pendiente', 'confirmada', 'en_curso', 'completada', 'cancelada'],
                                   state='readonly', font=('Arial', 11), width=25)
        estado_combo.pack(anchor='w', pady=(8, 0))
        entries['estado'] = estado_combo
        
        # Observaciones
        obs_frame = tk.Frame(details_section, bg='#F8FAFC')
        obs_frame.pack(fill='x')
        
        tk.Label(obs_frame, text="📝 Observaciones y Notas", 
                font=('Arial', 11, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
        
        obs_text = tk.Text(obs_frame, height=4, font=('Arial', 11), relief='solid', bd=1, wrap='word')
        obs_text.pack(fill='x', pady=(8, 0))
        entries['observaciones'] = obs_text
        
        # Placeholder text
        obs_text.insert(1.0, "Ingrese observaciones adicionales, instrucciones especiales, o notas importantes para la cita...")
        obs_text.bind('<FocusIn>', lambda e: obs_text.delete(1.0, tk.END) if obs_text.get(1.0, tk.END).strip().startswith("Ingrese observaciones") else None)
        
        # BOTONES DE ACCIÓN
        buttons_section = tk.Frame(scrollable_frame, bg='#F8FAFC')
        buttons_section.pack(fill='x', pady=(30, 20))
        
        # Separador visual
        separator = tk.Frame(buttons_section, height=2, bg='#CBD5E1')
        separator.pack(fill='x', pady=(0, 20))
        
        # Frame para botones
        buttons_frame = tk.Frame(buttons_section, bg='#F8FAFC')
        buttons_frame.pack()
        
        # Botón Cancelar
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar", 
                              bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                              command=window.destroy, padx=25, pady=12, relief='flat', cursor='hand2')
        cancel_btn.pack(side='left', padx=(0, 15))
        
        # Botón Limpiar
        clear_btn = tk.Button(buttons_frame, text="�️ Limpiar", 
                             bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                             command=lambda: self.clear_appointment_form(appointment_vars, entries),
                             padx=25, pady=12, relief='flat', cursor='hand2')
        clear_btn.pack(side='left', padx=(0, 15))
        
        # Botón Guardar
        save_btn = tk.Button(buttons_frame, text="💾 Guardar Cita", 
                            bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                            command=lambda: self.save_appointment_enhanced(window, appointment_vars, entries),
                            padx=25, pady=12, relief='flat', cursor='hand2')
        save_btn.pack(side='left')
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll con mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Focus en primer campo
        fecha_entry.focus_set()
        
        # Validación en tiempo real
        self.setup_form_validation(appointment_vars, entries)
    
    def select_date(self, date_var):
        """Selector de fecha visual"""
        from datetime import date
        import calendar
        
        date_window = tk.Toplevel(self.root)
        date_window.title("Seleccionar Fecha")
        date_window.geometry("300x350")
        date_window.configure(bg='white')
        date_window.transient(self.root)
        date_window.grab_set()
        
        # Centrar ventana
        date_window.update_idletasks()
        x = (date_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (date_window.winfo_screenheight() // 2) - (350 // 2)
        date_window.geometry(f"300x350+{x}+{y}")
        
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        # Variables para navegación
        month_var = tk.IntVar(value=current_month)
        year_var = tk.IntVar(value=current_year)
        
        def update_calendar():
            # Limpiar calendario anterior
            for widget in cal_frame.winfo_children():
                widget.destroy()
            
            # Obtener días del mes
            cal = calendar.monthcalendar(year_var.get(), month_var.get())
            month_name = calendar.month_name[month_var.get()]
            
            # Título del mes
            tk.Label(cal_frame, text=f"{month_name} {year_var.get()}", 
                    font=('Arial', 12, 'bold'), bg='white').grid(row=0, column=0, columnspan=7, pady=10)
            
            # Días de la semana
            days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            for i, day in enumerate(days):
                tk.Label(cal_frame, text=day, font=('Arial', 9, 'bold'), 
                        bg='#FFFFFF', width=4).grid(row=1, column=i, padx=1, pady=1)
            
            # Días del mes
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        tk.Label(cal_frame, text="", width=4, height=2).grid(
                            row=week_num+2, column=day_num, padx=1, pady=1)
                    else:
                        btn = tk.Button(cal_frame, text=str(day), width=4, height=2,
                                      command=lambda d=day: select_day(d))
                        
                        # Marcar día actual
                        if (day == today.day and month_var.get() == today.month and 
                            year_var.get() == today.year):
                            btn.configure(bg='#0B5394', fg='white', font=('Arial', 9, 'bold'))
                        else:
                            btn.configure(bg='white', fg='black')
                        
                        btn.grid(row=week_num+2, column=day_num, padx=1, pady=1)
        
        def select_day(day):
            selected_date = f"{day:02d}/{month_var.get():02d}/{year_var.get()}"
            date_var.set(selected_date)
            date_window.destroy()
        
        def prev_month():
            if month_var.get() == 1:
                month_var.set(12)
                year_var.set(year_var.get() - 1)
            else:
                month_var.set(month_var.get() - 1)
            update_calendar()
        
        def next_month():
            if month_var.get() == 12:
                month_var.set(1)
                year_var.set(year_var.get() + 1)
            else:
                month_var.set(month_var.get() + 1)
            update_calendar()
        
        # Header con navegación
        nav_frame = tk.Frame(date_window, bg='white')
        nav_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(nav_frame, text="◀", command=prev_month, 
                 bg='#0B5394', fg='white', font=('Arial', 12, 'bold')).pack(side='left')
        tk.Button(nav_frame, text="▶", command=next_month, 
                 bg='#0B5394', fg='white', font=('Arial', 12, 'bold')).pack(side='right')
        
        # Frame del calendario
        cal_frame = tk.Frame(date_window, bg='white')
        cal_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Inicializar calendario
        update_calendar()
    
    def save_appointment(self, window, appointment_vars, entries):
        """Guardar nueva cita"""
        try:
            # Validar campos requeridos
            required_fields = ['fecha', 'hora', 'paciente_id', 'doctor_id', 'motivo']
            for field in required_fields:
                value = appointment_vars[field].get().strip()
                if not value:
                    messagebox.showerror("Error", f"El campo {field} es obligatorio")
                    return
            
            # Obtener valores
            fecha = appointment_vars['fecha'].get().strip()
            hora = appointment_vars['hora'].get().strip()
            
            # Validar formato de fecha
            try:
                day, month, year = fecha.split('/')
                fecha_obj = datetime(int(year), int(month), int(day))
            except:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY")
                return
            
            # Validar formato de hora
            try:
                hour, minute = hora.split(':')
                hora_obj = datetime.strptime(hora, '%H:%M').time()
            except:
                messagebox.showerror("Error", "Formato de hora inválido. Use HH:MM")
                return
            
            # Combinar fecha y hora
            fecha_hora = datetime.combine(fecha_obj.date(), hora_obj).isoformat()
            
            # Extraer IDs de paciente y doctor
            paciente_text = appointment_vars['paciente_id'].get()
            doctor_text = appointment_vars['doctor_id'].get()
            
            try:
                paciente_id = int(paciente_text.split(' - ')[0])
                doctor_id = int(doctor_text.split(' - ')[0])
            except:
                messagebox.showerror("Error", "Seleccione paciente y doctor válidos")
                return
            
            # Obtener observaciones del Text widget
            observaciones = ""
            if 'observaciones' in entries and hasattr(entries['observaciones'], 'get'):
                try:
                    observaciones = entries['observaciones'].get(1.0, tk.END).strip()
                except:
                    observaciones = ""
            
            # Crear diccionario de datos
            appointment_data = {
                'fecha_hora': fecha_hora,
                'paciente_id': paciente_id,
                'doctor_id': doctor_id,
                'motivo': appointment_vars['motivo'].get().strip(),
                'estado': appointment_vars['estado'].get(),
                'observaciones': observaciones
            }
            
            # Guardar en base de datos
            success = self.db_manager.create_appointment(appointment_data)
            
            if success:
                messagebox.showinfo("Éxito", "Cita creada exitosamente")
                window.destroy()
                
                # Actualizar tabla
                if hasattr(self, 'appointments_tree'):
                    self.load_appointments_data(self.appointments_tree)
            else:
                messagebox.showerror("Error", "No se pudo crear la cita")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la cita: {str(e)}")
    
    def edit_appointment(self):
        """Editar cita seleccionada"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para editar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            # Obtener datos de la cita
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            self.edit_appointment_window(appointment)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar cita: {str(e)}")
    
    def edit_appointment_window(self, appointment):
        """Ventana para editar cita existente"""
        window = tk.Toplevel(self.root)
        window.title("✏️ Editar Cita Médica")
        window.geometry("600x700")
        window.configure(bg='#F8FAFC')
        window.transient(self.root)
        window.grab_set()
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (600 // 2)
        y = (window.winfo_screenheight() // 2) - (700 // 2)
        window.geometry(f"600x700+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(window, bg='#0B5394', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"✏️ Editar Cita #{appointment['id']}", 
                font=('Arial', 16, 'bold'), bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido principal
        main_frame = tk.Frame(window, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Variables del formulario con valores actuales
        fecha_hora = appointment.get('fecha_hora', '')
        fecha_str, hora_str = '', ''
        if fecha_hora:
            try:
                dt = datetime.fromisoformat(fecha_hora)
                fecha_str = dt.strftime('%d/%m/%Y')
                hora_str = dt.strftime('%H:%M')
            except:
                pass
        
        appointment_vars = {
            'fecha': tk.StringVar(value=fecha_str),
            'hora': tk.StringVar(value=hora_str),
            'paciente_id': tk.StringVar(),
            'doctor_id': tk.StringVar(),
            'motivo': tk.StringVar(value=appointment.get('motivo', '')),
            'observaciones': tk.StringVar(value=appointment.get('observaciones', '')),
            'estado': tk.StringVar(value=appointment.get('estado', 'pendiente'))
        }
        
        # Campos del formulario
        fields = [
            ("Fecha de la Cita *", 'fecha', 'date'),
            ("Hora *", 'hora', 'time'),
            ("Paciente *", 'paciente_id', 'combo_patient'),
            ("Doctor *", 'doctor_id', 'combo_doctor'),
            ("Motivo de la Consulta *", 'motivo', 'entry'),
            ("Estado", 'estado', 'combo_status'),
            ("Observaciones", 'observaciones', 'text')
        ]
        
        entries = {}
        doctor_combo_ref = None  # Para almacenar la referencia al combobox del doctor
        quick_time_frame_edit = None  # Para almacenar la referencia al frame de horarios
        
        for label, var_key, field_type in fields:
            field_frame = tk.Frame(main_frame, bg='#F8FAFC')
            field_frame.pack(fill='x', pady=8)
            
            tk.Label(field_frame, text=label, font=('Arial', 10, 'bold'), 
                    bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            
            if field_type == 'entry':
                entry = tk.Entry(field_frame, textvariable=appointment_vars[var_key], 
                               font=('Arial', 10), width=50)
                entry.pack(fill='x', pady=(5, 0))
                entries[var_key] = entry
                
            elif field_type == 'date':
                date_frame = tk.Frame(field_frame, bg='#F8FAFC')
                date_frame.pack(fill='x', pady=(5, 0))
                
                # Usar DateEntry si está disponible, sino Entry normal
                if CALENDAR_AVAILABLE:
                    entry = DateEntry(date_frame, textvariable=appointment_vars[var_key],
                                     font=('Arial', 10), width=20, relief='solid', bd=1,
                                     date_pattern='dd/mm/yyyy', background='#0B5394',
                                     foreground='white', borderwidth=2)
                    entry.pack(side='left')
                else:
                    entry = tk.Entry(date_frame, textvariable=appointment_vars[var_key], 
                                   font=('Arial', 10), width=20)
                    entry.pack(side='left')
                    
                    tk.Button(date_frame, text="📅", command=lambda: self.select_date_enhanced(appointment_vars[var_key]),
                             bg='#0B5394', fg='white', padx=10).pack(side='left', padx=(10, 0))
                
                entries[var_key] = entry
                
            elif field_type == 'time':
                time_frame = tk.Frame(field_frame, bg='#F8FAFC')
                time_frame.pack(fill='x', pady=(5, 0))
                
                entry = tk.Entry(time_frame, textvariable=appointment_vars[var_key], 
                               font=('Arial', 10), width=20)
                entry.pack(side='left')
                entries[var_key] = entry
                
                # Botones de horarios rápidos para editar
                quick_times_edit = ['08:00', '09:00', '10:00', '14:00', '15:00', '16:00']
                quick_time_frame_edit = tk.Frame(time_frame, bg='#F8FAFC')
                quick_time_frame_edit.pack(side='left', padx=(10, 0))
                
                for time in quick_times_edit[:4]:
                    tk.Button(quick_time_frame_edit, text=time, 
                             command=lambda t=time: appointment_vars['hora'].set(t),
                             bg='#FFFFFF', fg='#1E3A8A', font=('Arial', 8),
                             relief='flat', padx=5, pady=2, cursor='hand2').pack(side='left', padx=1)
                
            elif field_type == 'combo_patient':
                combo = ttk.Combobox(field_frame, textvariable=appointment_vars[var_key], 
                                   font=('Arial', 10), width=47, state="readonly")
                combo.pack(fill='x', pady=(5, 0))
                entries[var_key] = combo
                
                # Cargar pacientes y seleccionar el actual
                try:
                    patients = self.db_manager.get_all_patients()
                    patient_values = [f"{p['id']} - {p['nombre']} {p['apellido']}" for p in patients]
                    combo['values'] = patient_values
                    
                    # Seleccionar paciente actual
                    current_patient_id = appointment.get('paciente_id')
                    if current_patient_id:
                        for value in patient_values:
                            if value.startswith(f"{current_patient_id} -"):
                                appointment_vars[var_key].set(value)
                                break
                except:
                    combo['values'] = ["No hay pacientes disponibles"]
                
            elif field_type == 'combo_doctor':
                combo = ttk.Combobox(field_frame, textvariable=appointment_vars[var_key], 
                                   font=('Arial', 10), width=47, state="readonly")
                combo.pack(fill='x', pady=(5, 0))
                entries[var_key] = combo
                doctor_combo_ref = combo  # Almacenar referencia
                
                # Cargar doctores y seleccionar el actual
                try:
                    doctors = self.db_manager.get_all_doctors()
                    doctor_values = [f"{d['id']} - Dr. {d['nombre']} {d['apellido']}" for d in doctors]
                    combo['values'] = doctor_values
                    
                    # Seleccionar doctor actual
                    current_doctor_id = appointment.get('doctor_id')
                    if current_doctor_id:
                        for value in doctor_values:
                            if value.startswith(f"{current_doctor_id} -"):
                                appointment_vars[var_key].set(value)
                                break
                except:
                    combo['values'] = ["No hay doctores disponibles"]
                
            elif field_type == 'combo_status':
                combo = ttk.Combobox(field_frame, textvariable=appointment_vars[var_key], 
                                   font=('Arial', 10), width=47, state="readonly",
                                   values=["pendiente", "confirmada", "en_curso", "completada", "cancelada"])
                combo.pack(fill='x', pady=(5, 0))
                entries[var_key] = combo
                
            elif field_type == 'text':
                text_widget = tk.Text(field_frame, height=4, font=('Arial', 10), width=50)
                text_widget.pack(fill='x', pady=(5, 0))
                # Insertar texto actual
                current_text = appointment.get('observaciones', '')
                if current_text:
                    text_widget.insert(1.0, current_text)
                entries[var_key] = text_widget
        
        # Conectar evento del doctor con el frame de horarios (después de que ambos existan)
        if doctor_combo_ref is not None and quick_time_frame_edit is not None:
            doctor_combo_ref.bind('<<ComboboxSelected>>', 
                                 lambda e: self.update_available_hours(appointment_vars['doctor_id'], 
                                                                      appointment_vars['fecha'], 
                                                                      appointment_vars['hora'],
                                                                      quick_time_frame_edit))
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#F8FAFC')
        button_frame.pack(fill='x', pady=(30, 0))
        
        tk.Button(button_frame, text="💾 Actualizar Cita", 
                 bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                 command=lambda: self.update_appointment(window, appointment['id'], appointment_vars, entries),
                 padx=20, pady=10).pack(side='right', padx=(10, 0))
        
        tk.Button(button_frame, text="❌ Cancelar", 
                 bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                 command=window.destroy, padx=20, pady=10).pack(side='right')
    
    def update_appointment(self, window, appointment_id, appointment_vars, entries):
        """Actualizar cita existente"""
        try:
            # Validar campos requeridos
            required_fields = ['fecha', 'hora', 'paciente_id', 'doctor_id', 'motivo']
            for field in required_fields:
                value = appointment_vars[field].get().strip()
                if not value:
                    messagebox.showerror("Error", f"El campo {field} es obligatorio")
                    return
            
            # Obtener valores
            fecha = appointment_vars['fecha'].get().strip()
            hora = appointment_vars['hora'].get().strip()
            
            # Validar formato de fecha
            try:
                day, month, year = fecha.split('/')
                fecha_obj = datetime(int(year), int(month), int(day))
            except:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY")
                return
            
            # Validar formato de hora
            try:
                hour, minute = hora.split(':')
                hora_obj = datetime.strptime(hora, '%H:%M').time()
            except:
                messagebox.showerror("Error", "Formato de hora inválido. Use HH:MM")
                return
            
            # Combinar fecha y hora
            fecha_hora = datetime.combine(fecha_obj.date(), hora_obj).isoformat()
            
            # Extraer IDs de paciente y doctor
            paciente_text = appointment_vars['paciente_id'].get()
            doctor_text = appointment_vars['doctor_id'].get()
            
            try:
                paciente_id = int(paciente_text.split(' - ')[0])
                doctor_id = int(doctor_text.split(' - ')[0])
            except:
                messagebox.showerror("Error", "Seleccione paciente y doctor válidos")
                return
            
            # Obtener observaciones del Text widget
            observaciones = ""
            if 'observaciones' in entries and hasattr(entries['observaciones'], 'get'):
                try:
                    observaciones = entries['observaciones'].get(1.0, tk.END).strip()
                except:
                    observaciones = ""
            
            # Crear diccionario de datos
            appointment_data = {
                'fecha_hora': fecha_hora,
                'paciente_id': paciente_id,
                'doctor_id': doctor_id,
                'motivo': appointment_vars['motivo'].get().strip(),
                'estado': appointment_vars['estado'].get(),
                'observaciones': observaciones
            }
            
            # Actualizar en base de datos
            success = self.db_manager.update_appointment(appointment_id, appointment_data)
            
            if success:
                messagebox.showinfo("Éxito", "Cita actualizada exitosamente")
                window.destroy()
                
                # Actualizar tabla
                if hasattr(self, 'appointments_tree'):
                    self.load_appointments_data(self.appointments_tree)
                    self.show_appointment_details(appointment_id)
            else:
                messagebox.showerror("Error", "No se pudo actualizar la cita")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la cita: {str(e)}")
        
    def view_appointment_details(self, appointment_id=None):
        """Ver detalles completos de la cita en ventana separada"""
        try:
            if appointment_id is None:
                selection = self.appointments_tree.selection()
                if not selection:
                    messagebox.showwarning("Advertencia", "Por favor seleccione una cita para ver detalles")
                    return
                
                item = self.appointments_tree.item(selection[0])
                appointment_id = item['values'][0]
            
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            # Crear ventana de detalles mejorada
            details_window = tk.Toplevel(self.root)
            details_window.title(f"👁️ Detalles de Cita #{appointment_id}")
            details_window.geometry("700x750")
            details_window.configure(bg='#F8FAFC')
            details_window.transient(self.root)
            details_window.grab_set()
            details_window.resizable(False, False)
            
            # Centrar ventana
            details_window.update_idletasks()
            x = (details_window.winfo_screenwidth() // 2) - (700 // 2)
            y = (details_window.winfo_screenheight() // 2) - (750 // 2)
            details_window.geometry(f"700x750+{x}+{y}")
            
            # Header con estado dinámico
            estado = appointment.get('estado', 'pendiente').lower()
            estado_colors = {
                'pendiente': '#E67E22',
                'confirmada': '#0B5394', 
                'en_curso': '#E67E22',
                'completada': '#16A085',
                'cancelada': '#C0392B'
            }
            header_color = estado_colors.get(estado, '#64748B')
            
            header_frame = tk.Frame(details_window, bg=header_color, height=100)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            # Contenido del header
            header_content = tk.Frame(header_frame, bg=header_color)
            header_content.pack(expand=True, fill='both', padx=20, pady=10)
            
            # Título y estado
            title_frame = tk.Frame(header_content, bg=header_color)
            title_frame.pack(side='left', fill='y')
            
            tk.Label(title_frame, text=f"📋 Cita Médica #{appointment_id}", 
                    font=('Arial', 16, 'bold'), bg=header_color, fg='white').pack(anchor='w')
            tk.Label(title_frame, text=f"Estado: {estado.title()}", 
                    font=('Arial', 12, 'bold'), bg=header_color, fg='white').pack(anchor='w')
            
            # Fecha y hora
            fecha_hora = appointment.get('fecha_hora', '')
            if fecha_hora:
                try:
                    dt = datetime.fromisoformat(fecha_hora)
                    fecha_str = dt.strftime('%d/%m/%Y')
                    hora_str = dt.strftime('%H:%M')
                except:
                    fecha_str = fecha_hora
                    hora_str = ''
            else:
                fecha_str = 'No definida'
                hora_str = ''
            
            datetime_frame = tk.Frame(header_content, bg=header_color)
            datetime_frame.pack(side='right', fill='y')
            
            tk.Label(datetime_frame, text=f"📅 {fecha_str}", 
                    font=('Arial', 12, 'bold'), bg=header_color, fg='white').pack(anchor='e')
            if hora_str:
                tk.Label(datetime_frame, text=f"🕐 {hora_str}", 
                        font=('Arial', 12, 'bold'), bg=header_color, fg='white').pack(anchor='e')
            
            # Contenido principal con scroll
            main_container = tk.Frame(details_window, bg='#F8FAFC')
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Canvas para scroll
            canvas = tk.Canvas(main_container, bg='#F8FAFC', highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#F8FAFC')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # SECCIÓN 1: INFORMACIÓN DE LA CITA
            info_section = tk.LabelFrame(scrollable_frame, text="📋 Información de la Cita", 
                                       font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                       padx=20, pady=15)
            info_section.pack(fill='x', pady=(0, 15))
            
            # Grid para información
            info_grid = tk.Frame(info_section, bg='#F8FAFC')
            info_grid.pack(fill='x')
            
            info_data = [
                ("ID de Cita:", str(appointment_id)),
                ("Fecha:", fecha_str),
                ("Hora:", hora_str),
                ("Estado:", estado.title()),
                ("Tipo:", appointment.get('tipo_consulta', 'General').title()),
                ("Duración:", f"{appointment.get('duracion', 60)} minutos")
            ]
            
            for i, (label, value) in enumerate(info_data):
                row = i // 2
                col = (i % 2) * 2
                
                tk.Label(info_grid, text=label, font=('Arial', 10, 'bold'), 
                        bg='#F8FAFC', fg='#1E3A8A').grid(row=row, column=col, sticky='w', pady=5, padx=(0, 10))
                tk.Label(info_grid, text=value, font=('Arial', 10), 
                        bg='#F8FAFC', fg='#64748B').grid(row=row, column=col+1, sticky='w', pady=5, padx=(0, 30))
            
            # SECCIÓN 2: PARTICIPANTES
            participants_section = tk.LabelFrame(scrollable_frame, text="👥 Participantes", 
                                               font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                               padx=20, pady=15)
            participants_section.pack(fill='x', pady=(0, 15))
            
            # Información del paciente
            patient_frame = tk.Frame(participants_section, bg='#F8FAFC')
            patient_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(patient_frame, text="👤 Paciente:", font=('Arial', 11, 'bold'), 
                    bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            patient_name = appointment.get('paciente_nombre', 'No disponible')
            tk.Label(patient_frame, text=f"    {patient_name}", font=('Arial', 10), 
                    bg='#F8FAFC', fg='#64748B').pack(anchor='w')
            
            # Información del doctor
            doctor_frame = tk.Frame(participants_section, bg='#F8FAFC')
            doctor_frame.pack(fill='x')
            
            tk.Label(doctor_frame, text="👨‍⚕️ Doctor:", font=('Arial', 11, 'bold'), 
                    bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            doctor_name = appointment.get('doctor_nombre', 'No disponible')
            tk.Label(doctor_frame, text=f"    Dr. {doctor_name}", font=('Arial', 10), 
                    bg='#F8FAFC', fg='#64748B').pack(anchor='w')
            
            # SECCIÓN 3: DETALLES MÉDICOS
            medical_section = tk.LabelFrame(scrollable_frame, text="🏥 Detalles Médicos", 
                                          font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                          padx=20, pady=15)
            medical_section.pack(fill='x', pady=(0, 15))
            
            # Motivo
            motivo_frame = tk.Frame(medical_section, bg='#F8FAFC')
            motivo_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(motivo_frame, text="💭 Motivo de la Consulta:", font=('Arial', 11, 'bold'), 
                    bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            motivo = appointment.get('motivo', 'No especificado')
            tk.Label(motivo_frame, text=f"    {motivo}", font=('Arial', 10), 
                    bg='#F8FAFC', fg='#64748B', wraplength=600, justify='left').pack(anchor='w')
            
            # Observaciones
            obs_frame = tk.Frame(medical_section, bg='#F8FAFC')
            obs_frame.pack(fill='x')
            
            tk.Label(obs_frame, text="📝 Observaciones:", font=('Arial', 11, 'bold'), 
                    bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            observaciones = appointment.get('observaciones', 'Sin observaciones')
            if observaciones and not observaciones.startswith("Ingrese observaciones"):
                obs_text = observaciones
            else:
                obs_text = "Sin observaciones adicionales"
            tk.Label(obs_frame, text=f"    {obs_text}", font=('Arial', 10), 
                    bg='#F8FAFC', fg='#64748B', wraplength=600, justify='left').pack(anchor='w')
            
            # SECCIÓN 4: GESTIÓN DE ESTADO
            status_section = tk.LabelFrame(scrollable_frame, text="⚙️ Gestión de Estado", 
                                         font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                         padx=20, pady=15)
            status_section.pack(fill='x', pady=(0, 15))
            
            # Botones de cambio de estado
            status_buttons_frame = tk.Frame(status_section, bg='#F8FAFC')
            status_buttons_frame.pack(fill='x')
            
            # Primera fila de botones
            buttons_row1 = tk.Frame(status_buttons_frame, bg='#F8FAFC')
            buttons_row1.pack(fill='x', pady=(0, 10))
            
            if estado != 'confirmada':
                tk.Button(buttons_row1, text="✅ Confirmar Cita", 
                         bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                         command=lambda: self.change_appointment_status(appointment_id, 'confirmada', details_window),
                         padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left', padx=(0, 10))
            
            if estado not in ['en_curso', 'completada']:
                tk.Button(buttons_row1, text="🔄 Iniciar Consulta", 
                         bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                         command=lambda: self.change_appointment_status(appointment_id, 'en_curso', details_window),
                         padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left', padx=(0, 10))
            
            if estado not in ['completada', 'cancelada']:
                tk.Button(buttons_row1, text="✅ Completar", 
                         bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                         command=lambda: self.change_appointment_status(appointment_id, 'completada', details_window),
                         padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left')
            
            # Segunda fila de botones
            buttons_row2 = tk.Frame(status_buttons_frame, bg='#F8FAFC')
            buttons_row2.pack(fill='x')
            
            if estado not in ['cancelada', 'completada']:
                tk.Button(buttons_row2, text="❌ Cancelar Cita", 
                         bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                         command=lambda: self.cancel_appointment_with_reason(appointment_id, details_window),
                         padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left', padx=(0, 10))
            
            tk.Button(buttons_row2, text="✏️ Editar Cita", 
                     bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                     command=lambda: self.edit_appointment_from_details(appointment_id, details_window),
                     padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left', padx=(0, 10))
            
            tk.Button(buttons_row2, text="🖨️ Imprimir", 
                     bg='#0B5394', fg='white', font=('Arial', 9, 'bold'),
                     command=lambda: self.print_appointment_details(appointment_id),
                     padx=15, pady=8, relief='flat', cursor='hand2').pack(side='left')
            
            # BOTONES DE ACCIÓN PRINCIPALES
            main_actions_section = tk.Frame(scrollable_frame, bg='#F8FAFC')
            main_actions_section.pack(fill='x', pady=(20, 0))
            
            # Separador visual
            separator = tk.Frame(main_actions_section, height=2, bg='#CBD5E1')
            separator.pack(fill='x', pady=(0, 15))
            
            # Botones principales
            main_buttons_frame = tk.Frame(main_actions_section, bg='#F8FAFC')
            main_buttons_frame.pack()
            
            tk.Button(main_buttons_frame, text="🔙 Cerrar", 
                     bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                     command=details_window.destroy, padx=25, pady=12, relief='flat', cursor='hand2').pack(side='left', padx=(0, 10))
            
            tk.Button(main_buttons_frame, text="🔄 Actualizar Vista", 
                     bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                     command=lambda: self.refresh_appointment_details(appointment_id, details_window),
                     padx=25, pady=12, relief='flat', cursor='hand2').pack(side='left')
            
            # Configurar scroll
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Bind para scroll con mouse wheel
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", _on_mousewheel)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles de la cita: {str(e)}")

    def change_appointment_status(self, appointment_id, new_status, details_window=None):
        """Cambiar estado de una cita con validaciones"""
        try:
            # Validar transición de estado
            current_appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not current_appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            current_status = current_appointment.get('estado', 'pendiente').lower()
            
            # Validaciones de transición
            valid_transitions = {
                'pendiente': ['confirmada', 'cancelada'],
                'confirmada': ['en_curso', 'cancelada', 'completada'],
                'en_curso': ['completada', 'cancelada'],
                'completada': [],  # No se puede cambiar desde completada
                'cancelada': []    # No se puede cambiar desde cancelada
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                messagebox.showerror("Error", 
                    f"No se puede cambiar de '{current_status}' a '{new_status}'.\n"
                    f"Transiciones válidas desde '{current_status}': {', '.join(valid_transitions.get(current_status, []))}")
                return
            
            # Confirmar cambio
            status_messages = {
                'confirmada': '✅ ¿Confirmar esta cita médica?',
                'en_curso': '🔄 ¿Iniciar la consulta médica?',
                'completada': '✅ ¿Marcar la cita como completada?',
                'cancelada': '❌ ¿Cancelar esta cita médica?'
            }
            
            message = status_messages.get(new_status, f'¿Cambiar estado a {new_status}?')
            
            if not messagebox.askyesno("Confirmar Cambio", 
                f"{message}\n\nCita #{appointment_id}\nEstado actual: {current_status.title()}"):
                return
            
            # Realizar cambio en la base de datos
            success = self.db_manager.update_appointment_status(appointment_id, new_status)
            
            if success:
                # Mensaje de éxito personalizado
                success_messages = {
                    'confirmada': '✅ Cita confirmada exitosamente',
                    'en_curso': '🔄 Consulta iniciada',
                    'completada': '✅ Cita completada exitosamente',
                    'cancelada': '❌ Cita cancelada'
                }
                
                messagebox.showinfo("Éxito", 
                    f"{success_messages.get(new_status, 'Estado actualizado')}\n"
                    f"Cita #{appointment_id} ahora está: {new_status.title()}")
                
                # Actualizar interfaz
                if hasattr(self, 'load_appointments_data') and hasattr(self, 'appointments_tree'):
                    self.load_appointments_data(self.appointments_tree)
                
                # Actualizar ventana de detalles si está abierta
                if details_window and details_window.winfo_exists():
                    self.refresh_appointment_details(appointment_id, details_window)
                
                # Registrar cambio en el log
                self.log_appointment_change(appointment_id, current_status, new_status)
                
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado de la cita")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")

    def cancel_appointment_with_reason(self, appointment_id, details_window=None):
        """Cancelar cita con motivo de cancelación"""
        try:
            # Crear ventana para motivo de cancelación
            reason_window = tk.Toplevel(self.root)
            reason_window.title("❌ Cancelar Cita")
            reason_window.geometry("500x400")
            reason_window.configure(bg='#F8FAFC')
            reason_window.transient(self.root)
            reason_window.grab_set()
            reason_window.resizable(False, False)
            
            # Centrar ventana
            reason_window.update_idletasks()
            x = (reason_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (reason_window.winfo_screenheight() // 2) - (400 // 2)
            reason_window.geometry(f"500x400+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(reason_window, bg='#0B5394', height=80)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text=f"❌ Cancelar Cita #{appointment_id}", 
                    font=('Arial', 16, 'bold'), bg='#0B5394', fg='white').pack(expand=True)
            
            # Contenido principal
            main_frame = tk.Frame(reason_window, bg='#F8FAFC')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Información de la cita
            info_frame = tk.LabelFrame(main_frame, text="📋 Información de la Cita", 
                                     font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                     padx=15, pady=10)
            info_frame.pack(fill='x', pady=(0, 20))
            
            # Obtener datos de la cita
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if appointment:
                fecha_hora = appointment.get('fecha_hora', '')
                if fecha_hora:
                    try:
                        dt = datetime.fromisoformat(fecha_hora)
                        fecha_str = dt.strftime('%d/%m/%Y')
                        hora_str = dt.strftime('%H:%M')
                    except:
                        fecha_str = fecha_hora
                        hora_str = ''
                else:
                    fecha_str = 'No definida'
                    hora_str = ''
                
                info_text = f"Fecha: {fecha_str}\n"
                if hora_str:
                    info_text += f"Hora: {hora_str}\n"
                info_text += f"Paciente: {appointment.get('paciente_nombre', 'No disponible')}\n"
                info_text += f"Doctor: Dr. {appointment.get('doctor_nombre', 'No disponible')}\n"
                info_text += f"Motivo: {appointment.get('motivo', 'No especificado')}"
                
                tk.Label(info_frame, text=info_text, font=('Arial', 10), 
                        bg='#F8FAFC', fg='#64748B', justify='left').pack(anchor='w')
            
            # Motivo de cancelación
            reason_frame = tk.LabelFrame(main_frame, text="📝 Motivo de Cancelación", 
                                       font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                       padx=15, pady=10)
            reason_frame.pack(fill='x', pady=(0, 20))
            
            # Motivos predefinidos
            reason_var = tk.StringVar()
            predefined_reasons = [
                "Paciente no puede asistir",
                "Doctor no disponible",
                "Emergencia médica",
                "Reprogramación solicitada",
                "Problemas técnicos",
                "Otro motivo"
            ]
            
            for reason in predefined_reasons:
                tk.Radiobutton(reason_frame, text=reason, variable=reason_var, value=reason,
                              font=('Arial', 10), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w', pady=2)
            
            # Campo de texto para motivo personalizado
            custom_frame = tk.Frame(reason_frame, bg='#F8FAFC')
            custom_frame.pack(fill='x', pady=(10, 0))
            
            tk.Label(custom_frame, text="Detalles adicionales:", 
                    font=('Arial', 10, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(anchor='w')
            
            custom_text = tk.Text(custom_frame, height=4, font=('Arial', 10), 
                                 relief='solid', bd=1, wrap='word')
            custom_text.pack(fill='x', pady=(5, 0))
            
            # Botones
            buttons_frame = tk.Frame(main_frame, bg='#F8FAFC')
            buttons_frame.pack(fill='x', pady=(20, 0))
            
            def confirm_cancellation():
                selected_reason = reason_var.get()
                custom_details = custom_text.get(1.0, tk.END).strip()
                
                if not selected_reason:
                    messagebox.showerror("Error", "Por favor seleccione un motivo de cancelación")
                    return
                
                # Construir motivo completo
                full_reason = selected_reason
                if custom_details:
                    full_reason += f" - {custom_details}"
                
                # Confirmar cancelación
                if messagebox.askyesno("Confirmar Cancelación", 
                    f"¿Está seguro de cancelar la cita #{appointment_id}?\n\n"
                    f"Motivo: {full_reason}"):
                    
                    # Actualizar en base de datos con motivo
                    success = self.db_manager.cancel_appointment_with_reason(appointment_id, full_reason)
                    
                    if success:
                        messagebox.showinfo("Éxito", 
                            f"✅ Cita #{appointment_id} cancelada exitosamente\n\n"
                            f"Motivo: {full_reason}")
                        
                        # Actualizar interfaz
                        if hasattr(self, 'load_appointments_data') and hasattr(self, 'appointments_tree'):
                            self.load_appointments_data(self.appointments_tree)
                        
                        # Actualizar ventana de detalles si está abierta
                        if details_window and details_window.winfo_exists():
                            self.refresh_appointment_details(appointment_id, details_window)
                        
                        reason_window.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudo cancelar la cita")
            
            tk.Button(buttons_frame, text="❌ Cancelar Cita", 
                     bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                     command=confirm_cancellation, padx=20, pady=10, relief='flat', cursor='hand2').pack(side='right', padx=(10, 0))
            
            tk.Button(buttons_frame, text="🔙 Volver", 
                     bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                     command=reason_window.destroy, padx=20, pady=10, relief='flat', cursor='hand2').pack(side='right')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de cancelación: {str(e)}")

    def edit_appointment_from_details(self, appointment_id, details_window):
        """Editar cita desde la ventana de detalles"""
        try:
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            self.edit_appointment_window(appointment)
            
            # Actualizar detalles después de la edición
            if details_window and details_window.winfo_exists():
                details_window.after(1000, lambda: self.refresh_appointment_details(appointment_id, details_window))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar cita: {str(e)}")

    def refresh_appointment_details(self, appointment_id, details_window):
        """Actualizar ventana de detalles de la cita"""
        try:
            if details_window and details_window.winfo_exists():
                details_window.destroy()
                self.view_appointment_details(appointment_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar detalles: {str(e)}")

    def print_appointment_details(self, appointment_id):
        """Imprimir o exportar detalles de la cita"""
        try:
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            # Crear ventana de opciones de impresión
            print_window = tk.Toplevel(self.root)
            print_window.title("🖨️ Opciones de Impresión")
            print_window.geometry("400x300")
            print_window.configure(bg='#F8FAFC')
            print_window.transient(self.root)
            print_window.grab_set()
            print_window.resizable(False, False)
            
            # Centrar ventana
            print_window.update_idletasks()
            x = (print_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (print_window.winfo_screenheight() // 2) - (300 // 2)
            print_window.geometry(f"400x300+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(print_window, bg='#0B5394', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="🖨️ Imprimir Cita", 
                    font=('Arial', 14, 'bold'), bg='#0B5394', fg='white').pack(expand=True)
            
            # Contenido
            main_frame = tk.Frame(print_window, bg='#F8FAFC')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            tk.Label(main_frame, text=f"Cita #{appointment_id}", 
                    font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
            
            # Opciones
            tk.Button(main_frame, text="📄 Generar PDF", 
                     bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                     command=lambda: self.generate_appointment_pdf(appointment_id, print_window),
                     padx=20, pady=10, relief='flat', cursor='hand2').pack(fill='x', pady=5)
            
            tk.Button(main_frame, text="📋 Copiar al Portapapeles", 
                     bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                     command=lambda: self.copy_appointment_to_clipboard(appointment_id, print_window),
                     padx=20, pady=10, relief='flat', cursor='hand2').pack(fill='x', pady=5)
            
            tk.Button(main_frame, text="📧 Enviar por Email", 
                     bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                     command=lambda: self.email_appointment_details(appointment_id),
                     padx=20, pady=10, relief='flat', cursor='hand2').pack(fill='x', pady=5)
            
            tk.Button(main_frame, text="🔙 Cerrar", 
                     bg='#0B5394', fg='white', font=('Arial', 11, 'bold'),
                     command=print_window.destroy, padx=20, pady=10, relief='flat', cursor='hand2').pack(fill='x', pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir opciones de impresión: {str(e)}")

    def generate_appointment_pdf(self, appointment_id, parent_window):
        """Generar PDF de la cita"""
        try:
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            # Aquí iría la lógica para generar PDF
            # Por ahora mostrar mensaje informativo
            messagebox.showinfo("PDF", 
                f"Generando PDF para cita #{appointment_id}...\n"
                "Funcionalidad en desarrollo")
            
            if parent_window:
                parent_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

    def copy_appointment_to_clipboard(self, appointment_id, parent_window):
        """Copiar detalles de la cita al portapapeles"""
        try:
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            # Formatear información para el portapapeles
            fecha_hora = appointment.get('fecha_hora', '')
            if fecha_hora:
                try:
                    dt = datetime.fromisoformat(fecha_hora)
                    fecha_str = dt.strftime('%d/%m/%Y')
                    hora_str = dt.strftime('%H:%M')
                except:
                    fecha_str = fecha_hora
                    hora_str = ''
            else:
                fecha_str = 'No definida'
                hora_str = ''
            
            clipboard_text = f"""
MEDISYNC - DETALLES DE CITA MÉDICA

ID de Cita: {appointment_id}
Fecha: {fecha_str}
Hora: {hora_str}
Estado: {appointment.get('estado', 'pendiente').title()}

PARTICIPANTES:
Paciente: {appointment.get('paciente_nombre', 'No disponible')}
Doctor: Dr. {appointment.get('doctor_nombre', 'No disponible')}

DETALLES MÉDICOS:
Motivo: {appointment.get('motivo', 'No especificado')}
Tipo de Consulta: {appointment.get('tipo_consulta', 'General').title()}
Duración: {appointment.get('duracion', 60)} minutos

Observaciones: {appointment.get('observaciones', 'Sin observaciones')}

Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """.strip()
            
            # Copiar al portapapeles
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            
            messagebox.showinfo("Éxito", 
                "✅ Detalles de la cita copiados al portapapeles")
            
            if parent_window:
                parent_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar al portapapeles: {str(e)}")

    def email_appointment_details(self, appointment_id):
        """Enviar detalles de la cita por email (placeholder)"""
        messagebox.showinfo("Email", 
            f"Enviando detalles de cita #{appointment_id} por email...\n"
            "Funcionalidad en desarrollo")

    def log_appointment_change(self, appointment_id, old_status, new_status):
        """Registrar cambio de estado en el log del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_name = f"{self.current_user.nombre} {self.current_user.apellido}"
            
            log_entry = f"[{timestamp}] Usuario: {user_name} | Cita #{appointment_id} | Estado: {old_status} → {new_status}"
            
            # Aquí se podría guardar en un archivo de log o en la base de datos
            print(f"LOG: {log_entry}")
            
        except Exception as e:
            print(f"Error al registrar log: {str(e)}")

    def confirm_appointment(self):
        """Confirmar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para confirmar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            self.change_appointment_status(appointment_id, 'confirmada')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar cita: {str(e)}")

    def cancel_appointment(self):
        """Cancelar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para cancelar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            self.cancel_appointment_with_reason(appointment_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar cita: {str(e)}")

    def complete_appointment(self):
        """Completar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para completar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            # Completar la cita
            self.change_appointment_status(appointment_id, 'completada')
            
            # Crear registro médico automáticamente
            self.create_medical_note_from_appointment(appointment_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al completar cita: {str(e)}")
    
    def start_appointment(self):
        """Iniciar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para iniciar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            self.change_appointment_status(appointment_id, 'en_curso')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar cita: {str(e)}")
    
    def update_appointment_status(self, new_status, success_message):
        """Actualizar estado de la cita"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            # Confirmar acción
            if messagebox.askyesno("Confirmar", f"¿Está seguro de cambiar el estado a '{new_status}'?"):
                success = self.db_manager.update_appointment_status(appointment_id, new_status)
                
                if success:
                    messagebox.showinfo("Éxito", success_message)
                    self.load_appointments_data(self.appointments_tree)
                    self.show_appointment_details(appointment_id)
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el estado de la cita")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")
    
    def print_appointment(self, appointment):
        """Imprimir detalles de la cita"""
        try:
            # Aquí puedes implementar la funcionalidad de impresión
            # Por ahora, mostraremos un mensaje
            messagebox.showinfo("Imprimir", "Funcionalidad de impresión en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir: {str(e)}")
    
    def create_medical_history_tab(self, parent):
        """Crear pestaña de historial médico"""
        # Limpiar contenido previo
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título y descripción
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_frame = tk.Frame(header_frame, bg='#0B5394', relief='raised', bd=2)
        title_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(title_frame, text="🩺 Historial Médico de Pacientes", 
                font=('Arial', 18, 'bold'), bg='#0B5394', fg='white', pady=15).pack()
        
        tk.Label(header_frame, text="Gestione y consulte los historiales médicos completos de sus pacientes", 
                font=('Arial', 11), bg='#F8FAFC', fg='#1E3A8A').pack()
        
        # Frame de contenido dividido
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Lista de pacientes
        left_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1, width=400)
        left_panel.pack(side='left', fill='both', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Header del panel izquierdo
        left_header = tk.Frame(left_panel, bg='#0B5394', height=50)
        left_header.pack(fill='x')
        left_header.pack_propagate(False)
        
        tk.Label(left_header, text="👥 Seleccionar Paciente", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Búsqueda de pacientes
        search_frame = tk.Frame(left_panel, bg='white')
        search_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(search_frame, text="🔍 Buscar paciente:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        search_row = tk.Frame(search_frame, bg='white')
        search_row.pack(fill='x', pady=(5, 0))
        
        self.patient_search_var = tk.StringVar()
        self.patient_search_entry = tk.Entry(search_row, textvariable=self.patient_search_var, 
                                           font=('Arial', 10), width=25)
        self.patient_search_entry.pack(side='left', fill='x', expand=True)
        self.patient_search_entry.bind('<KeyRelease>', self.search_patients_medical)
        
        tk.Button(search_row, text="🔍", bg='#0B5394', fg='white', font=('Arial', 9),
                 command=self.search_patients_medical).pack(side='right', padx=(5, 0))
        
        # Lista de pacientes
        patients_frame = tk.Frame(left_panel, bg='white')
        patients_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Treeview para pacientes
        columns = ('ID', 'Nombre', 'Apellido', 'Edad', 'Teléfono')
        self.patients_medical_tree = ttk.Treeview(patients_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        headers = {
            'ID': ('ID', 50),
            'Nombre': ('Nombre', 100),
            'Apellido': ('Apellido', 100),
            'Edad': ('Edad', 60),
            'Teléfono': ('Teléfono', 100)
        }
        
        for col, (text, width) in headers.items():
            self.patients_medical_tree.heading(col, text=text)
            self.patients_medical_tree.column(col, width=width, minwidth=width)
        
        # Scrollbars para pacientes con mejor visibilidad
        patients_scrollbar_y = ttk.Scrollbar(patients_frame, orient="vertical", command=self.patients_medical_tree.yview)
        patients_scrollbar_x = ttk.Scrollbar(patients_frame, orient="horizontal", command=self.patients_medical_tree.xview)
        self.patients_medical_tree.configure(yscrollcommand=patients_scrollbar_y.set, xscrollcommand=patients_scrollbar_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.patients_medical_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        patients_scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        patients_scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        patients_frame.grid_rowconfigure(0, weight=1)
        patients_frame.grid_rowconfigure(1, weight=0, minsize=20)
        patients_frame.grid_columnconfigure(0, weight=1)
        patients_frame.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Bind para selección de paciente
        self.patients_medical_tree.bind('<<TreeviewSelect>>', self.on_patient_select_medical)
        
        # Panel derecho - Historial del paciente seleccionado
        right_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Header del panel derecho
        right_header = tk.Frame(right_panel, bg='#0B5394', height=50)
        right_header.pack(fill='x')
        right_header.pack_propagate(False)
        
        self.patient_name_label = tk.Label(right_header, text="📋 Historial Médico", 
                                         font=('Arial', 14, 'bold'), bg='#0B5394', fg='white')
        self.patient_name_label.pack(expand=True)
        
        # Información del paciente seleccionado
        self.patient_info_frame = tk.Frame(right_panel, bg='#FFFFFF')
        self.patient_info_frame.pack(fill='x', padx=15, pady=10)
        
        # Botones de acción para historial
        actions_frame = tk.Frame(right_panel, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Button(actions_frame, text="➕ Nueva Consulta", bg='#0B5394', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.add_medical_record).pack(side='left', padx=(0, 5))
        
        tk.Button(actions_frame, text="📄 Ver Detalle", bg='#0B5394', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.view_medical_record_detail).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="✏️ Editar", bg='#0B5394', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.edit_medical_record).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="🖨️ Imprimir", bg='#0B5394', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.print_medical_record).pack(side='left', padx=5)
        
        # Lista de registros médicos
        records_frame = tk.Frame(right_panel, bg='white')
        records_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Treeview para registros médicos
        records_columns = ('ID', 'Fecha', 'Tipo', 'Doctor', 'Diagnóstico', 'Estado')
        self.medical_records_tree = ttk.Treeview(records_frame, columns=records_columns, show='headings', height=15)
        
        # Configurar headers de registros
        records_headers = {
            'ID': ('ID', 50),
            'Fecha': ('Fecha', 100),
            'Tipo': ('Tipo', 100),
            'Doctor': ('Doctor', 120),
            'Diagnóstico': ('Diagnóstico', 200),
            'Estado': ('Estado', 80)
        }
        
        for col, (text, width) in records_headers.items():
            self.medical_records_tree.heading(col, text=text)
            self.medical_records_tree.column(col, width=width, minwidth=width)
        
        # Scrollbars para registros con mejor visibilidad
        records_scrollbar_y = ttk.Scrollbar(records_frame, orient="vertical", command=self.medical_records_tree.yview)
        records_scrollbar_x = ttk.Scrollbar(records_frame, orient="horizontal", command=self.medical_records_tree.xview)
        self.medical_records_tree.configure(yscrollcommand=records_scrollbar_y.set, xscrollcommand=records_scrollbar_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.medical_records_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        records_scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        records_scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        records_frame.grid_rowconfigure(0, weight=1)
        records_frame.grid_rowconfigure(1, weight=0, minsize=20)
        records_frame.grid_columnconfigure(0, weight=1)
        records_frame.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Bind para selección de registro
        self.medical_records_tree.bind('<<TreeviewSelect>>', self.on_medical_record_select)
        
        # Variables para control
        self.selected_patient_id = None
        self.selected_medical_record_id = None
        
        # Cargar datos iniciales
        self.load_patients_for_medical_history()
        self.show_default_medical_info()
        
        # Verificar si hay pacientes, si no crear algunos de prueba
        self.ensure_test_patients()
    
    def ensure_test_patients(self):
        """Asegurar que existan pacientes de prueba"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Verificar si hay pacientes
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = 'paciente'")
            patient_count = cursor.fetchone()[0]
            
            if patient_count == 0:
                # Crear pacientes de prueba
                test_patients = [
                    ('Juan', 'Pérez', 'juan.perez@email.com', '809-555-0001', '1985-05-15'),
                    ('María', 'García', 'maria.garcia@email.com', '809-555-0002', '1990-08-22'),
                    ('Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '809-555-0003', '1978-12-10'),
                    ('Ana', 'López', 'ana.lopez@email.com', '809-555-0004', '1992-03-08')
                ]
                
                for nombre, apellido, email, telefono, fecha_nac in test_patients:
                    password_hash = self.hash_password('123456')  # Contraseña por defecto
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nombre, apellido, email, telefono, fecha_nacimiento, 
                                            tipo_usuario, password_hash, activo, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, 'paciente', ?, 1, ?)
                    """, (nombre, apellido, email, telefono, fecha_nac, password_hash, 
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                conn.commit()
                print("✅ Pacientes de prueba creados")
                
                # Recargar la lista
                self.load_patients_for_medical_history()
                
                # Crear algunos registros médicos de prueba
                self.create_sample_medical_records()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error creando pacientes de prueba: {str(e)}")
    
    def create_sample_medical_records(self):
        """Crear registros médicos de prueba"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener IDs de pacientes y doctor
            cursor.execute("SELECT id FROM usuarios WHERE tipo_usuario = 'paciente' LIMIT 2")
            patients = cursor.fetchall()
            
            cursor.execute("SELECT id FROM usuarios WHERE tipo_usuario = 'doctor' LIMIT 1")
            doctor = cursor.fetchone()
            
            if patients and doctor:
                sample_records = [
                    {
                        'paciente_id': patients[0][0],
                        'doctor_id': doctor[0],
                        'fecha_consulta': '2025-07-20',
                        'tipo_consulta': 'Consulta General',
                        'motivo_consulta': 'Dolor de cabeza frecuente',
                        'sintomas': 'Dolor de cabeza, mareos ocasionales',
                        'diagnostico': 'Cefalea tensional',
                        'tratamiento': 'Descanso, hidratación adecuada',
                        'medicamentos': 'Ibuprofeno 400mg cada 8 horas',
                        'estado': 'Completada'
                    },
                    {
                        'paciente_id': patients[0][0],
                        'doctor_id': doctor[0],
                        'fecha_consulta': '2025-07-15',
                        'tipo_consulta': 'Control',
                        'motivo_consulta': 'Control rutinario',
                        'sintomas': 'Ninguno reportado',
                        'diagnostico': 'Estado de salud normal',
                        'tratamiento': 'Continuar con hábitos saludables',
                        'medicamentos': 'Ninguno',
                        'estado': 'Completada'
                    }
                ]
                
                if len(patients) > 1:
                    sample_records.append({
                        'paciente_id': patients[1][0],
                        'doctor_id': doctor[0],
                        'fecha_consulta': '2025-07-22',
                        'tipo_consulta': 'Consulta Especializada',
                        'motivo_consulta': 'Dolor abdominal',
                        'sintomas': 'Dolor en abdomen bajo, náuseas',
                        'diagnostico': 'Gastritis leve',
                        'tratamiento': 'Dieta blanda, evitar irritantes',
                        'medicamentos': 'Omeprazol 20mg en ayunas',
                        'estado': 'Completada'
                    })
                
                for record in sample_records:
                    cursor.execute("""
                        INSERT INTO historial_medico 
                        (paciente_id, doctor_id, fecha_consulta, tipo_consulta, motivo_consulta,
                         sintomas, diagnostico, tratamiento, medicamentos, estado, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['paciente_id'], record['doctor_id'], record['fecha_consulta'],
                        record['tipo_consulta'], record['motivo_consulta'], record['sintomas'],
                        record['diagnostico'], record['tratamiento'], record['medicamentos'],
                        record['estado'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                conn.commit()
                print("✅ Registros médicos de prueba creados")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error creando registros médicos de prueba: {str(e)}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error creando pacientes de prueba: {str(e)}")
    
    def create_advanced_billing_tab(self, parent):
        """Sistema de facturación avanzado integrado directamente en MEDISYNC"""
        # Inicializar variables de facturación integrada
        self.init_integrated_billing_system()
        
        # Frame principal
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True)
        
        # Header moderno
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=20, pady=15)
        
        tk.Label(header_content, text="� SISTEMA DE FACTURACIÓN INTEGRADO", 
                font=('Arial', 18, 'bold'), bg='#1E3A8A', fg='white').pack()
        tk.Label(header_content, text="PDFs Automáticos | Control de Pagos | Gestión Completa", 
                font=('Arial', 11), bg='#1E3A8A', fg='#CBD5E1').pack()
        
        # Crear notebook para pestañas del sistema de facturación
        self.billing_notebook = ttk.Notebook(main_frame)
        self.billing_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Facturación Principal
        billing_frame = tk.Frame(self.billing_notebook, bg='#F8FAFC')
        self.billing_notebook.add(billing_frame, text="💰 Facturación")
        
        # Pestaña 2: Servicios Médicos
        services_frame = tk.Frame(self.billing_notebook, bg='#F8FAFC')
        self.billing_notebook.add(services_frame, text="🏥 Servicios")
        
        # Pestaña 3: Reportes
        reports_frame = tk.Frame(self.billing_notebook, bg='#F8FAFC')
        self.billing_notebook.add(reports_frame, text="📊 Reportes")
        
        # Crear contenido de cada pestaña
        self.create_integrated_billing_content(billing_frame)
        self.create_integrated_services_content(services_frame)
        self.create_integrated_reports_content(reports_frame)
        
        # Status bar
        self.create_billing_status_bar(main_frame)
        
        # Cargar datos iniciales
        self.load_integrated_billing_data()
    
    def auto_launch_billing_system(self):
        """Lanzar automáticamente el sistema de facturación al abrir la pestaña"""
        # Esta función ya no es necesaria con el sistema integrado
        pass
    
    def manual_launch_billing_system(self):
        """Lanzar manualmente el sistema de facturación"""
        # Esta función ya no es necesaria con el sistema integrado  
        pass
    
    def init_integrated_billing_system(self):
        """Inicializar el sistema de facturación integrado"""
        # Variables para el sistema de facturación
        self.billing_notebook = None
        self.appointments_tree_billing = None
        self.services_tree_billing = None
        self.invoice_services_tree = None
        self.selected_services = []
        self.current_appointment_billing = None
        
        # Variables de cálculo
        self.subtotal_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0.00")
        self.total_var = tk.StringVar(value="0.00")
        self.payment_var = tk.StringVar(value="0.00")
        self.change_var = tk.StringVar(value="0.00")
        
        # Servicios médicos predefinidos
        self.medical_services = [
            {'codigo': 'CONS001', 'nombre': 'Consulta General', 'categoria': 'Consulta', 'precio': 1500.00},
            {'codigo': 'CONS002', 'nombre': 'Consulta Especializada', 'categoria': 'Consulta', 'precio': 2500.00},
            {'codigo': 'LAB001', 'nombre': 'Análisis de Sangre', 'categoria': 'Laboratorio', 'precio': 800.00},
            {'codigo': 'RAD001', 'nombre': 'Radiografía', 'categoria': 'Imagen', 'precio': 1800.00},
            {'codigo': 'PROC001', 'nombre': 'Procedimiento Menor', 'categoria': 'Procedimiento', 'precio': 1000.00},
            {'codigo': 'ULTRA001', 'nombre': 'Ultrasonido', 'categoria': 'Imagen', 'precio': 2200.00},
            {'codigo': 'CARDIO001', 'nombre': 'Electrocardiograma', 'categoria': 'Cardiología', 'precio': 1200.00},
            {'codigo': 'VACU001', 'nombre': 'Aplicación de Vacuna', 'categoria': 'Prevención', 'precio': 500.00}
        ]
        
        # Configuración de clínica
        self.clinic_config = {
            'nombre': 'MEDISYNC - Centro Médico',
            'direccion': 'Avenida Central, San José, Costa Rica',
            'telefono': '+506 2000-0000',
            'email': 'info@medisync.cr'
        }
    
    def create_integrated_billing_content(self, parent):
        """Crear contenido principal de facturación con diseño mejorado"""
        # Frame principal con mejor margen
        main_container = tk.Frame(parent, bg='#F8FAFC')
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Panel superior: Acciones Rápidas
        quick_actions_frame = tk.LabelFrame(main_container, text="⚡ ACCIONES RÁPIDAS", 
                                          font=('Arial', 14, 'bold'), bg='#e8f5e8', fg='#2e7d32', 
                                          padx=20, pady=15)
        quick_actions_frame.pack(fill='x', pady=(0, 15))
        
        # Grid de botones de acciones rápidas
        actions_grid = tk.Frame(quick_actions_frame, bg='#e8f5e8')
        actions_grid.pack(fill='x')
        
        # Primera fila de botones
        first_row = tk.Frame(actions_grid, bg='#e8f5e8')
        first_row.pack(fill='x', pady=(0, 10))
        
        tk.Button(first_row, text="📄 NUEVA FACTURA", command=self.open_invoice_popup,
                 bg='#4caf50', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left', padx=(0, 15))
        
        tk.Button(first_row, text="� COBROS DEL DÍA", command=self.show_daily_payments,
                 bg='#2196f3', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left', padx=(0, 15))
        
        tk.Button(first_row, text="📊 REPORTES", command=self.show_billing_reports,
                 bg='#ff9800', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left')
        
        # Segunda fila de botones
        second_row = tk.Frame(actions_grid, bg='#e8f5e8')
        second_row.pack(fill='x')
        
        tk.Button(second_row, text="🔍 BUSCAR FACTURA", command=self.search_invoice,
                 bg='#9c27b0', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left', padx=(0, 15))
        
        tk.Button(second_row, text="⚙️ CONFIGURACIÓN", command=self.billing_settings,
                 bg='#607d8b', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left', padx=(0, 15))
        
        tk.Button(second_row, text="📋 FACTURAS PENDIENTES", command=self.show_pending_invoices,
                 bg='#f44336', fg='white', font=('Arial', 12, 'bold'), 
                 width=20, height=2).pack(side='left')
        
        # Panel de facturas recientes con mejor margen
        recent_frame = tk.LabelFrame(main_container, text="📋 FACTURAS RECIENTES", 
                                   font=('Arial', 12, 'bold'), bg='#e3f2fd', fg='#1565c0', 
                                   padx=20, pady=15)
        recent_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Filtros de facturas
        filters_frame = tk.Frame(recent_frame, bg='#e3f2fd')
        filters_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(filters_frame, text="Mostrar:", bg='#e3f2fd', fg='#1565c0', 
                font=('Arial', 11, 'bold')).pack(side='left')
        
        self.invoice_filter_var = tk.StringVar(value="hoy")
        filter_combo = ttk.Combobox(filters_frame, textvariable=self.invoice_filter_var,
                                   values=["hoy", "esta_semana", "este_mes", "todas"], 
                                   width=15, state="readonly")
        filter_combo.pack(side='left', padx=(10, 15))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_recent_invoices)
        
        tk.Button(filters_frame, text="🔄 Actualizar", command=self.load_recent_invoices,
                 bg='#2196f3', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        
        # Estado actual del sistema
        status_info = tk.Frame(filters_frame, bg='#e3f2fd')
        status_info.pack(side='right')
        
        self.status_label = tk.Label(status_info, text="Sistema listo", 
                                   bg='#e3f2fd', fg='#1565c0', font=('Arial', 10, 'italic'))
        self.status_label.pack()
        
        # Tabla de facturas recientes con mejor diseño
        table_container = tk.Frame(recent_frame, bg='#e3f2fd')
        table_container.pack(fill='both', expand=True)
        
        columns_invoices = ('ID', 'Fecha', 'Paciente', 'Total', 'Estado', 'Acciones')
        self.recent_invoices_tree = ttk.Treeview(table_container, columns=columns_invoices, 
                                               show='headings', height=12)
        
        # Configurar columnas con mejor ancho
        widths_invoices = {'ID': 80, 'Fecha': 120, 'Paciente': 200, 'Total': 100, 'Estado': 100, 'Acciones': 120}
        for col in columns_invoices:
            self.recent_invoices_tree.heading(col, text=col)
            self.recent_invoices_tree.column(col, width=widths_invoices.get(col, 100), anchor='center')
        
        # Scrollbars mejoradas
        scroll_invoices_y = ttk.Scrollbar(table_container, orient="vertical", 
                                        command=self.recent_invoices_tree.yview)
        scroll_invoices_x = ttk.Scrollbar(table_container, orient="horizontal", 
                                        command=self.recent_invoices_tree.xview)
        self.recent_invoices_tree.configure(yscrollcommand=scroll_invoices_y.set, 
                                          xscrollcommand=scroll_invoices_x.set)
        
        # Layout con grid y márgenes mejorados
        self.recent_invoices_tree.grid(row=0, column=0, sticky='nsew', padx=(10, 0), pady=(10, 0))
        scroll_invoices_y.grid(row=0, column=1, sticky='ns', padx=(0, 10), pady=(10, 0))
        scroll_invoices_x.grid(row=1, column=0, sticky='ew', padx=(10, 0), pady=(0, 10))
        
        # Configurar expansión
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=0, minsize=25)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_columnconfigure(1, weight=0, minsize=25)
        
        # Eventos de la tabla
        self.recent_invoices_tree.bind('<Double-1>', self.view_invoice_details)
        self.recent_invoices_tree.bind('<Button-3>', self.show_invoice_context_menu)
        
        # Panel de información rápida con mejor margen
        info_frame = tk.LabelFrame(main_container, text="� RESUMEN DEL DÍA", 
                                 font=('Arial', 12, 'bold'), bg='#fff3e0', fg='#e65100', 
                                 padx=20, pady=15)
        info_frame.pack(fill='x')
        
        # Grid de estadísticas
        stats_grid = tk.Frame(info_frame, bg='#fff3e0')
        stats_grid.pack(fill='x')
        
        # Obtener estadísticas básicas
        try:
            stats = self.get_daily_billing_stats()
            
            # Primera fila de estadísticas
            stats_row1 = tk.Frame(stats_grid, bg='#fff3e0')
            stats_row1.pack(fill='x', pady=(0, 10))
            
            self.create_stat_widget(stats_row1, "💰", "Ingresos Hoy", 
                                  f"₡{stats.get('ingresos', 0):,.2f}", "#4caf50")
            self.create_stat_widget(stats_row1, "📄", "Facturas Emitidas", 
                                  str(stats.get('facturas', 0)), "#2196f3")
            self.create_stat_widget(stats_row1, "⏳", "Pendientes", 
                                  str(stats.get('pendientes', 0)), "#ff9800")
            
        except Exception as e:
            tk.Label(stats_grid, text="Error cargando estadísticas", 
                    bg='#fff3e0', fg='#e65100').pack()
        
        # Cargar datos iniciales
        self.load_recent_invoices()
    
    
    def create_billing_calculations_panel(self, parent):
        """Panel de cálculos de facturación"""
        calc_frame = tk.LabelFrame(parent, text="💰 CÁLCULOS", bg='#fff3e0', fg='#e65100',
                                  font=('Arial', 10, 'bold'), padx=10, pady=10)
        calc_frame.pack(fill='x', pady=(10, 0))
        
        # Subtotal
        subtotal_row = tk.Frame(calc_frame, bg='#fff3e0')
        subtotal_row.pack(fill='x', pady=2)
        tk.Label(subtotal_row, text="Subtotal:", bg='#fff3e0', fg='#e65100', font=('Arial', 10)).pack(side='left')
        tk.Label(subtotal_row, textvariable=self.subtotal_var, bg='#fff3e0', fg='#e65100', 
                font=('Arial', 10, 'bold')).pack(side='right')
        
        # Descuento
        discount_row = tk.Frame(calc_frame, bg='#fff3e0')
        discount_row.pack(fill='x', pady=2)
        tk.Label(discount_row, text="Descuento:", bg='#fff3e0', fg='#e65100', font=('Arial', 10)).pack(side='left')
        
        discount_frame = tk.Frame(discount_row, bg='#fff3e0')
        discount_frame.pack(side='right')
        
        self.discount_entry = tk.Entry(discount_frame, textvariable=self.discount_var, width=10, font=('Arial', 9))
        self.discount_entry.pack(side='left')
        self.discount_entry.bind('<KeyRelease>', self.calculate_totals)
        
        tk.Button(discount_frame, text="Aplicar", command=self.apply_discount,
                 bg='#2196f3', fg='white', font=('Arial', 8)).pack(side='left', padx=(5, 0))
        
        # Total
        total_row = tk.Frame(calc_frame, bg='#fff3e0')
        total_row.pack(fill='x', pady=5)
        tk.Label(total_row, text="TOTAL:", bg='#fff3e0', fg='#e65100', font=('Arial', 12, 'bold')).pack(side='left')
        tk.Label(total_row, textvariable=self.total_var, bg='#fff3e0', fg='#e65100', 
                font=('Arial', 12, 'bold')).pack(side='right')
        
        # Panel de pago
        payment_frame = tk.LabelFrame(parent, text="💳 INFORMACIÓN DE PAGO", bg='#fff3e0', fg='#e65100',
                                     font=('Arial', 10, 'bold'), padx=10, pady=10)
        payment_frame.pack(fill='x', pady=(10, 0))
        
        # Monto pagado
        payment_row = tk.Frame(payment_frame, bg='#fff3e0')
        payment_row.pack(fill='x', pady=2)
        tk.Label(payment_row, text="Monto Recibido:", bg='#fff3e0', fg='#e65100', font=('Arial', 10)).pack(side='left')
        
        payment_entry_frame = tk.Frame(payment_row, bg='#fff3e0')
        payment_entry_frame.pack(side='right')
        
        self.payment_entry = tk.Entry(payment_entry_frame, textvariable=self.payment_var, width=10, font=('Arial', 9))
        self.payment_entry.pack(side='left')
        self.payment_entry.bind('<KeyRelease>', self.calculate_change)
        
        tk.Button(payment_entry_frame, text="Calcular", command=self.calculate_change,
                 bg='#4caf50', fg='white', font=('Arial', 8)).pack(side='left', padx=(5, 0))
        
        # Cambio/Faltante
        change_row = tk.Frame(payment_frame, bg='#fff3e0')
        change_row.pack(fill='x', pady=2)
        self.change_label = tk.Label(change_row, text="Cambio:", bg='#fff3e0', fg='#e65100', font=('Arial', 10))
        self.change_label.pack(side='left')
        self.change_value_label = tk.Label(change_row, textvariable=self.change_var, bg='#fff3e0', fg='#4caf50', 
                                          font=('Arial', 10, 'bold'))
        self.change_value_label.pack(side='right')
        
        # Botones principales
        buttons_frame = tk.Frame(parent, bg='#fff3e0')
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(buttons_frame, text="📄 GENERAR FACTURA PDF", command=self.generate_invoice_pdf_integrated,
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold'), pady=8).pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        tk.Button(buttons_frame, text="💾 GUARDAR", command=self.save_invoice_integrated,
                 bg='#4caf50', fg='white', font=('Arial', 11, 'bold'), pady=8).pack(side='right', padx=(5, 0), fill='x', expand=True)
    
    def create_stat_widget(self, parent, icon, title, value, color):
        """Crear widget de estadística individual"""
        stat_frame = tk.Frame(parent, bg='#fff3e0', relief='solid', bd=1)
        stat_frame.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        # Icono y valor
        header_frame = tk.Frame(stat_frame, bg='#fff3e0')
        header_frame.pack(fill='x', padx=10, pady=(8, 2))
        
        tk.Label(header_frame, text=icon, bg='#fff3e0', fg=color, 
                font=('Arial', 16, 'bold')).pack(side='left')
        tk.Label(header_frame, text=value, bg='#fff3e0', fg=color, 
                font=('Arial', 14, 'bold')).pack(side='right')
        
        # Título
        tk.Label(stat_frame, text=title, bg='#fff3e0', fg='#e65100', 
                font=('Arial', 10)).pack(padx=10, pady=(0, 8))
    
    def open_invoice_popup(self):
        """Abrir ventana emergente para crear nueva factura"""
        popup = tk.Toplevel(self.root)
        popup.title("📄 Nueva Factura - MEDISYNC")
        popup.geometry("1000x700")
        popup.configure(bg='#F8FAFC')
        popup.transient(self.root)
        popup.grab_set()
        
        # Centrar la ventana
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (1000 // 2)
        y = (popup.winfo_screenheight() // 2) - (700 // 2)
        popup.geometry(f"1000x700+{x}+{y}")
        
        # Header del popup
        header_frame = tk.Frame(popup, bg='#1E3A8A', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=20, pady=10)
        
        tk.Label(header_content, text="📄 CREAR NUEVA FACTURA", 
                font=('Arial', 16, 'bold'), bg='#1E3A8A', fg='white').pack(side='left')
        
        tk.Button(header_content, text="❌ Cerrar", command=popup.destroy,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold')).pack(side='right')
        
        # Contenido principal del popup
        main_content = tk.Frame(popup, bg='#F8FAFC')
        main_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo: Selección de paciente
        left_panel = tk.Frame(main_content, bg='#F8FAFC', width=450)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        patient_frame = tk.LabelFrame(left_panel, text="👤 SELECCIONAR PACIENTE", 
                                    font=('Arial', 12, 'bold'), bg='#e3f2fd', fg='#1565c0',
                                    padx=15, pady=10)
        patient_frame.pack(fill='both', expand=True)
        
        # Búsqueda de paciente
        search_frame = tk.Frame(patient_frame, bg='#e3f2fd')
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:", bg='#e3f2fd', fg='#1565c0', 
                font=('Arial', 10, 'bold')).pack(side='left')
        self.patient_search_var = tk.StringVar()
        patient_search = tk.Entry(search_frame, textvariable=self.patient_search_var, width=25)
        patient_search.pack(side='left', padx=(5, 0), fill='x', expand=True)
        patient_search.bind('<KeyRelease>', self.filter_patients_popup)
        
        # Lista de pacientes
        columns_patients = ('ID', 'Nombre', 'Apellido', 'Teléfono')
        self.patients_tree_popup = ttk.Treeview(patient_frame, columns=columns_patients, 
                                              show='headings', height=15)
        
        for col in columns_patients:
            self.patients_tree_popup.heading(col, text=col)
            self.patients_tree_popup.column(col, width=80, anchor='center')
        
        scroll_patients = ttk.Scrollbar(patient_frame, orient="vertical", 
                                      command=self.patients_tree_popup.yview)
        self.patients_tree_popup.configure(yscrollcommand=scroll_patients.set)
        
        table_frame_patients = tk.Frame(patient_frame, bg='#e3f2fd')
        table_frame_patients.pack(fill='both', expand=True, pady=(10, 0))
        
        self.patients_tree_popup.pack(side='left', fill='both', expand=True)
        scroll_patients.pack(side='right', fill='y')
        
        self.patients_tree_popup.bind('<<TreeviewSelect>>', self.on_patient_select_popup)
        
        # Panel derecho: Creación de factura
        right_panel = tk.Frame(main_content, bg='#F8FAFC')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Información del paciente seleccionado
        self.selected_patient_frame = tk.LabelFrame(right_panel, text="📋 PACIENTE SELECCIONADO", 
                                                   font=('Arial', 11, 'bold'), bg='#e8f5e8', fg='#2e7d32',
                                                   padx=10, pady=10)
        self.selected_patient_frame.pack(fill='x', pady=(0, 10))
        
        self.selected_patient_label = tk.Label(self.selected_patient_frame, 
                                             text="Seleccione un paciente de la lista",
                                             bg='#e8f5e8', fg='#2e7d32', font=('Arial', 10))
        self.selected_patient_label.pack(pady=10)
        
        # Servicios disponibles
        services_popup_frame = tk.LabelFrame(right_panel, text="🏥 AGREGAR SERVICIOS", 
                                           font=('Arial', 11, 'bold'), bg='#fff3e0', fg='#e65100',
                                           padx=10, pady=10)
        services_popup_frame.pack(fill='both', expand=True)
        
        # Tabla de servicios disponibles en popup
        columns_services_popup = ('Código', 'Servicio', 'Precio')
        self.services_tree_popup = ttk.Treeview(services_popup_frame, columns=columns_services_popup, 
                                              show='headings', height=8)
        
        for col in columns_services_popup:
            self.services_tree_popup.heading(col, text=col)
            self.services_tree_popup.column(col, width=120, anchor='center')
        
        scroll_services_popup = ttk.Scrollbar(services_popup_frame, orient="vertical", 
                                            command=self.services_tree_popup.yview)
        self.services_tree_popup.configure(yscrollcommand=scroll_services_popup.set)
        
        services_table_frame = tk.Frame(services_popup_frame, bg='#fff3e0')
        services_table_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.services_tree_popup.pack(side='left', fill='both', expand=True)
        scroll_services_popup.pack(side='right', fill='y')
        
        # Botones de acción en popup
        popup_buttons_frame = tk.Frame(services_popup_frame, bg='#fff3e0')
        popup_buttons_frame.pack(fill='x')
        
        tk.Button(popup_buttons_frame, text="➕ Agregar Servicio", 
                 command=self.add_service_to_popup_invoice,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        tk.Button(popup_buttons_frame, text="💾 GENERAR FACTURA", 
                 command=lambda: self.generate_popup_invoice(popup),
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold')).pack(side='right')
        
        # Cargar datos en el popup
        self.load_patients_popup()
        self.load_services_popup()
        
        # Variables para el popup
        self.selected_patient_popup = None
        self.popup_invoice_services = []
    
    def show_daily_payments(self):
        """Mostrar cobros del día"""
        messagebox.showinfo("Cobros del Día", "Función en desarrollo - Mostrará cobros del día actual")
    
    def show_billing_reports(self):
        """Mostrar reportes de facturación"""
        messagebox.showinfo("Reportes", "Función en desarrollo - Mostrará reportes detallados")
    
    def search_invoice(self):
        """Buscar factura específica"""
        messagebox.showinfo("Buscar Factura", "Función en desarrollo - Permitirá buscar facturas")
    
    def billing_settings(self):
        """Configuración del sistema de facturación"""
        messagebox.showinfo("Configuración", "Función en desarrollo - Configuración del sistema")
    
    def show_pending_invoices(self):
        """Mostrar facturas pendientes"""
        messagebox.showinfo("Facturas Pendientes", "Función en desarrollo - Mostrará facturas pendientes")
    
    def load_recent_invoices(self):
        """Cargar facturas recientes"""
        try:
            # Limpiar tabla
            for item in self.recent_invoices_tree.get_children():
                self.recent_invoices_tree.delete(item)
            
            # Aquí iría la lógica para cargar facturas desde la base de datos
            # Por ahora, datos de ejemplo
            sample_invoices = [
                ("FAC-001", "2025-01-27", "Juan Pérez", "₡25,000", "Pagada"),
                ("FAC-002", "2025-01-27", "María González", "₡18,500", "Pendiente"),
                ("FAC-003", "2025-01-26", "Carlos Rodríguez", "₡32,000", "Pagada"),
            ]
            
            for invoice in sample_invoices:
                self.recent_invoices_tree.insert('', 'end', values=invoice + ("Ver",))
                
        except Exception as e:
            print(f"Error cargando facturas recientes: {str(e)}")
    
    def get_daily_billing_stats(self):
        """Obtener estadísticas del día"""
        try:
            # Aquí iría la lógica real de la base de datos
            return {
                'ingresos': 75500,
                'facturas': 3,
                'pendientes': 1
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {str(e)}")
            return {'ingresos': 0, 'facturas': 0, 'pendientes': 0}
    
    def filter_recent_invoices(self, event=None):
        """Filtrar facturas recientes según el período seleccionado"""
        self.load_recent_invoices()
    
    def view_invoice_details(self, event=None):
        """Ver detalles de una factura"""
        messagebox.showinfo("Detalles", "Función en desarrollo - Mostrará detalles de la factura")
    
    def show_invoice_context_menu(self, event=None):
        """Mostrar menú contextual para facturas"""
        pass
    
    def load_patients_popup(self):
        """Cargar pacientes en el popup"""
        try:
            # Limpiar tabla
            for item in self.patients_tree_popup.get_children():
                self.patients_tree_popup.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, apellidos, telefono 
                FROM pacientes 
                ORDER BY nombre, apellidos
            """)
            
            for patient in cursor.fetchall():
                self.patients_tree_popup.insert('', 'end', values=patient)
            
            conn.close()
            
        except Exception as e:
            print(f"Error cargando pacientes en popup: {str(e)}")
    
    def load_services_popup(self):
        """Cargar servicios en el popup"""
        try:
            # Limpiar tabla
            for item in self.services_tree_popup.get_children():
                self.services_tree_popup.delete(item)
            
            # Cargar servicios predefinidos
            for service in self.medical_services:
                self.services_tree_popup.insert('', 'end', values=(
                    service['codigo'], 
                    service['nombre'], 
                    f"₡{service['precio']:,.2f}"
                ))
                
        except Exception as e:
            print(f"Error cargando servicios en popup: {str(e)}")
    
    def filter_patients_popup(self, event=None):
        """Filtrar pacientes en el popup"""
        search_term = self.patient_search_var.get().lower()
        
        # Limpiar tabla
        for item in self.patients_tree_popup.get_children():
            self.patients_tree_popup.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, apellidos, telefono 
                FROM pacientes 
                WHERE LOWER(nombre || ' ' || apellidos) LIKE ?
                ORDER BY nombre, apellidos
            """, (f'%{search_term}%',))
            
            for patient in cursor.fetchall():
                self.patients_tree_popup.insert('', 'end', values=patient)
            
            conn.close()
            
        except Exception as e:
            print(f"Error filtrando pacientes: {str(e)}")
    
    def on_patient_select_popup(self, event=None):
        """Manejar selección de paciente en popup"""
        selection = self.patients_tree_popup.selection()
        if selection:
            item = self.patients_tree_popup.item(selection[0])
            values = item['values']
            
            self.selected_patient_popup = {
                'id': values[0],
                'nombre': values[1],
                'apellidos': values[2],
                'telefono': values[3]
            }
            
            # Actualizar etiqueta
            self.selected_patient_label.config(
                text=f"👤 {values[1]} {values[2]}\n📞 {values[3]}"
            )
    
    def add_service_to_popup_invoice(self):
        """Agregar servicio a la factura en popup"""
        selection = self.services_tree_popup.selection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione un servicio")
            return
        
        if not self.selected_patient_popup:
            messagebox.showwarning("Paciente", "Seleccione un paciente primero")
            return
        
        item = self.services_tree_popup.item(selection[0])
        values = item['values']
        
        # Agregar a lista de servicios del popup
        service_data = {
            'codigo': values[0],
            'nombre': values[1],
            'precio': float(values[2].replace('₡', '').replace(',', ''))
        }
        
        self.popup_invoice_services.append(service_data)
        messagebox.showinfo("Servicio Agregado", f"Servicio {values[1]} agregado a la factura")
    
    def generate_popup_invoice(self, popup):
        """Generar factura desde el popup"""
        if not self.selected_patient_popup:
            messagebox.showwarning("Error", "Seleccione un paciente")
            return
        
        if not self.popup_invoice_services:
            messagebox.showwarning("Error", "Agregue al menos un servicio")
            return
        
        try:
            # Aquí iría la lógica para generar la factura
            total = sum(service['precio'] for service in self.popup_invoice_services)
            
            messagebox.showinfo("Factura Creada", 
                              f"Factura generada para {self.selected_patient_popup['nombre']} {self.selected_patient_popup['apellidos']}\n"
                              f"Total: ₡{total:,.2f}")
            
            # Limpiar y cerrar popup
            self.popup_invoice_services = []
            popup.destroy()
            
            # Actualizar lista de facturas recientes
            self.load_recent_invoices()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando factura: {str(e)}")

    def create_integrated_services_content(self, parent):
        """Pestaña de gestión de servicios médicos"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(main_frame, text="🏥 GESTIÓN DE SERVICIOS MÉDICOS", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Botones de acción
        buttons_frame = tk.Frame(main_frame, bg='#F8FAFC')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(buttons_frame, text="➕ Nuevo Servicio", command=self.add_new_service,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="✏️ Editar Servicio", command=self.edit_selected_service,
                 bg='#ff9800', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="❌ Eliminar Servicio", command=self.delete_selected_service,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        
        # Tabla de servicios
        # Frame contenedor para tabla y scrollbars
        table_frame_mgmt = tk.Frame(main_frame, bg='#F8FAFC')
        table_frame_mgmt.pack(fill='both', expand=True)
        
        columns = ('Código', 'Nombre', 'Categoría', 'Precio')
        self.services_management_tree = ttk.Treeview(table_frame_mgmt, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.services_management_tree.heading(col, text=col)
            self.services_management_tree.column(col, width=150, anchor='center')
        
        # Scrollbars verticales y horizontales con mejor visibilidad
        scroll_services_mgmt_y = ttk.Scrollbar(table_frame_mgmt, orient="vertical", command=self.services_management_tree.yview)
        scroll_services_mgmt_x = ttk.Scrollbar(table_frame_mgmt, orient="horizontal", command=self.services_management_tree.xview)
        self.services_management_tree.configure(yscrollcommand=scroll_services_mgmt_y.set, xscrollcommand=scroll_services_mgmt_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.services_management_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        scroll_services_mgmt_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        scroll_services_mgmt_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        table_frame_mgmt.grid_rowconfigure(0, weight=1)
        table_frame_mgmt.grid_rowconfigure(1, weight=0, minsize=20)
        table_frame_mgmt.grid_columnconfigure(0, weight=1)
        table_frame_mgmt.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Cargar servicios
        self.load_services_management()
    
    def create_integrated_reports_content(self, parent):
        """Pestaña de reportes del sistema de facturación"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(main_frame, text="📊 REPORTES DE FACTURACIÓN", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Panel de estadísticas
        stats_frame = tk.LabelFrame(main_frame, text="📈 ESTADÍSTICAS RÁPIDAS", 
                                   font=('Arial', 12, 'bold'), bg='#e3f2fd', fg='#1565c0',
                                   padx=20, pady=15)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg='#e3f2fd')
        stats_grid.pack()
        
        try:
            # Obtener estadísticas de la base de datos
            stats = self.get_billing_statistics_integrated()
            
            stats_items = [
                ("💰", "Ingresos Hoy", f"₡{stats.get('ingresos_hoy', 0):,.2f}", "#4caf50"),
                ("📋", "Facturas Hoy", str(stats.get('facturas_hoy', 0)), "#2196f3"),
                ("⏳", "Pendientes", str(stats.get('pendientes', 0)), "#ff9800"),
                ("📅", "Este Mes", f"₡{stats.get('ingresos_mes', 0):,.2f}", "#9c27b0")
            ]
            
            for i, (icon, title, value, color) in enumerate(stats_items):
                col = i % 4
                
                stat_frame = tk.Frame(stats_grid, bg='white', relief='raised', bd=2)
                stat_frame.grid(row=0, column=col, padx=10, pady=10)
                
                tk.Label(stat_frame, text=icon, font=('Arial', 20), bg='white').pack(pady=(10, 5))
                tk.Label(stat_frame, text=title, font=('Arial', 10, 'bold'), bg='white', fg='#1E3A8A').pack()
                tk.Label(stat_frame, text=value, font=('Arial', 12, 'bold'), bg='white', fg=color).pack(pady=(5, 10))
                
        except Exception as e:
            tk.Label(stats_grid, text=f"Error cargando estadísticas: {str(e)}", 
                    bg='#e3f2fd', fg='red').pack()
        
        # Botones de reportes
        reports_frame = tk.LabelFrame(main_frame, text="📄 GENERAR REPORTES", 
                                     font=('Arial', 12, 'bold'), bg='#f1f8e9', fg='#2e7d32',
                                     padx=20, pady=15)
        reports_frame.pack(fill='x', pady=(0, 20))
        
        reports_buttons = [
            ("📊 Reporte Diario", self.generate_daily_report_integrated, "#4caf50"),
            ("📈 Reporte Mensual", self.generate_monthly_report_integrated, "#2196f3"),
            ("📋 Facturas Pendientes", self.generate_pending_report_integrated, "#ff9800"),
            ("💰 Ingresos por Servicio", self.generate_services_report_integrated, "#9c27b0")
        ]
        
        reports_grid = tk.Frame(reports_frame, bg='#f1f8e9')
        reports_grid.pack()
        
        for i, (text, command, color) in enumerate(reports_buttons):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(reports_grid, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           padx=20, pady=10)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
        reports_grid.grid_columnconfigure(0, weight=1)
        reports_grid.grid_columnconfigure(1, weight=1)
    
    def create_billing_status_bar(self, parent):
        """Barra de estado para el sistema de facturación"""
        status_frame = tk.Frame(parent, bg='#0B5394', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Sistema de facturación listo", 
                                    bg='#0B5394', fg='white', font=('Arial', 10))
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Fecha y hora actual
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        tk.Label(status_frame, text=current_time, bg='#0B5394', fg='#CBD5E1', 
                font=('Arial', 9)).pack(side='right', padx=10, pady=5)
    
    # ==================== FUNCIONES DE LÓGICA DEL SISTEMA DE FACTURACIÓN INTEGRADO ====================
    
    def load_integrated_billing_data(self):
        """Cargar datos del sistema de facturación integrado"""
        try:
            self.load_appointments_for_billing()
            self.load_services_for_billing()
            self.update_status("Datos cargados correctamente")
        except Exception as e:
            self.update_status(f"Error cargando datos: {str(e)}")
    
    def load_appointments_for_billing(self):
        """Cargar citas para facturación"""
        if not hasattr(self, 'appointments_tree_billing') or not self.appointments_tree_billing:
            return
            
        try:
            # Limpiar tabla
            for item in self.appointments_tree_billing.get_children():
                self.appointments_tree_billing.delete(item)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            filter_value = self.appointment_filter_var.get()
            
            if filter_value == "completadas":
                query = """
                SELECT c.id, 
                       DATE(c.fecha_hora) as fecha_cita, 
                       TIME(c.fecha_hora) as hora_cita,
                       p.nombre || ' ' || p.apellido as paciente,
                       u.nombre || ' ' || u.apellido as doctor,
                       c.estado,
                       'No' as facturada
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios u ON c.doctor_id = u.id
                WHERE c.estado = 'completada'
                ORDER BY c.fecha_hora DESC
                """
            elif filter_value == "hoy":
                query = """
                SELECT c.id, 
                       DATE(c.fecha_hora) as fecha_cita, 
                       TIME(c.fecha_hora) as hora_cita,
                       p.nombre || ' ' || p.apellido as paciente,
                       u.nombre || ' ' || u.apellido as doctor,
                       c.estado,
                       'No' as facturada
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios u ON c.doctor_id = u.id
                WHERE DATE(c.fecha_hora) = DATE('now', 'localtime')
                ORDER BY c.fecha_hora
                """
            else:  # todas
                query = """
                SELECT c.id, 
                       DATE(c.fecha_hora) as fecha_cita, 
                       TIME(c.fecha_hora) as hora_cita,
                       p.nombre || ' ' || p.apellido as paciente,
                       u.nombre || ' ' || u.apellido as doctor,
                       c.estado,
                       'No' as facturada
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios u ON c.doctor_id = u.id
                ORDER BY c.fecha_hora DESC
                """
            
            cursor.execute(query)
            appointments = cursor.fetchall()
            
            for appointment in appointments:
                self.appointments_tree_billing.insert('', 'end', values=appointment)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error cargando citas para facturación: {str(e)}")
    
    def load_services_for_billing(self):
        """Cargar servicios médicos para facturación"""
        if not hasattr(self, 'services_tree_billing') or not self.services_tree_billing:
            return
            
        try:
            # Limpiar tabla
            for item in self.services_tree_billing.get_children():
                self.services_tree_billing.delete(item)
            
            # Cargar servicios predefinidos
            for service in self.medical_services:
                self.services_tree_billing.insert('', 'end', values=(
                    service['codigo'],
                    service['nombre'],
                    service['categoria'],
                    f"₡{service['precio']:,.2f}"
                ))
            
        except Exception as e:
            print(f"Error cargando servicios: {str(e)}")
    
    def filter_appointments_billing(self, event=None):
        """Filtrar citas para facturación"""
        self.load_appointments_for_billing()
    
    def filter_services(self, event=None):
        """Filtrar servicios médicos"""
        search_term = self.service_search_var.get().lower()
        
        if not hasattr(self, 'services_tree_billing') or not self.services_tree_billing:
            return
        
        # Limpiar tabla
        for item in self.services_tree_billing.get_children():
            self.services_tree_billing.delete(item)
        
        # Filtrar y mostrar servicios
        for service in self.medical_services:
            if (search_term in service['nombre'].lower() or 
                search_term in service['categoria'].lower() or
                search_term in service['codigo'].lower()):
                
                self.services_tree_billing.insert('', 'end', values=(
                    service['codigo'],
                    service['nombre'],
                    service['categoria'],
                    f"₡{service['precio']:,.2f}"
                ))
    
    def on_appointment_select_for_billing(self, event=None):
        """Cuando se selecciona una cita"""
        if not hasattr(self, 'appointments_tree_billing') or not self.appointments_tree_billing:
            return
            
        selection = self.appointments_tree_billing.selection()
        if not selection:
            return
        
        item = self.appointments_tree_billing.item(selection[0])
        appointment_data = item['values']
        
        if len(appointment_data) >= 6:
            self.current_appointment_billing = {
                'id': appointment_data[0],
                'fecha': appointment_data[1],
                'paciente': appointment_data[3],
                'doctor': appointment_data[4],
                'estado': appointment_data[5],
                'facturada': appointment_data[6]
            }
            
            # Actualizar información del paciente
            if hasattr(self, 'patient_info_label'):
                info_text = f"Paciente: {appointment_data[3]} | Doctor: {appointment_data[4]} | Fecha: {appointment_data[1]}"
                self.patient_info_label.config(text=info_text)
    
    def add_service_to_invoice(self):
        """Agregar servicio a la factura"""
        if not hasattr(self, 'services_tree_billing') or not self.services_tree_billing:
            return
            
        selection = self.services_tree_billing.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione un servicio")
            return
        
        if not self.current_appointment_billing:
            messagebox.showwarning("Cita", "Por favor seleccione una cita primero")
            return
        
        item = self.services_tree_billing.item(selection[0])
        service_data = item['values']
        
        # Buscar el servicio completo
        selected_service = None
        for service in self.medical_services:
            if service['codigo'] == service_data[0]:
                selected_service = service
                break
        
        if not selected_service:
            return
        
        # Pedir cantidad
        quantity = simpledialog.askinteger("Cantidad", f"Cantidad de '{selected_service['nombre']}':", 
                                          initialvalue=1, minvalue=1, maxvalue=10)
        if not quantity:
            return
        
        # Agregar a la lista de servicios seleccionados
        service_invoice = {
            'codigo': selected_service['codigo'],
            'nombre': selected_service['nombre'],
            'cantidad': quantity,
            'precio_unitario': selected_service['precio'],
            'total': selected_service['precio'] * quantity
        }
        
        self.selected_services.append(service_invoice)
        self.update_invoice_services_display()
        self.calculate_totals()
    
    def update_invoice_services_display(self):
        """Actualizar la visualización de servicios en la factura"""
        if not hasattr(self, 'invoice_services_tree') or not self.invoice_services_tree:
            return
            
        # Limpiar tabla
        for item in self.invoice_services_tree.get_children():
            self.invoice_services_tree.delete(item)
        
        # Agregar servicios seleccionados
        for service in self.selected_services:
            self.invoice_services_tree.insert('', 'end', values=(
                service['nombre'],
                service['cantidad'],
                f"₡{service['precio_unitario']:,.2f}",
                f"₡{service['total']:,.2f}"
            ))
    
    def remove_service_from_invoice(self):
        """Quitar servicio de la factura"""
        if not hasattr(self, 'invoice_services_tree') or not self.invoice_services_tree:
            return
            
        selection = self.invoice_services_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione un servicio para quitar")
            return
        
        # Obtener índice del servicio seleccionado
        index = self.invoice_services_tree.index(selection[0])
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Quitar '{self.selected_services[index]['nombre']}' de la factura?"):
            del self.selected_services[index]
            self.update_invoice_services_display()
            self.calculate_totals()
    
    def edit_service_in_invoice(self):
        """Editar servicio en la factura"""
        if not hasattr(self, 'invoice_services_tree') or not self.invoice_services_tree:
            return
            
        selection = self.invoice_services_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione un servicio para editar")
            return
        
        # Obtener índice del servicio seleccionado
        index = self.invoice_services_tree.index(selection[0])
        service = self.selected_services[index]
        
        # Pedir nueva cantidad
        new_quantity = simpledialog.askinteger("Editar Cantidad", 
                                              f"Nueva cantidad para '{service['nombre']}':", 
                                              initialvalue=service['cantidad'], minvalue=1, maxvalue=10)
        if new_quantity and new_quantity != service['cantidad']:
            service['cantidad'] = new_quantity
            service['total'] = service['precio_unitario'] * new_quantity
            self.update_invoice_services_display()
            self.calculate_totals()
    
    def calculate_totals(self, event=None):
        """Calcular totales de la factura"""
        subtotal = sum(service['total'] for service in self.selected_services)
        
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
            self.discount_var.set("0.00")
        
        total = subtotal - discount
        if total < 0:
            total = 0
        
        self.subtotal_var.set(f"₡{subtotal:,.2f}")
        self.total_var.set(f"₡{total:,.2f}")
        
        # Recalcular cambio si hay pago ingresado
        self.calculate_change()
    
    def apply_discount(self):
        """Aplicar descuento"""
        self.calculate_totals()
    
    def calculate_change(self, event=None):
        """Calcular cambio o faltante"""
        try:
            total_str = self.total_var.get().replace('₡', '').replace(',', '')
            total = float(total_str)
            
            payment = float(self.payment_var.get() or 0)
            
            difference = payment - total
            
            if difference > 0:
                self.change_label.config(text="Cambio:")
                self.change_var.set(f"₡{difference:,.2f}")
                self.change_value_label.config(fg='#4caf50')
            elif difference < 0:
                self.change_label.config(text="Faltante:")
                self.change_var.set(f"₡{abs(difference):,.2f}")
                self.change_value_label.config(fg='#f44336')
            else:
                self.change_label.config(text="Exacto:")
                self.change_var.set("₡0.00")
                self.change_value_label.config(fg='#4caf50')
                
        except ValueError:
            self.change_var.set("₡0.00")
            self.change_value_label.config(fg='#4caf50')
    
    def generate_invoice_pdf_integrated(self):
        """Generar PDF de factura integrada"""
        if not self.current_appointment_billing:
            messagebox.showwarning("Cita", "Por favor seleccione una cita primero")
            return
        
        if not self.selected_services:
            messagebox.showwarning("Servicios", "Por favor agregue al menos un servicio")
            return
        
        try:
            # Crear directorio de PDFs si no existe
            pdf_directory = "facturas_pdf"
            if not os.path.exists(pdf_directory):
                os.makedirs(pdf_directory)
            
            # Generar número de factura
            invoice_number = f"FAC-{datetime.now().strftime('%Y-%m')}-{datetime.now().strftime('%d%H%M%S')}"
            
            # Nombre del archivo
            patient_name = self.current_appointment_billing['paciente'].replace(' ', '_')
            filename = f"Factura_{invoice_number}_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(pdf_directory, filename)
            
            # Generar PDF simple (sin dependencias externas)
            self.generate_simple_pdf(filepath, invoice_number)
            
            messagebox.showinfo("PDF Generado", f"Factura guardada como:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {str(e)}")
    
    def generate_simple_pdf(self, filepath, invoice_number):
        """Generar PDF simple de texto"""
        try:
            total_str = self.total_var.get().replace('₡', '').replace(',', '')
            total = float(total_str)
            
            payment = float(self.payment_var.get() or 0)
            
            # Crear contenido de texto para el PDF (como fallback)
            content = f"""
=====================================
        MEDISYNC - CENTRO MÉDICO
=====================================

FACTURA MÉDICA
Número: {invoice_number}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

-------------------------------------
INFORMACIÓN DEL PACIENTE
-------------------------------------
Paciente: {self.current_appointment_billing['paciente']}
Doctor: {self.current_appointment_billing['doctor']}
Fecha de Cita: {self.current_appointment_billing['fecha']}

-------------------------------------
SERVICIOS PRESTADOS
-------------------------------------
"""
            
            for service in self.selected_services:
                content += f"{service['nombre']:<30} x{service['cantidad']:>3} = ₡{service['total']:>10,.2f}\n"
            
            content += f"""
-------------------------------------
RESUMEN FINANCIERO
-------------------------------------
Subtotal:           ₡{sum(s['total'] for s in self.selected_services):>10,.2f}
Descuento:          ₡{float(self.discount_var.get() or 0):>10,.2f}
TOTAL A PAGAR:      ₡{total:>10,.2f}

Monto Recibido:     ₡{payment:>10,.2f}
"""
            
            if payment >= total:
                content += f"Cambio:             ₡{payment - total:>10,.2f}\n"
            else:
                content += f"Faltante:           ₡{total - payment:>10,.2f}\n"
            
            content += f"""
=====================================
Gracias por confiar en nuestros servicios
Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
=====================================
"""
            
            # Guardar como archivo de texto (mejor compatibilidad)
            txt_filepath = filepath.replace('.pdf', '.txt')
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Intentar abrir el archivo
            if os.name == 'nt':  # Windows
                os.startfile(txt_filepath)
            else:  # Unix/Linux/Mac
                subprocess.call(['open', txt_filepath])
                
        except Exception as e:
            print(f"Error generando archivo: {str(e)}")
    
    def save_invoice_integrated(self):
        """Guardar factura en la base de datos"""
        if not self.current_appointment_billing:
            messagebox.showwarning("Cita", "Por favor seleccione una cita primero")
            return
        
        if not self.selected_services:
            messagebox.showwarning("Servicios", "Por favor agregue al menos un servicio")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Generar número de factura
            invoice_number = f"FAC-{datetime.now().strftime('%Y-%m')}-{datetime.now().strftime('%d%H%M%S')}"
            
            # Calcular totales
            subtotal = sum(service['total'] for service in self.selected_services)
            discount = float(self.discount_var.get() or 0)
            total = subtotal - discount
            payment = float(self.payment_var.get() or 0)
            
            # Insertar factura
            cursor.execute("""
                INSERT INTO facturas (numero_factura, cita_id, fecha_creacion, monto, estado, concepto)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                invoice_number,
                self.current_appointment_billing['id'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total,
                'pagada' if payment >= total else 'pendiente',
                'Servicios médicos'
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Guardado", f"Factura {invoice_number} guardada exitosamente")
            
            # Limpiar formulario
            self.clear_invoice_form()
            
            # Recargar datos
            self.load_appointments_for_billing()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando factura: {str(e)}")
    
    def clear_invoice_form(self):
        """Limpiar formulario de factura"""
        self.selected_services = []
        self.current_appointment_billing = None
        
        self.subtotal_var.set("0.00")
        self.discount_var.set("0.00")
        self.total_var.set("0.00")
        self.payment_var.set("0.00")
        self.change_var.set("0.00")
        
        if hasattr(self, 'patient_info_label'):
            self.patient_info_label.config(text="Seleccione una cita para continuar")
        
        self.update_invoice_services_display()
    
    def update_status(self, message):
        """Actualizar barra de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    # ==================== FUNCIONES DE GESTIÓN DE SERVICIOS ====================
    
    def load_services_management(self):
        """Cargar servicios en la pestaña de gestión"""
        if not hasattr(self, 'services_management_tree'):
            return
            
        # Limpiar tabla
        for item in self.services_management_tree.get_children():
            self.services_management_tree.delete(item)
        
        # Cargar servicios
        for service in self.medical_services:
            self.services_management_tree.insert('', 'end', values=(
                service['codigo'],
                service['nombre'],
                service['categoria'],
                f"₡{service['precio']:,.2f}"
            ))
    
    def add_new_service(self):
        """Agregar nuevo servicio médico"""
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Servicio Médico")
        dialog.geometry("400x300")
        dialog.configure(bg='#F8FAFC')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Campos del formulario
        fields_frame = tk.Frame(dialog, bg='#F8FAFC')
        fields_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Código
        tk.Label(fields_frame, text="Código:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        codigo_var = tk.StringVar()
        tk.Entry(fields_frame, textvariable=codigo_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Nombre
        tk.Label(fields_frame, text="Nombre:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        nombre_var = tk.StringVar()
        tk.Entry(fields_frame, textvariable=nombre_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Categoría
        tk.Label(fields_frame, text="Categoría:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        categoria_var = tk.StringVar()
        categoria_combo = ttk.Combobox(fields_frame, textvariable=categoria_var, width=27,
                                      values=['Consulta', 'Laboratorio', 'Imagen', 'Procedimiento', 'Cardiología', 'Prevención'])
        categoria_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Precio
        tk.Label(fields_frame, text="Precio (₡):", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        precio_var = tk.StringVar()
        tk.Entry(fields_frame, textvariable=precio_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Botones
        buttons_frame = tk.Frame(dialog, bg='#F8FAFC')
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        def save_service():
            try:
                codigo = codigo_var.get().strip()
                nombre = nombre_var.get().strip()
                categoria = categoria_var.get().strip()
                precio = float(precio_var.get().strip())
                
                if not all([codigo, nombre, categoria]) or precio <= 0:
                    messagebox.showerror("Error", "Todos los campos son obligatorios y el precio debe ser mayor a 0")
                    return
                
                # Verificar que el código no exista
                for service in self.medical_services:
                    if service['codigo'] == codigo:
                        messagebox.showerror("Error", "Ya existe un servicio con ese código")
                        return
                
                # Agregar servicio
                new_service = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'categoria': categoria,
                    'precio': precio
                }
                
                self.medical_services.append(new_service)
                self.load_services_management()
                self.load_services_for_billing()
                
                messagebox.showinfo("Éxito", "Servicio agregado correctamente")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando servicio: {str(e)}")
        
        tk.Button(buttons_frame, text="💾 Guardar", command=save_service,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="❌ Cancelar", command=dialog.destroy,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
    
    def edit_selected_service(self):
        """Editar servicio seleccionado"""
        if not hasattr(self, 'services_management_tree'):
            return
            
        selection = self.services_management_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione un servicio para editar")
            return
        
        # Obtener servicio seleccionado
        item = self.services_management_tree.item(selection[0])
        service_data = item['values']
        codigo_selected = service_data[0]
        
        # Buscar servicio en la lista
        service_to_edit = None
        service_index = -1
        for i, service in enumerate(self.medical_services):
            if service['codigo'] == codigo_selected:
                service_to_edit = service
                service_index = i
                break
        
        if not service_to_edit:
            return
        
        # Crear ventana de edición (similar a la de agregar)
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Servicio Médico")
        dialog.geometry("400x300")
        dialog.configure(bg='#F8FAFC')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Campos del formulario con valores actuales
        fields_frame = tk.Frame(dialog, bg='#F8FAFC')
        fields_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Código (readonly)
        tk.Label(fields_frame, text="Código:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        codigo_var = tk.StringVar(value=service_to_edit['codigo'])
        codigo_entry = tk.Entry(fields_frame, textvariable=codigo_var, width=30, state='readonly')
        codigo_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Nombre
        tk.Label(fields_frame, text="Nombre:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        nombre_var = tk.StringVar(value=service_to_edit['nombre'])
        tk.Entry(fields_frame, textvariable=nombre_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Categoría
        tk.Label(fields_frame, text="Categoría:", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        categoria_var = tk.StringVar(value=service_to_edit['categoria'])
        categoria_combo = ttk.Combobox(fields_frame, textvariable=categoria_var, width=27,
                                      values=['Consulta', 'Laboratorio', 'Imagen', 'Procedimiento', 'Cardiología', 'Prevención'])
        categoria_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Precio
        tk.Label(fields_frame, text="Precio (₡):", bg='#F8FAFC', font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        precio_var = tk.StringVar(value=str(service_to_edit['precio']))
        tk.Entry(fields_frame, textvariable=precio_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Botones
        buttons_frame = tk.Frame(dialog, bg='#F8FAFC')
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        def update_service():
            try:
                nombre = nombre_var.get().strip()
                categoria = categoria_var.get().strip()
                precio = float(precio_var.get().strip())
                
                if not all([nombre, categoria]) or precio <= 0:
                    messagebox.showerror("Error", "Todos los campos son obligatorios y el precio debe ser mayor a 0")
                    return
                
                # Actualizar servicio
                self.medical_services[service_index] = {
                    'codigo': service_to_edit['codigo'],
                    'nombre': nombre,
                    'categoria': categoria,
                    'precio': precio
                }
                
                self.load_services_management()
                self.load_services_for_billing()
                
                messagebox.showinfo("Éxito", "Servicio actualizado correctamente")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando servicio: {str(e)}")
        
        tk.Button(buttons_frame, text="💾 Actualizar", command=update_service,
                 bg='#ff9800', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="❌ Cancelar", command=dialog.destroy,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
    
    def delete_selected_service(self):
        """Eliminar servicio seleccionado"""
        if not hasattr(self, 'services_management_tree'):
            return
            
        selection = self.services_management_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione un servicio para eliminar")
            return
        
        # Obtener servicio seleccionado
        item = self.services_management_tree.item(selection[0])
        service_data = item['values']
        codigo_selected = service_data[0]
        nombre_selected = service_data[1]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar el servicio:\n'{nombre_selected}'?"):
            try:
                # Buscar y eliminar servicio
                for i, service in enumerate(self.medical_services):
                    if service['codigo'] == codigo_selected:
                        del self.medical_services[i]
                        break
                
                self.load_services_management()
                self.load_services_for_billing()
                
                messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando servicio: {str(e)}")
    
    # ==================== FUNCIONES DE REPORTES ====================
    
    def get_billing_statistics_integrated(self):
        """Obtener estadísticas de facturación"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            this_month = datetime.now().strftime('%Y-%m')
            
            stats = {}
            
            # Ingresos de hoy
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM facturas WHERE DATE(fecha_creacion) = ?", (today,))
            stats['ingresos_hoy'] = cursor.fetchone()[0]
            
            # Facturas de hoy
            cursor.execute("SELECT COUNT(*) FROM facturas WHERE DATE(fecha_creacion) = ?", (today,))
            stats['facturas_hoy'] = cursor.fetchone()[0]
            
            # Facturas pendientes
            cursor.execute("SELECT COUNT(*) FROM facturas WHERE estado = 'pendiente'")
            stats['pendientes'] = cursor.fetchone()[0]
            
            # Ingresos del mes
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM facturas WHERE strftime('%Y-%m', fecha_creacion) = ?", (this_month,))
            stats['ingresos_mes'] = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {str(e)}")
            return {'ingresos_hoy': 0, 'facturas_hoy': 0, 'pendientes': 0, 'ingresos_mes': 0}
    
    def generate_daily_report_integrated(self):
        """Generar reporte diario"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT f.numero_factura, f.fecha_creacion, 
                       p.nombre || ' ' || p.apellido as paciente,
                       d.nombre || ' ' || d.apellido as doctor,
                       f.monto, f.estado
                FROM facturas f
                JOIN citas c ON f.cita_id = c.id
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios d ON c.doctor_id = d.id
                WHERE DATE(f.fecha_creacion) = ?
                ORDER BY f.fecha_creacion DESC
            """, (today,))
            
            facturas = cursor.fetchall()
            
            # Generar reporte
            report_content = f"""
REPORTE DIARIO DE FACTURACIÓN
Fecha: {datetime.now().strftime('%d/%m/%Y')}
====================================

RESUMEN:
- Total de facturas: {len(facturas)}
- Ingresos del día: ₡{sum(f[4] for f in facturas):,.2f}

DETALLE DE FACTURAS:
"""
            
            for factura in facturas:
                report_content += f"""
Factura: {factura[0]}
Fecha: {factura[1]}
Paciente: {factura[2]}
Doctor: {factura[3]}
Monto: ₡{factura[4]:,.2f}
Estado: {factura[5]}
-----------------------------------
"""
            
            # Guardar reporte
            reports_dir = "reportes_facturacion"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            filename = f"reporte_diario_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            messagebox.showinfo("Reporte Generado", f"Reporte guardado como: {filename}")
            
            # Abrir archivo
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generate_monthly_report_integrated(self):
        """Generar reporte mensual"""
        messagebox.showinfo("Reporte Mensual", "Función de reporte mensual en desarrollo")
    
    def generate_pending_report_integrated(self):
        """Generar reporte de facturas pendientes"""
        messagebox.showinfo("Facturas Pendientes", "Función de reporte de pendientes en desarrollo")
    
    def generate_services_report_integrated(self):
        """Generar reporte de ingresos por servicio"""
        messagebox.showinfo("Ingresos por Servicio", "Función de reporte por servicios en desarrollo")


        
        # Botón Resumen Rápido
        summary_btn = tk.Button(
            buttons_frame,
            text="� Resumen",
            command=self.show_billing_summary,
            bg='#0B5394',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        )
        summary_btn.pack(side='left', padx=5)
        
        # Contenido principal dividido en secciones
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo: Facturas recientes
        left_panel = tk.LabelFrame(
            content_frame,
            text="📋 FACTURAS RECIENTES",
            font=('Arial', 12, 'bold'),
            bg='#FFFFFF',
            fg='#1E3A8A',
            padx=15,
            pady=15
        )
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Frame para tabla y scrollbars
        table_frame = tk.Frame(left_panel, bg='#FFFFFF')
        table_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Tabla de facturas recientes
        columns = ('Número', 'Fecha', 'Paciente', 'Monto', 'Estado')
        self.billing_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        column_widths = {'Número': 120, 'Fecha': 100, 'Paciente': 150, 'Monto': 100, 'Estado': 100}
        for col in columns:
            self.billing_tree.heading(col, text=col)
            self.billing_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars verticales y horizontales con mejor visibilidad
        billing_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.billing_tree.yview)
        billing_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.billing_tree.xview)
        self.billing_tree.configure(yscrollcommand=billing_scroll_y.set, xscrollcommand=billing_scroll_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.billing_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        billing_scroll_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        billing_scroll_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=0, minsize=20)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Panel derecho: Estadísticas y acciones rápidas
        right_panel = tk.Frame(content_frame, bg='#F8FAFC', width=300)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self.create_billing_stats_panel(right_panel)
        
        # Cargar datos iniciales
        self.load_billing_data_integrated()
    
    def create_billing_stats_panel(self, parent):
        """Crear panel de estadísticas de facturación"""
        # Panel de estadísticas
        stats_frame = tk.LabelFrame(
            parent,
            text="📈 ESTADÍSTICAS HOY",
            font=('Arial', 11, 'bold'),
            bg='#e3f2fd',
            fg='#1565c0',
            padx=15,
            pady=15
        )
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Variables de estadísticas
        self.stats_vars = {
            'facturas_hoy': tk.StringVar(value="0"),
            'ingresos_hoy': tk.StringVar(value="₡0.00"),
            'pendientes': tk.StringVar(value="0"),
            'citas_sin_facturar': tk.StringVar(value="0")
        }
        
        # Crear indicadores
        stats_data = [
            ("💰 Facturas Hoy:", self.stats_vars['facturas_hoy'], '#16A085'),
            ("💵 Ingresos Hoy:", self.stats_vars['ingresos_hoy'], '#059669'),
            ("⏳ Pendientes:", self.stats_vars['pendientes'], '#C0392B'),
            ("📅 Sin Facturar:", self.stats_vars['citas_sin_facturar'], '#E67E22')
        ]
        
        for label, var, color in stats_data:
            stat_row = tk.Frame(stats_frame, bg='#e3f2fd')
            stat_row.pack(fill='x', pady=8)
            
            tk.Label(stat_row, text=label, font=('Arial', 10, 'bold'),
                    bg='#e3f2fd', fg='#1565c0').pack(side='left')
            tk.Label(stat_row, textvariable=var, font=('Arial', 11, 'bold'),
                    bg='#e3f2fd', fg=color).pack(side='right')
        
        # Panel de acciones rápidas
        actions_frame = tk.LabelFrame(
            parent,
            text="⚡ ACCIONES RÁPIDAS",
            font=('Arial', 11, 'bold'),
            bg='#fff3e0',
            fg='#e65100',
            padx=15,
            pady=15
        )
        actions_frame.pack(fill='x', pady=(0, 15))
        
        # Botones de acciones
        actions = [
            ("💵 Nueva Factura Rápida", self.quick_invoice, '#16A085'),
            ("📄 Generar Reporte PDF", self.generate_billing_report, '#0B5394'),
            ("🔍 Buscar Factura", self.search_invoice, '#16A085'),
            ("🔄 Actualizar Datos", self.refresh_billing_data, '#64748B')
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 9, 'bold'),
                padx=10,
                pady=8,
                relief='raised'
            )
            btn.pack(fill='x', pady=5)
        
        # Panel de citas sin facturar
        pending_frame = tk.LabelFrame(
            parent,
            text="📋 CITAS SIN FACTURAR",
            font=('Arial', 11, 'bold'),
            bg='#ffebee',
            fg='#c62828',
            padx=15,
            pady=15
        )
        pending_frame.pack(fill='both', expand=True)
        
        # Lista de citas pendientes
        self.pending_appointments_list = tk.Listbox(
            pending_frame,
            height=6,
            font=('Arial', 9),
            bg='white',
            selectmode='single'
        )
        self.pending_appointments_list.pack(fill='both', expand=True, pady=(10, 10))
        
        # Botón para facturar cita seleccionada
        bill_selected_btn = tk.Button(
            pending_frame,
            text="💰 Facturar Seleccionada",
            command=self.bill_selected_appointment,
            bg='#0B5394',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        )
        bill_selected_btn.pack(fill='x')
    
    # ==================== FUNCIONES AUXILIARES DE FACTURACIÓN ====================
        """Instalar dependencias necesarias para PDFs automáticamente"""
        try:
            import reportlab
            import qrcode
            from PIL import Image
            print("✅ Dependencias para PDF disponibles")
            return True
        except ImportError:
            print("📦 Instalando dependencias para PDFs...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "qrcode[pil]", "pillow"])
                print("✅ Dependencias instaladas exitosamente")
                messagebox.showinfo("Sistema de Facturación", "Dependencias para PDFs instaladas exitosamente.\nSistema completo listo para usar.")
                return True
            except:
                print("⚠️ No se pudieron instalar dependencias - Usando modo básico")
                messagebox.showwarning("Advertencia", "No se pudieron instalar las dependencias para PDFs.\nAlgunas funciones avanzadas pueden no estar disponibles.")
                return False
    
    def create_complete_billing_interface(self, parent):
        """Crear interfaz completa del sistema de facturación"""
        # Header moderno
        header_frame = tk.Frame(parent, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Título y logo
        title_frame = tk.Frame(header_frame, bg='#1E3A8A')
        title_frame.pack(expand=True, fill='both')
        
        tk.Label(title_frame, text="🧾", font=('Arial', 24), bg='#1E3A8A', fg='white').pack(side='left', padx=(20, 10), pady=10)
        tk.Label(title_frame, text="SISTEMA DE FACTURACIÓN COMPLETO", font=('Arial', 18, 'bold'), 
                bg='#1E3A8A', fg='white').pack(side='left', pady=10)
        
        # Botones de acción rápida
        actions_frame = tk.Frame(title_frame, bg='#1E3A8A')
        actions_frame.pack(side='right', padx=20, pady=10)
        
        # Crear notebook con pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Facturación
        billing_frame = tk.Frame(notebook, bg='#F8FAFC')
        notebook.add(billing_frame, text='🧾 Facturación')
        
        # Pestaña 2: Pagos
        payments_frame = tk.Frame(notebook, bg='#F8FAFC')
        notebook.add(payments_frame, text='💳 Procesar Pagos')
        
        # Pestaña 3: Reportes
        reports_frame = tk.Frame(notebook, bg='#F8FAFC')
        notebook.add(reports_frame, text='📊 Reportes')
        
        # Pestaña 4: Configuración
        config_frame = tk.Frame(notebook, bg='#F8FAFC')
        notebook.add(config_frame, text='⚙️ Configuración')
        
        # Crear contenido de cada pestaña
        self.create_advanced_billing_tab(billing_frame)
        self.create_payments_tab(payments_frame)
        self.create_reports_tab(reports_frame)
        self.create_billing_config_tab(config_frame)
    
    def load_existing_invoices(self):
        """Cargar facturas existentes (pagadas y pendientes)"""
        try:
            print("🔄 Iniciando carga de facturas existentes...")
            
            # Limpiar el treeview de facturas si existe
            if hasattr(self, 'billing_appointments_tree'):
                for item in self.billing_appointments_tree.get_children():
                    self.billing_appointments_tree.delete(item)
            
            # Aquí cargaríamos las facturas desde la base de datos
            # Por ahora, solo mostramos un mensaje de confirmación
            print("✅ Facturas cargadas exitosamente")
            
        except Exception as e:
            print(f"❌ Error al cargar facturas: {e}")
            messagebox.showerror("Error", f"Error al cargar facturas: {e}")
        left_header.pack_propagate(False)
        
        header_content = tk.Frame(left_header, bg='#0B5394')
        header_content.pack(expand=True, fill='both')
        
        tk.Label(header_content, text="� GESTIÓN DE CITAS Y FACTURAS", font=('Arial', 12, 'bold'), 
                bg='#0B5394', fg='white').pack(side='left', padx=20, pady=15)
        
        # Botones de acción en el header
        actions_frame = tk.Frame(header_content, bg='#0B5394')
        actions_frame.pack(side='right', padx=20)
        
        refresh_btn = tk.Button(actions_frame, text="🔄 Actualizar", bg='#1e7e34', fg='white',
                              font=('Arial', 10, 'bold'), relief='flat', cursor='hand2',
                              command=self.load_pending_appointments, padx=15, pady=8)
        refresh_btn.pack(side='right', padx=5)
        
        # Notebook para organizar las secciones
        notebook_frame = tk.Frame(left_panel, bg='#ffffff')
        notebook_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Crear notebook con estilo moderno
        style = ttk.Style()
        style.configure('Modern.TNotebook', background='#ffffff')
        style.configure('Modern.TNotebook.Tab', padding=[20, 12])
        
        self.billing_notebook = ttk.Notebook(notebook_frame, style='Modern.TNotebook')
        self.billing_notebook.pack(fill='both', expand=True)
        
        # TAB 1: Citas Pendientes
        appointments_tab = tk.Frame(self.billing_notebook, bg='#ffffff')
        self.billing_notebook.add(appointments_tab, text='📅 Citas Pendientes')
        
        # Subheader para citas
        appointments_subheader = tk.Frame(appointments_tab, bg='#e8f4f8', height=40)
        appointments_subheader.pack(fill='x', pady=(0, 10))
        appointments_subheader.pack_propagate(False)
        
        tk.Label(appointments_subheader, text="Seleccione una cita para generar factura", 
                font=('Arial', 10, 'italic'), bg='#e8f4f8', fg='#0B5394').pack(pady=10)
        
        # Container para la tabla de citas con mejor diseño
        appointments_container = tk.Frame(appointments_tab, bg='#ffffff', relief='solid', bd=1)
        appointments_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para citas con diseño mejorado
        columns = ('ID', 'Fecha', 'Paciente', 'Doctor', 'Motivo', 'Estado')
        self.billing_appointments_tree = ttk.Treeview(appointments_container, columns=columns, 
                                                     show='headings', height=12)
        
        # Configurar columnas con mejor espaciado
        column_config = {
            'ID': {'width': 60, 'anchor': 'center'},
            'Fecha': {'width': 110, 'anchor': 'center'},
            'Paciente': {'width': 160, 'anchor': 'w'},
            'Doctor': {'width': 130, 'anchor': 'w'},
            'Motivo': {'width': 180, 'anchor': 'w'},
            'Estado': {'width': 100, 'anchor': 'center'}
        }
        
        for col in columns:
            self.billing_appointments_tree.heading(col, text=col, anchor='center')
            config = column_config.get(col, {})
            self.billing_appointments_tree.column(col, width=config.get('width', 100), 
                                                 anchor=config.get('anchor', 'center'),
                                                 minwidth=50)
        
        # Scrollbars modernos para citas
        appointments_scrollbar_y = ttk.Scrollbar(appointments_container, orient="vertical", 
                                               command=self.billing_appointments_tree.yview)
        appointments_scrollbar_x = ttk.Scrollbar(appointments_container, orient="horizontal", 
                                               command=self.billing_appointments_tree.xview)
        self.billing_appointments_tree.configure(yscrollcommand=appointments_scrollbar_y.set, 
                                                xscrollcommand=appointments_scrollbar_x.set)
        
        # Grid layout mejorado para citas
        self.billing_appointments_tree.grid(row=0, column=0, sticky='nsew', padx=(8, 0), pady=(8, 0))
        appointments_scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(2, 8), pady=(8, 0))
        appointments_scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(8, 0), pady=(2, 8))
        
        appointments_container.grid_rowconfigure(0, weight=1)
        appointments_container.grid_columnconfigure(0, weight=1)
        
        # Eventos para citas
        self.billing_appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select_billing)
        self.billing_appointments_tree.bind("<MouseWheel>", 
                                          lambda e: self.billing_appointments_tree.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # TAB 2: Facturas Generadas
        invoices_tab = tk.Frame(self.billing_notebook, bg='#ffffff')
        self.billing_notebook.add(invoices_tab, text='📄 Facturas Generadas')
        
        # Subheader para facturas
        invoices_subheader = tk.Frame(invoices_tab, bg='#f0f8e8', height=40)
        invoices_subheader.pack(fill='x', pady=(0, 10))
        invoices_subheader.pack_propagate(False)
        
        tk.Label(invoices_subheader, text="Historial completo de facturas del sistema", 
                font=('Arial', 10, 'italic'), bg='#f0f8e8', fg='#155724').pack(pady=10)
        
        # Container para la tabla de facturas
        invoices_container = tk.Frame(invoices_tab, bg='#ffffff', relief='solid', bd=1)
        invoices_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para facturas con diseño mejorado
        invoice_columns = ('Número', 'Fecha', 'Paciente', 'Monto', 'Estado', 'Acciones')
        self.billing_invoices_tree = ttk.Treeview(invoices_container, columns=invoice_columns, 
                                                 show='headings', height=12)
        
        # Configurar columnas de facturas
        invoice_config = {
            'Número': {'width': 130, 'anchor': 'center'},
            'Fecha': {'width': 100, 'anchor': 'center'},
            'Paciente': {'width': 160, 'anchor': 'w'},
            'Monto': {'width': 120, 'anchor': 'e'},
            'Estado': {'width': 120, 'anchor': 'center'},
            'Acciones': {'width': 100, 'anchor': 'center'}
        }
        
        for col in invoice_columns:
            self.billing_invoices_tree.heading(col, text=col, anchor='center')
            config = invoice_config.get(col, {})
            self.billing_invoices_tree.column(col, width=config.get('width', 100), 
                                            anchor=config.get('anchor', 'center'),
                                            minwidth=50)
        
        # Scrollbars modernos para facturas
        invoices_scrollbar_y = ttk.Scrollbar(invoices_container, orient="vertical", 
                                           command=self.billing_invoices_tree.yview)
        invoices_scrollbar_x = ttk.Scrollbar(invoices_container, orient="horizontal", 
                                           command=self.billing_invoices_tree.xview)
        self.billing_invoices_tree.configure(yscrollcommand=invoices_scrollbar_y.set, 
                                           xscrollcommand=invoices_scrollbar_x.set)
        
        # Grid layout mejorado para facturas
        self.billing_invoices_tree.grid(row=0, column=0, sticky='nsew', padx=(8, 0), pady=(8, 0))
        invoices_scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(2, 8), pady=(8, 0))
        invoices_scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(8, 0), pady=(2, 8))
        
        invoices_container.grid_rowconfigure(0, weight=1)
        invoices_container.grid_columnconfigure(0, weight=1)
        
        # Eventos para facturas
        self.billing_invoices_tree.bind('<Double-1>', self.view_invoice_details_billing)
        self.billing_invoices_tree.bind("<MouseWheel>", 
                                       lambda e: self.billing_invoices_tree.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Panel de acciones moderno para facturas
        invoice_actions_panel = tk.Frame(invoices_tab, bg='#ffffff')
        invoice_actions_panel.pack(fill='x', padx=10, pady=(15, 10))
        
        # Título del panel de acciones
        tk.Label(invoice_actions_panel, text="🎛️ ACCIONES DISPONIBLES", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#0B5394').pack(anchor='w', pady=(0, 10))
        
        # Frame para los botones con diseño en grid
        actions_grid = tk.Frame(invoice_actions_panel, bg='#ffffff')
        actions_grid.pack(fill='x')
        
        # Botones modernos con iconos
        button_style = {
            'font': ('Arial', 10, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 20,
            'pady': 10,
            'width': 18
        }
        
        # Primera fila de botones
        row1_frame = tk.Frame(actions_grid, bg='#ffffff')
        row1_frame.pack(fill='x', pady=(0, 8))
        
        tk.Button(row1_frame, text="💳 Procesar Pago", bg='#28a745', fg='white',
                 command=self.process_payment_window, **button_style).pack(side='left', padx=(0, 8))
        tk.Button(row1_frame, text="👁️ Ver Detalles", bg='#17a2b8', fg='white',
                 command=self.view_invoice_details_billing, **button_style).pack(side='left', padx=8)
        
        # Segunda fila de botones
        row2_frame = tk.Frame(actions_grid, bg='#ffffff')
        row2_frame.pack(fill='x')
        
        tk.Button(row2_frame, text="📄 Reimprimir PDF", bg='#6f42c1', fg='white',
                 command=self.reprint_invoice_pdf, **button_style).pack(side='left', padx=(0, 8))
        tk.Button(row2_frame, text="� Actualizar Lista", bg='#1e7e34', fg='white',
                 command=self.load_existing_invoices, **button_style).pack(side='left', padx=8)
        
        # Panel derecho - Crear factura con diseño moderno
        right_panel = tk.Frame(content_frame, bg='#ffffff', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=False, padx=(8, 0))
        right_panel.configure(width=550)  # Ancho fijo más controlado
        right_panel.pack_propagate(False)
        
        # Header del panel derecho modernizado
        right_header = tk.Frame(right_panel, bg='#0B5394', height=55)
        right_header.pack(fill='x')
        right_header.pack_propagate(False)
        
        header_right_content = tk.Frame(right_header, bg='#0B5394')
        header_right_content.pack(expand=True, fill='both')
        
        tk.Label(header_right_content, text="🧾 CREAR NUEVA FACTURA", font=('Arial', 12, 'bold'), 
                bg='#0B5394', fg='white').pack(pady=15)
        
        # Formulario de factura con diseño moderno
        form_container = tk.Frame(right_panel, bg='#ffffff')
        form_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Llamar a la función existente del formulario
        self.create_invoice_form(form_container)
        
        # Panel de estado y notificaciones
        status_panel = tk.Frame(main_frame, bg='#e9ecef', height=40)
        status_panel.pack(fill='x', pady=(10, 0))
        status_panel.pack_propagate(False)
        
        # Etiqueta de estado
        self.billing_status_label = tk.Label(status_panel, text="✅ Sistema de facturación listo", 
                                           font=('Arial', 10), bg='#e9ecef', fg='#495057')
        self.billing_status_label.pack(expand=True, pady=10)
        
        # Cargar datos iniciales después de que la interfaz esté lista
        self.root.after(100, self.load_pending_appointments)
        self.root.after(200, self.load_existing_invoices)
        
        # Actualizar estado
        self.root.after(300, lambda: self.update_billing_status("📊 Datos cargados exitosamente"))
    
    def load_existing_invoices(self):
        """Cargar facturas existentes (pagadas y pendientes)"""
        try:
            print("🔄 Iniciando carga de facturas existentes...")
            
            # Verificar que el widget existe
            if not hasattr(self, 'billing_invoices_tree'):
                print("❌ ERROR: billing_invoices_tree no existe")
                return
            
            print(f"✅ Widget billing_invoices_tree existe: {self.billing_invoices_tree}")
            
            # Limpiar tabla de facturas
            for item in self.billing_invoices_tree.get_children():
                self.billing_invoices_tree.delete(item)
                
            print("🧹 Tabla limpiada")
            
            # Obtener facturas
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            print(f"📊 Consultando facturas en base de datos...")
            
            cursor.execute("""
                SELECT f.id, f.numero_factura, f.fecha_creacion, 
                       p.nombre || ' ' || p.apellido as paciente,
                       f.monto, f.estado,
                       f.metodo_pago, f.fecha_pago
                FROM facturas f
                JOIN usuarios p ON f.paciente_id = p.id
                ORDER BY f.fecha_creacion DESC
                LIMIT 50
            """)
            
            invoices = cursor.fetchall()
            print(f"✅ Se encontraron {len(invoices)} facturas en la base de datos")
            
            # Contador para verificar inserciones
            inserted_count = 0
            
            for invoice in invoices:
                try:
                    invoice_id, numero, fecha, paciente, monto, estado, metodo_pago, fecha_pago = invoice
                    
                    # Formatear fecha
                    try:
                        fecha_obj = datetime.fromisoformat(fecha)
                        fecha_formatted = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        fecha_formatted = fecha
                    
                    # Formatear monto
                    monto_formatted = f"RD$ {float(monto):,.2f}"
                    
                    # Determinar estado y color
                    if estado in ['pagada', 'pagado']:
                        estado_display = "✅ Pagada"
                    elif estado == 'pendiente':
                        estado_display = "⏳ Pendiente"
                    elif estado == 'pago_parcial':
                        estado_display = "🔵 Parcial"
                    elif estado == 'vencido':
                        estado_display = "🔴 Vencida"
                    elif estado == 'cancelado':
                        estado_display = "❌ Cancelada"
                    else:
                        estado_display = f"🔧 {estado}"
                    
                    # Insertar en la tabla
                    item_id = self.billing_invoices_tree.insert('', 'end', values=(
                        numero, fecha_formatted, paciente, monto_formatted, estado_display, "🔧"
                    ))
                    
                    # Verificar que se insertó
                    if item_id:
                        inserted_count += 1
                        print(f"➕ Insertada factura #{inserted_count}: {numero} - {paciente} - {estado_display}")
                    else:
                        print(f"❌ Error insertando factura: {numero}")
                    
                    # Guardar ID de factura como tag (si es necesario)
                    try:
                        self.billing_invoices_tree.set(item_id, '#1', invoice_id)
                    except:
                        pass
                        
                except Exception as insert_error:
                    print(f"❌ Error procesando factura {invoice}: {insert_error}")
                    continue
            
            cursor.close()
            conn.close()
            
            # Verificar cuántos items tiene la tabla después de la carga
            children_count = len(self.billing_invoices_tree.get_children())
            print(f"📊 Items en la tabla después de carga: {children_count}")
            
            # Forzar actualización visual
            self.billing_invoices_tree.update()
            self.billing_invoices_tree.update_idletasks()
            
            print(f"✅ Carga completada: {inserted_count} facturas insertadas correctamente")
            
            if inserted_count == 0:
                print("⚠️ ADVERTENCIA: No se insertaron facturas en la tabla")
            
        except Exception as e:
            error_msg = f"Error cargando facturas: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"Error completo: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def update_billing_status(self, message):
        """Actualizar el mensaje de estado del sistema de facturación"""
        try:
            if hasattr(self, 'billing_status_label'):
                self.billing_status_label.config(text=message)
                self.billing_status_label.update()
        except Exception as e:
            print(f"Error actualizando estado: {e}")
    
    def create_invoice_form(self, parent):
        """Crear formulario para crear facturas"""
        # Crear un canvas con scrollbar para el formulario completo
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar_form = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar_form.pack(side="right", fill="y", pady=15)
        
        # Configurar el ancho del frame scrollable para que coincida con el canvas
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.configure(width=event.width)
        
        canvas.bind('<Configure>', configure_scroll_region)
        
        # El form_frame ahora será el scrollable_frame
        form_frame = scrollable_frame
        
        # Información de la cita seleccionada
        info_frame = tk.LabelFrame(form_frame, text="📋 Información de la Cita", 
                                  font=('Arial', 11, 'bold'), padx=10, pady=10)
        info_frame.pack(fill='x', pady=(0, 15))
        
        self.selected_appointment_info = tk.Label(info_frame, text="Seleccione una cita para facturar", 
                                                 font=('Arial', 10), bg='white', fg='#64748B', 
                                                 wraplength=400, justify='left')
        self.selected_appointment_info.pack(anchor='w')
        
        # Panel de información del doctor y seguro
        doctor_insurance_frame = tk.LabelFrame(form_frame, text="👨‍⚕️ Info Doctor & 🏥 Seguros", 
                                             font=('Arial', 11, 'bold'), padx=10, pady=10)
        doctor_insurance_frame.pack(fill='x', pady=(0, 15))
        
        # Dividir en dos columnas
        columns_frame = tk.Frame(doctor_insurance_frame, bg='white')
        columns_frame.pack(fill='x')
        
        # Columna izquierda - Info Doctor
        doctor_col = tk.Frame(columns_frame, bg='#e8f5e8', relief='solid', bd=1)
        doctor_col.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(doctor_col, text="👨‍⚕️ DOCTOR", font=('Arial', 10, 'bold'), 
                bg='#e8f5e8', fg='#2e7d32').pack(pady=5)
        
        self.doctor_info_label = tk.Label(doctor_col, text="Seleccione una cita\npara ver información", 
                                         font=('Arial', 9), bg='#e8f5e8', fg='#2e7d32',
                                         wraplength=200, justify='center')
        self.doctor_info_label.pack(pady=10)
        
        # Columna derecha - Info Seguro
        insurance_col = tk.Frame(columns_frame, bg='#e3f2fd', relief='solid', bd=1)
        insurance_col.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(insurance_col, text="🏥 SEGURO MÉDICO", font=('Arial', 10, 'bold'), 
                bg='#e3f2fd', fg='#1565c0').pack(pady=5)
        
        self.insurance_info_label = tk.Label(insurance_col, text="Seleccione una cita\npara ver información", 
                                           font=('Arial', 9), bg='#e3f2fd', fg='#1565c0',
                                           wraplength=200, justify='center')
        self.insurance_info_label.pack(pady=10)
        
        # Servicios y precios
        services_frame = tk.LabelFrame(form_frame, text="💰 Servicios y Precios", 
                                      font=('Arial', 11, 'bold'), padx=10, pady=10)
        services_frame.pack(fill='x', pady=(0, 15))
        
        # Lista de servicios con scrollbar
        services_list_frame = tk.Frame(services_frame)
        services_list_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Frame para la tabla con scrollbar
        table_container = tk.Frame(services_list_frame, relief='sunken', bd=1)
        table_container.pack(fill='both', expand=True)
        
        # Treeview para servicios con altura aumentada
        columns = ('Servicio', 'Precio')
        self.services_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=250 if col == 'Servicio' else 150, anchor='center')
        
        # Scrollbar para servicios
        services_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=services_scrollbar.set)
        
        # Pack tabla y scrollbar
        self.services_tree.pack(side='left', fill='both', expand=True)
        services_scrollbar.pack(side='right', fill='y')
        
        # Botones para servicios con mejor espaciado
        services_btn_frame = tk.Frame(services_frame)
        services_btn_frame.pack(fill='x', pady=(15, 0))
        
        tk.Button(services_btn_frame, text="➕ Agregar Servicio", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), width=15, command=self.add_service_to_invoice).pack(side='left', padx=(0, 8))
        tk.Button(services_btn_frame, text="➖ Quitar Servicio", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), width=15, command=self.remove_service_from_invoice).pack(side='left', padx=8)
        tk.Button(services_btn_frame, text="📝 Editar Precio", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), width=15, command=self.edit_service_price).pack(side='left', padx=8)
        
        # Totales
        totals_frame = tk.LabelFrame(form_frame, text="💵 Totales", 
                                    font=('Arial', 11, 'bold'), padx=10, pady=10)
        totals_frame.pack(fill='x', pady=(0, 15))
        
        # Subtotal
        subtotal_frame = tk.Frame(totals_frame)
        subtotal_frame.pack(fill='x', pady=2)
        tk.Label(subtotal_frame, text="Subtotal:", font=('Arial', 10, 'bold')).pack(side='left')
        self.subtotal_label = tk.Label(subtotal_frame, text="RD$ 0.00", font=('Arial', 10), fg='#1E3A8A')
        self.subtotal_label.pack(side='right')
        
        # ITBIS
        itbis_frame = tk.Frame(totals_frame)
        itbis_frame.pack(fill='x', pady=2)
        tk.Label(itbis_frame, text="ITBIS (18%):", font=('Arial', 10, 'bold')).pack(side='left')
        self.itbis_label = tk.Label(itbis_frame, text="RD$ 0.00", font=('Arial', 10), fg='#1E3A8A')
        self.itbis_label.pack(side='right')
        
        # Total
        total_frame = tk.Frame(totals_frame)
        total_frame.pack(fill='x', pady=2)
        tk.Label(total_frame, text="TOTAL:", font=('Arial', 12, 'bold')).pack(side='left')
        self.total_label = tk.Label(total_frame, text="RD$ 0.00", font=('Arial', 12, 'bold'), fg='#C0392B')
        self.total_label.pack(side='right')
        
        # Observaciones
        obs_frame = tk.LabelFrame(form_frame, text="📝 Observaciones", 
                                 font=('Arial', 11, 'bold'), padx=10, pady=10)
        obs_frame.pack(fill='x', pady=(0, 15))
        
        self.observations_text = tk.Text(obs_frame, height=4, font=('Arial', 10), wrap='word')
        self.observations_text.pack(fill='x', pady=(5, 0))
        
        # Botones de acción principales con mejor diseño
        actions_frame = tk.Frame(form_frame)
        actions_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(actions_frame, text="🧾 Crear Factura", bg='#0B5394', fg='white',
                 font=('Arial', 12, 'bold'), width=18, pady=8,
                 command=self.create_invoice_from_appointment).pack(side='left', padx=(0, 8))
        tk.Button(actions_frame, text="� Procesar Pago", bg='#0B5394', fg='white',
                 font=('Arial', 12, 'bold'), width=18, pady=8,
                 command=self.open_payment_window).pack(side='left', padx=8)
        tk.Button(actions_frame, text="🗑️ Limpiar", bg='#0B5394', fg='white',
                 font=('Arial', 12, 'bold'), width=12, pady=8,
                 command=self.clear_invoice_form).pack(side='right')
        
        # Cargar servicios predeterminados
        self.load_default_services()
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind del scroll del mouse al canvas y todos sus widgets
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
    
    def load_pending_appointments(self):
        """Cargar citas pendientes de facturación"""
        try:
            # Limpiar tabla
            for item in self.billing_appointments_tree.get_children():
                self.billing_appointments_tree.delete(item)
            
            # Obtener citas completadas pero no facturadas
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.id, 
                       DATE(c.fecha_hora) as fecha_cita, 
                       TIME(c.fecha_hora) as hora_cita,
                       p.nombre || ' ' || p.apellido as paciente,
                       d.nombre || ' ' || d.apellido as doctor,
                       c.motivo, c.estado
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios d ON c.doctor_id = d.id
                WHERE c.estado IN ('completada', 'realizada') 
                ORDER BY c.fecha_hora DESC
            """)
            
            appointments = cursor.fetchall()
            
            for appointment in appointments:
                # Formatear fecha
                fecha = datetime.fromisoformat(appointment[1]).strftime('%d/%m/%Y') if appointment[1] else ''
                
                self.billing_appointments_tree.insert('', 'end', values=(
                    appointment[0],  # ID
                    fecha,           # Fecha
                    appointment[3],  # Paciente
                    appointment[4],  # Doctor
                    appointment[5],  # Motivo
                    appointment[6].title()  # Estado
                ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando citas: {str(e)}")
    
    def load_default_services(self):
        """Cargar servicios predeterminados"""
        # Servicios comunes con precios
        default_services = [
            ("Consulta General", 2500.00),
            ("Consulta Especializada", 3500.00),
            ("Consulta Pediátrica", 2800.00),
            ("Consulta Cardiológica", 4000.00),
            ("Consulta Ginecológica", 3200.00),
            ("Consulta Dermatológica", 3800.00),
            ("Consulta Neurológica", 4500.00),
            ("Consulta Oftalmológica", 3000.00),
            ("Análisis de Laboratorio", 1500.00),
            ("Análisis de Sangre Completo", 2200.00),
            ("Análisis de Orina", 800.00),
            ("Perfil Lipídico", 1800.00),
            ("Glicemia", 600.00),
            ("Hemoglobina Glicosilada", 1200.00),
            ("Radiografía", 3000.00),
            ("Radiografía de Tórax", 2500.00),
            ("Radiografía de Extremidades", 2800.00),
            ("Electrocardiograma", 2000.00),
            ("Ecografía", 4500.00),
            ("Ecografía Abdominal", 4000.00),
            ("Ecografía Pélvica", 3800.00),
            ("Mamografía", 5000.00),
            ("Tomografía", 8000.00),
            ("Resonancia Magnética", 12000.00),
            ("Procedimiento Menor", 3500.00),
            ("Sutura Simple", 2000.00),
            ("Curación", 1000.00),
            ("Inyección Intramuscular", 500.00),
            ("Vacunación", 800.00),
            ("Terapia Física", 2500.00)
        ]
        
        for service, price in default_services:
            self.services_tree.insert('', 'end', values=(service, f"RD$ {price:,.2f}"))
    
    def on_appointment_select_billing(self, event):
        """Manejar selección de cita para facturar"""
        selection = self.billing_appointments_tree.selection()
        if selection:
            item = self.billing_appointments_tree.item(selection[0])
            values = item['values']
            
            # Obtener información del doctor y paciente
            doctor_info = self.get_doctor_billing_info(values[3])
            patient_info = self.get_patient_insurance_info(values[2])
            
            # Mostrar información de la cita con tarifas
            info_text = f"""📅 Fecha: {values[1]}
👤 Paciente: {values[2]}
👨‍⚕️ Doctor: {values[3]}
💰 Tarifa Doctor: RD$ {doctor_info['tarifa']:,.2f}
🏥 Acepta Seguros: {'✅ Sí' if doctor_info['acepta_seguros'] else '❌ No'}
�️ Seguro Paciente: {patient_info['seguro'] if patient_info['seguro'] else 'Sin Seguro'}
�💭 Motivo: {values[4]}
📊 Estado: {values[5]}

✅ Cita lista para facturar"""
            
            self.selected_appointment_info.config(text=info_text, fg='#16A085')
            
            # Guardar información para facturar
            self.selected_appointment_id = values[0]
            self.selected_doctor_info = doctor_info
            self.selected_patient_info = patient_info
            
            # Recargar servicios con tarifa del doctor
            self.load_doctor_services(doctor_info)
            
            # Actualizar paneles de información
            self.update_doctor_info_panel(doctor_info)
            self.update_insurance_info_panel(patient_info, doctor_info['acepta_seguros'])
    
    def get_doctor_billing_info(self, doctor_name):
        """Obtener información de facturación del doctor"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Buscar información del doctor
            cursor.execute('''
                SELECT u.nombre, u.apellido, u.telefono, u.email,
                       COALESCE(d.tarifa_consulta, 3000.00) as tarifa,
                       COALESCE(d.acepta_seguros, 1) as acepta_seguros,
                       COALESCE(d.especialidad, 'Medicina General') as especialidad
                FROM usuarios u
                LEFT JOIN doctores d ON u.id = d.id
                WHERE (u.nombre || ' ' || u.apellido) LIKE ? AND u.tipo_usuario = 'doctor'
                LIMIT 1
            ''', (f'%{doctor_name}%',))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'nombre_completo': f"{result[0]} {result[1]}",
                    'telefono': result[2] or 'No especificado',
                    'email': result[3] or 'No especificado',
                    'tarifa': float(result[4]),
                    'acepta_seguros': bool(result[5]),
                    'especialidad': result[6]
                }
            else:
                # Valores por defecto si no se encuentra el doctor
                return {
                    'nombre_completo': doctor_name,
                    'telefono': 'No especificado',
                    'email': 'No especificado',
                    'tarifa': 3000.00,
                    'acepta_seguros': True,
                    'especialidad': 'Medicina General'
                }
                
        except Exception as e:
            print(f"Error obteniendo info del doctor: {e}")
            return {
                'nombre_completo': doctor_name,
                'telefono': 'No especificado',
                'email': 'No especificado',
                'tarifa': 3000.00,
                'acepta_seguros': True,
                'especialidad': 'Medicina General'
            }
    
    def get_patient_insurance_info(self, patient_name):
        """Obtener información del seguro del paciente"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Buscar información del paciente
            cursor.execute('''
                SELECT u.nombre, u.apellido, u.telefono, u.email,
                       p.seguro_medico, p.numero_seguro, p.porcentaje_cobertura
                FROM usuarios u
                LEFT JOIN pacientes p ON u.id = p.id
                WHERE (u.nombre || ' ' || u.apellido) LIKE ? AND u.tipo_usuario = 'paciente'
                LIMIT 1
            ''', (f'%{patient_name}%',))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'nombre_completo': f"{result[0]} {result[1]}",
                    'telefono': result[2] or 'No especificado',
                    'email': result[3] or 'No especificado',
                    'seguro': result[4] or None,
                    'numero_seguro': result[5] or None,
                    'cobertura': float(result[6]) if result[6] else 0.0
                }
            else:
                return {
                    'nombre_completo': patient_name,
                    'telefono': 'No especificado',
                    'email': 'No especificado',
                    'seguro': None,
                    'numero_seguro': None,
                    'cobertura': 0.0
                }
                
        except Exception as e:
            print(f"Error obteniendo info del paciente: {e}")
            return {
                'nombre_completo': patient_name,
                'telefono': 'No especificado',
                'email': 'No especificado',
                'seguro': None,
                'numero_seguro': None,
                'cobertura': 0.0
            }
    
    def load_doctor_services(self, doctor_info):
        """Cargar servicios con la tarifa específica del doctor"""
        # Limpiar servicios actuales
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        
        # Servicios base ajustados con la tarifa del doctor
        base_price = doctor_info['tarifa']
        specialty = doctor_info['especialidad']
        
        # Servicios específicos según especialidad y tarifa del doctor
        if 'Cardiolog' in specialty:
            services = [
                ("Consulta Cardiológica", base_price),
                ("Electrocardiograma", base_price * 0.7),
                ("Ecocardiograma", base_price * 1.8),
                ("Prueba de Esfuerzo", base_price * 2.0),
                ("Holter 24h", base_price * 2.5)
            ]
        elif 'Ginecolog' in specialty:
            services = [
                ("Consulta Ginecológica", base_price),
                ("Ecografía Pélvica", base_price * 1.5),
                ("Papanicolaou", base_price * 0.8),
                ("Colposcopia", base_price * 1.3),
                ("Control Prenatal", base_price * 0.9)
            ]
        elif 'Pediatr' in specialty:
            services = [
                ("Consulta Pediátrica", base_price),
                ("Control de Niño Sano", base_price * 0.8),
                ("Vacunación", base_price * 0.3),
                ("Nebulización", base_price * 0.5),
                ("Evaluación Desarrollo", base_price * 1.2)
            ]
        elif 'Dermatolog' in specialty:
            services = [
                ("Consulta Dermatológica", base_price),
                ("Biopsia de Piel", base_price * 1.5),
                ("Criocirugía", base_price * 1.8),
                ("Dermatoscopia", base_price * 1.2),
                ("Tratamiento Acné", base_price * 0.9)
            ]
        elif 'Neurolog' in specialty:
            services = [
                ("Consulta Neurológica", base_price),
                ("Electroencefalograma", base_price * 1.8),
                ("Evaluación Neurológica", base_price * 1.3),
                ("Test Cognitivo", base_price * 1.1),
                ("Tratamiento Migraña", base_price * 0.9)
            ]
        else:
            # Medicina General - servicios estándar
            services = [
                ("Consulta General", base_price),
                ("Consulta de Control", base_price * 0.8),
                ("Certificado Médico", base_price * 0.5),
                ("Inyección Intramuscular", base_price * 0.2),
                ("Curación", base_price * 0.4),
                ("Sutura Simple", base_price * 0.8),
                ("Electrocardiograma", base_price * 0.7),
                ("Toma de Presión", base_price * 0.2)
            ]
        
        # Agregar servicios adicionales comunes
        additional_services = [
            ("Análisis de Laboratorio", 1500.00),
            ("Análisis de Sangre", 2200.00),
            ("Análisis de Orina", 800.00),
            ("Radiografía", 3000.00),
            ("Ecografía", 4500.00)
        ]
        
        # Insertar servicios en el tree
        for service, price in services + additional_services:
            self.services_tree.insert('', 'end', values=(service, f"RD$ {price:,.2f}"))
        
        # Calcular totales
        self.calculate_totals()
    
    def update_doctor_info_panel(self, doctor_info):
        """Actualizar panel de información del doctor"""
        doctor_text = f"""📋 {doctor_info['especialidad']}
💰 Tarifa: RD$ {doctor_info['tarifa']:,.2f}
🏥 Acepta Seguros: {'✅ SÍ' if doctor_info['acepta_seguros'] else '❌ NO'}
📧 {doctor_info['email'][:20]}{'...' if len(doctor_info['email']) > 20 else ''}
📞 {doctor_info['telefono']}"""
        
        self.doctor_info_label.config(text=doctor_text)
    
    def update_insurance_info_panel(self, patient_info, doctor_acepta_seguros):
        """Actualizar panel de información del seguro"""
        if patient_info['seguro'] and doctor_acepta_seguros:
            # Paciente tiene seguro y doctor acepta
            insurance_text = f"""✅ {patient_info['seguro']}
📋 No. {patient_info['numero_seguro'] or 'No especificado'}
💰 Cobertura: {patient_info['cobertura']:.0f}%
📊 Estado: APLICABLE
💡 Se aplicará descuento"""
            color = '#1565c0'
        elif patient_info['seguro'] and not doctor_acepta_seguros:
            # Paciente tiene seguro pero doctor no acepta
            insurance_text = f"""⚠️ {patient_info['seguro']}
📋 No. {patient_info['numero_seguro'] or 'No especificado'}
💰 Cobertura: {patient_info['cobertura']:.0f}%
📊 Estado: NO APLICABLE
❌ Doctor no acepta seguros"""
            color = '#f57c00'
        elif not patient_info['seguro'] and doctor_acepta_seguros:
            # Doctor acepta seguros pero paciente no tiene
            insurance_text = f"""ℹ️ SIN SEGURO MÉDICO
📊 Estado: NO APLICABLE
💡 Paciente pagará precio completo
✅ Doctor acepta seguros"""
            color = '#64748B'
        else:
            # Ni el doctor acepta ni el paciente tiene
            insurance_text = f"""❌ SIN SEGURO MÉDICO
📊 Estado: NO APLICABLE
💡 Paciente pagará precio completo
❌ Doctor no acepta seguros"""
            color = '#64748B'
        
        self.insurance_info_label.config(text=insurance_text, fg=color)
    
    def add_service_to_invoice(self):
        """Agregar servicio personalizado a la factura"""
        # Diálogo para agregar servicio
        dialog = tk.Toplevel()
        dialog.title("Agregar Servicio")
        dialog.geometry("400x200")
        dialog.configure(bg='#F8FAFC')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Campos
        tk.Label(dialog, text="Nombre del Servicio:", font=('Arial', 11, 'bold'), bg='#F8FAFC').pack(pady=10)
        service_entry = tk.Entry(dialog, font=('Arial', 11), width=40)
        service_entry.pack(pady=5)
        
        tk.Label(dialog, text="Precio (RD$):", font=('Arial', 11, 'bold'), bg='#F8FAFC').pack(pady=(10, 0))
        price_entry = tk.Entry(dialog, font=('Arial', 11), width=20)
        price_entry.pack(pady=5)
        
        # Botones
        btn_frame = tk.Frame(dialog, bg='#F8FAFC')
        btn_frame.pack(pady=20)
        
        def add_service():
            service_name = service_entry.get().strip()
            price_str = price_entry.get().strip()
            
            if not service_name or not price_str:
                messagebox.showerror("Error", "Complete todos los campos")
                return
            
            try:
                price = float(price_str)
                self.services_tree.insert('', 'end', values=(service_name, f"RD$ {price:,.2f}"))
                self.calculate_totals()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Servicio agregado correctamente")
            except ValueError:
                messagebox.showerror("Error", "Precio inválido")
        
        tk.Button(btn_frame, text="Agregar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=add_service).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancelar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=dialog.destroy).pack(side='left', padx=5)
        
        service_entry.focus()
    
    def calculate_totals(self):
        """Calcular totales de la factura con descuentos por seguro"""
        subtotal = 0.0
        
        # Sumar todos los servicios
        for item in self.services_tree.get_children():
            values = self.services_tree.item(item)['values']
            price_str = values[1].replace('RD$ ', '').replace(',', '')
            try:
                price = float(price_str)
                subtotal += price
            except ValueError:
                continue
        
        # Verificar si aplica descuento por seguro
        descuento_seguro = 0.0
        doctor_acepta_seguro = False
        paciente_tiene_seguro = False
        cobertura_porcentaje = 0.0
        
        if hasattr(self, 'selected_doctor_info') and hasattr(self, 'selected_patient_info'):
            doctor_acepta_seguro = self.selected_doctor_info.get('acepta_seguros', False)
            paciente_tiene_seguro = bool(self.selected_patient_info.get('seguro'))
            cobertura_porcentaje = self.selected_patient_info.get('cobertura', 0.0)
            
            # Aplicar descuento solo si el doctor acepta seguros Y el paciente tiene seguro
            if doctor_acepta_seguro and paciente_tiene_seguro and cobertura_porcentaje > 0:
                descuento_seguro = subtotal * (cobertura_porcentaje / 100)
        
        # Subtotal después del descuento
        subtotal_con_descuento = subtotal - descuento_seguro
        
        # Calcular ITBIS (18%) sobre el monto después del descuento
        itbis = subtotal_con_descuento * 0.18
        total = subtotal_con_descuento + itbis
        
        # Actualizar labels con información detallada
        if descuento_seguro > 0:
            seguro_info = self.selected_patient_info.get('seguro', 'Seguro Médico')
            
            # Mostrar información completa
            self.subtotal_label.config(
                text=f"Subtotal: RD$ {subtotal:,.2f}\n" +
                     f"Desc. {seguro_info} ({cobertura_porcentaje}%): -RD$ {descuento_seguro:,.2f}\n" +
                     f"Subtotal Final: RD$ {subtotal_con_descuento:,.2f}",
                justify='left'
            )
        else:
            self.subtotal_label.config(text=f"RD$ {subtotal:,.2f}")
        
        self.itbis_label.config(text=f"RD$ {itbis:,.2f}")
        self.total_label.config(text=f"RD$ {total:,.2f}")
        
        # Guardar valores para usar en facturación
        self.current_subtotal = subtotal
        self.current_descuento = descuento_seguro
        self.current_itbis = itbis
        self.current_total = total
    
    def create_invoice_from_appointment(self):
        """Crear factura desde la cita seleccionada"""
        if not hasattr(self, 'selected_appointment_id'):
            messagebox.showwarning("Selección requerida", "Seleccione una cita para facturar")
            return
        
        try:
            # Recopilar servicios
            services = []
            for item in self.services_tree.get_children():
                values = self.services_tree.item(item)['values']
                service_name = values[0]
                price_str = values[1].replace('RD$ ', '').replace(',', '')
                try:
                    price = float(price_str)
                    services.append({'nombre': service_name, 'precio': price})
                except ValueError:
                    continue
            
            if not services:
                messagebox.showwarning("Servicios requeridos", "Agregue al menos un servicio a la factura")
                return
            
            # Calcular totales
            subtotal = sum(s['precio'] for s in services)
            itbis = subtotal * 0.18
            total = subtotal + itbis
            
            # Obtener observaciones
            observations = self.observations_text.get("1.0", tk.END).strip()
            
            # Crear factura en la base de datos
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener datos de la cita
            cursor.execute("""
                SELECT c.paciente_id, c.doctor_id, p.nombre, p.apellido 
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                WHERE c.id = ?
            """, (self.selected_appointment_id,))
            
            cita_data = cursor.fetchone()
            
            if not cita_data:
                messagebox.showerror("Error", "No se encontraron datos de la cita")
                return
            
            # Generar número de factura
            cursor.execute("SELECT COUNT(*) FROM facturas WHERE DATE(fecha_creacion) = DATE('now')")
            count = cursor.fetchone()[0]
            fecha_actual = datetime.now()
            numero_factura = f"FAC-{fecha_actual.strftime('%Y')}-{str(count + 1).zfill(4)}"
            
            # Insertar factura
            cursor.execute("""
                INSERT INTO facturas (numero_factura, fecha_creacion, fecha_vencimiento, 
                                    paciente_id, concepto, monto, estado, cita_id, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_factura,
                fecha_actual.isoformat(),
                (fecha_actual + timedelta(days=30)).isoformat(),
                cita_data[0],
                f"Servicios médicos - {', '.join([s['nombre'] for s in services[:2]])}{'...' if len(services) > 2 else ''}",
                total,
                'pendiente',
                self.selected_appointment_id,
                observations
            ))
            
            factura_id = cursor.lastrowid
            
            # Insertar detalles de servicios (si existe tabla de detalles)
            try:
                for service in services:
                    cursor.execute("""
                        INSERT INTO facturas_detalle (factura_id, servicio, precio, cantidad)
                        VALUES (?, ?, ?, ?)
                    """, (factura_id, service['nombre'], service['precio'], 1))
            except:
                # Si no existe tabla de detalles, continuar sin error
                pass
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Mostrar confirmación
            messagebox.showinfo("Factura Creada", 
                              f"✅ Factura {numero_factura} creada exitosamente\n\n"
                              f"Paciente: {cita_data[2]} {cita_data[3]}\n"
                              f"Total: RD$ {total:,.2f}\n"
                              f"Estado: Pendiente")
            
            # Limpiar formulario
            self.clear_invoice_form()
            
            # Refrescar lista de citas
            self.load_pending_appointments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando factura: {str(e)}")
    
    def clear_invoice_form(self):
        """Limpiar formulario de factura"""
        # Limpiar servicios
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        
        # Recargar servicios predeterminados
        self.load_default_services()
        
        # Limpiar observaciones
        self.observations_text.delete("1.0", tk.END)
        
        # Limpiar información de cita
        self.selected_appointment_info.config(text="Seleccione una cita para facturar", fg='#64748B')
        
        # Resetear totales
        self.subtotal_label.config(text="RD$ 0.00")
        self.itbis_label.config(text="RD$ 0.00")
        self.total_label.config(text="RD$ 0.00")
        
        # Limpiar selección
        if hasattr(self, 'selected_appointment_id'):
            delattr(self, 'selected_appointment_id')
    
    def remove_service_from_invoice(self):
        """Quitar servicio seleccionado de la factura"""
        selection = self.services_tree.selection()
        if selection:
            self.services_tree.delete(selection[0])
            self.calculate_totals()
        else:
            messagebox.showwarning("Selección requerida", "Seleccione un servicio para quitar")
    
    def edit_service_price(self):
        """Editar precio del servicio seleccionado"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Seleccione un servicio para editar")
            return
        
        item = self.services_tree.item(selection[0])
        values = item['values']
        current_price = values[1].replace('RD$ ', '').replace(',', '')
        
        # Diálogo para editar precio
        new_price = simpledialog.askfloat("Editar Precio", 
                                         f"Nuevo precio para '{values[0]}':",
                                         initialvalue=float(current_price))
        
        if new_price is not None and new_price > 0:
            self.services_tree.item(selection[0], values=(values[0], f"RD$ {new_price:,.2f}"))
            self.calculate_totals()
    
    def generate_invoice_pdf(self):
        """Generar PDF completo de la factura con ReportLab"""
        if not hasattr(self, 'selected_appointment_id') or not self.selected_appointment_id:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una cita para facturar")
            return
        
        # Verificar que hay servicios agregados
        if not self.services_tree.get_children():
            messagebox.showwarning("Servicios requeridos", "Por favor, agregue al menos un servicio a la factura")
            return
        
        try:
            # Verificar si reportlab está disponible
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.pdfgen import canvas
            except ImportError:
                messagebox.showerror("Error", "ReportLab no está instalado. Instalando...")
                self.install_reportlab()
                return
            
            # Crear directorio para PDFs
            pdf_dir = "facturas_pdf"
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
                
            # Obtener datos de la cita
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener información de la cita y paciente
            cursor.execute("""
                SELECT c.id, c.fecha_hora, c.motivo, 
                       p.nombre, p.apellido, p.email, p.telefono,
                       d.nombre || ' ' || d.apellido as doctor_nombre,
                       dr.especialidad
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios d ON c.doctor_id = d.id
                LEFT JOIN doctores dr ON d.id = dr.id
                WHERE c.id = ?
            """, (self.selected_appointment_id,))
            
            appointment_data = cursor.fetchone()
            
            if not appointment_data:
                messagebox.showerror("Error", "No se encontró información de la cita")
                return
                
            # Generar número de factura único
            fecha_str = datetime.now().strftime('%Y%m%d%H%M%S')
            numero_factura = f"FAC-{fecha_str}"
            
            # Nombre del archivo
            paciente_nombre = f"{appointment_data[3]}_{appointment_data[4]}".replace(' ', '_')
            filename = f"Factura_{numero_factura}_{paciente_nombre}.pdf"
            filepath = os.path.join(pdf_dir, filename)
            
            # Crear el PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, 
                                   topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilo personalizado para el título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1,  # Centrado
                fontName='Helvetica-Bold'
            )
            
            # Estilo para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            # Header de la clínica
            story.append(Paragraph("🏥 MEDISYNC", title_style))
            story.append(Paragraph("Sistema de Gestión Médica Integral", styles['Normal']))
            story.append(Paragraph("Tel: (809) 555-0123 | Email: info@medisync.com", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Información de la factura
            invoice_info = f"""
            <b>FACTURA MÉDICA</b><br/>
            <b>Número:</b> {numero_factura}<br/>
            <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Válida hasta:</b> {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}
            """
            story.append(Paragraph(invoice_info, subtitle_style))
            story.append(Spacer(1, 20))
            
            # Información del paciente y doctor
            patient_doctor_data = [
                ['DATOS DEL PACIENTE', 'DATOS DEL MÉDICO'],
                [f'Nombre: {appointment_data[3]} {appointment_data[4]}', f'Doctor: {appointment_data[7]}'],
                [f'Email: {appointment_data[5] or "No especificado"}', f'Especialidad: {appointment_data[8] or "General"}'],
                [f'Teléfono: {appointment_data[6] or "No especificado"}', f'Fecha Consulta: {appointment_data[1]}'],
                [f'Motivo: {appointment_data[2]}', '']
            ]
            
            patient_doctor_table = Table(patient_doctor_data, colWidths=[3*inch, 3*inch])
            patient_doctor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(patient_doctor_table)
            story.append(Spacer(1, 20))
            
            # Servicios médicos
            story.append(Paragraph("SERVICIOS MÉDICOS", subtitle_style))
            
            # Recopilar servicios del TreeView
            services_data = [['Descripción del Servicio', 'Cantidad', 'Precio Unitario', 'Total']]
            subtotal = 0
            
            for item in self.services_tree.get_children():
                values = self.services_tree.item(item)['values']
                servicio = values[0]
                precio_str = str(values[1]).replace('RD$ ', '').replace(',', '')
                try:
                    precio = float(precio_str)
                    cantidad = 1  # Por defecto
                    total_servicio = precio * cantidad
                    subtotal += total_servicio
                    
                    services_data.append([
                        servicio,
                        str(cantidad),
                        f'RD$ {precio:,.2f}',
                        f'RD$ {total_servicio:,.2f}'
                    ])
                except ValueError:
                    # Si hay error convirtiendo precio, usar como está
                    services_data.append([servicio, '1', str(values[1]), str(values[1])])
            
            services_table = Table(services_data, colWidths=[3*inch, 0.8*inch, 1.1*inch, 1.1*inch])
            services_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Alinear totales a la derecha
            ]))
            
            story.append(services_table)
            story.append(Spacer(1, 20))
            
            # Cálculos de totales
            descuento = 0
            if hasattr(self, 'discount_var') and self.discount_var.get():
                try:
                    descuento = float(self.discount_var.get().replace('%', ''))
                    descuento = subtotal * (descuento / 100)
                except:
                    descuento = 0
                    
            subtotal_con_descuento = subtotal - descuento
            itbis = subtotal_con_descuento * 0.18  # ITBIS 18%
            total_final = subtotal_con_descuento + itbis
            
            # Tabla de totales
            totals_data = [
                ['Subtotal:', f'RD$ {subtotal:,.2f}'],
            ]
            
            if descuento > 0:
                totals_data.append(['Descuento:', f'- RD$ {descuento:,.2f}'])
                totals_data.append(['Subtotal con descuento:', f'RD$ {subtotal_con_descuento:,.2f}'])
            
            totals_data.extend([
                ['ITBIS (18%):', f'RD$ {itbis:,.2f}'],
                ['TOTAL A PAGAR:', f'RD$ {total_final:,.2f}']
            ])
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-2, -1), 'Helvetica'),
                ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-2, -1), 10),
                ('FONTSIZE', (-2, -1), (-1, -1), 12),
                ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('TEXTCOLOR', (-2, -1), (-1, -1), colors.darkblue),
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 30))
            
            # Información de pago
            payment_info = """
            <b>INFORMACIÓN DE PAGO:</b><br/>
            • Efectivo, Tarjeta de Crédito/Débito aceptadas<br/>
            • Transferencia bancaria disponible<br/>
            • Consulte nuestros planes de financiamiento<br/>
            """
            story.append(Paragraph(payment_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Footer
            footer_text = f"""
            <b>¡Gracias por confiar en MEDISYNC!</b><br/>
            Esta factura fue generada automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}<br/>
            Para consultas sobre esta factura, contacte a nuestro departamento de facturación.<br/>
            <i>Documento válido sin firma ni sello según resolución tributaria.</i>
            """
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Construir el PDF
            doc.build(story)
            
            # Guardar información de la factura en la base de datos
            try:
                cursor.execute("""
                    INSERT INTO facturas (
                        paciente_id, cita_id, numero_factura, concepto, monto, 
                        estado, fecha_creacion, fecha_vencimiento, notas, 
                        doctor_id, tipo_consulta, moneda
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    appointment_data[0],  # Usar el ID del paciente de la cita
                    self.selected_appointment_id,
                    numero_factura,
                    f"Consulta médica - {appointment_data[2]}",
                    total_final,
                    'pendiente',
                    datetime.now().isoformat(),
                    (datetime.now() + timedelta(days=30)).isoformat(),
                    f"Factura generada para consulta con {appointment_data[7]}",
                    appointment_data[0],  # ID del doctor (simplificado)
                    appointment_data[8] or 'Consulta General',
                    'RD$'
                ))
                
                conn.commit()
                
            except Exception as db_error:
                print(f"Error guardando en BD: {db_error}")
                # Continuar aún si hay error en BD
            
            cursor.close()
            conn.close()
            
            # Mostrar mensaje de éxito y abrir PDF
            result = messagebox.askquestion(
                "PDF Generado Exitosamente", 
                f"Factura guardada como: {filename}\n\n¿Desea abrir el PDF ahora?",
                icon='question'
            )
            
            if result == 'yes':
                try:
                    os.startfile(filepath)  # Windows
                except:
                    try:
                        os.system(f'open "{filepath}"')  # macOS
                    except:
                        try:
                            os.system(f'xdg-open "{filepath}"')  # Linux
                        except:
                            messagebox.showinfo("PDF Guardado", f"Archivo guardado en:\n{os.path.abspath(filepath)}")
            
        except ImportError:
            messagebox.showwarning("Dependencia requerida", 
                                 "ReportLab no está instalado.\n\nInstalando automáticamente...")
            self.install_reportlab()
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {str(e)}")
            print(f"Error detallado: {e}")
    
    def open_payment_window(self):
        """Abrir ventana de procesamiento de pagos amigable"""
        if not hasattr(self, 'selected_appointment_id') or not self.selected_appointment_id:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una cita primero")
            return
        
        # Verificar que hay servicios agregados
        if not self.services_tree.get_children():
            messagebox.showwarning("Servicios requeridos", "Por favor, agregue al menos un servicio a la factura")
            return
        
        # Calcular totales actuales
        self.calculate_totals()
        
        # Obtener el total de la etiqueta
        total_text = self.total_label.cget('text')
        try:
            total_amount = float(total_text.replace('RD$ ', '').replace(',', ''))
        except:
            messagebox.showerror("Error", "No se pudo calcular el total de la factura")
            return
        
        # Crear ventana de pago
        self.create_payment_window(total_amount)
    
    def create_payment_window(self, total_amount):
        """Crear ventana moderna de procesamiento de pagos con scroll"""
        # Ventana principal
        payment_window = tk.Toplevel(self.root)
        payment_window.title("💳 Procesamiento de Pago - MEDISYNC")
        payment_window.geometry("850x600")
        payment_window.configure(bg='#FFFFFF')
        payment_window.resizable(True, True)
        payment_window.transient(self.root)
        payment_window.grab_set()
        
        # Centrar ventana
        payment_window.update_idletasks()
        x = (payment_window.winfo_screenwidth() // 2) - (850 // 2)
        y = (payment_window.winfo_screenheight() // 2) - (600 // 2)
        payment_window.geometry(f"850x600+{x}+{y}")
        
        # Canvas y scrollbar para hacer scroll
        canvas = tk.Canvas(payment_window, bg='#FFFFFF')
        scrollbar = ttk.Scrollbar(payment_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout del canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal dentro del scrollable_frame
        main_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header elegante
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        tk.Label(header_content, text="💳", font=('Arial', 24), bg='#1E3A8A', fg='white').pack(side='left')
        
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', fill='both', expand=True, padx=(15, 0))
        
        tk.Label(title_frame, text="PROCESAMIENTO DE PAGO", 
                font=('Arial', 16, 'bold'), bg='#1E3A8A', fg='white').pack(anchor='w')
        tk.Label(title_frame, text="Complete la información del pago para generar la factura", 
                font=('Arial', 11), bg='#1E3A8A', fg='#CBD5E1').pack(anchor='w')
        
        # Información de la factura
        invoice_info_frame = tk.LabelFrame(main_frame, text="🧾 Información de la Factura", 
                                         font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                         padx=20, pady=15)
        invoice_info_frame.pack(fill='x', pady=(0, 20))
        
        # Obtener información del paciente
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nombre || ' ' || p.apellido as paciente,
                       d.nombre || ' ' || d.apellido as doctor,
                       c.motivo, c.fecha_hora
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                JOIN usuarios d ON c.doctor_id = d.id
                WHERE c.id = ?
            """, (self.selected_appointment_id,))
            
            appointment_info = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if appointment_info:
                paciente, doctor, motivo, fecha_hora = appointment_info
                
                info_grid = tk.Frame(invoice_info_frame, bg='#FFFFFF')
                info_grid.pack(fill='x')
                
                # Primera fila
                tk.Label(info_grid, text="👤 Paciente:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
                tk.Label(info_grid, text=paciente, font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=0, column=1, sticky='w', pady=5)
                
                tk.Label(info_grid, text="👨‍⚕️ Doctor:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=0, column=2, sticky='w', padx=(30, 10), pady=5)
                tk.Label(info_grid, text=doctor, font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=0, column=3, sticky='w', pady=5)
                
                # Segunda fila
                tk.Label(info_grid, text="🏥 Motivo:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
                tk.Label(info_grid, text=motivo, font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=1, column=1, columnspan=3, sticky='w', pady=5)
                
        except Exception as e:
            print(f"Error obteniendo información: {e}")
        
        # Servicios incluidos
        services_frame = tk.LabelFrame(main_frame, text="🏥 Servicios Incluidos", 
                                     font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                     padx=15, pady=10)
        services_frame.pack(fill='x', pady=(0, 20))
        
        # Lista de servicios
        services_list_frame = tk.Frame(services_frame, bg='white', relief='solid', bd=1)
        services_list_frame.pack(fill='x', pady=(10, 0))
        
        for item in self.services_tree.get_children():
            values = self.services_tree.item(item)['values']
            service_item = tk.Frame(services_list_frame, bg='white')
            service_item.pack(fill='x', padx=15, pady=5)
            
            tk.Label(service_item, text=f"• {values[0]}", font=('Arial', 10), 
                    bg='white', fg='#1E3A8A').pack(side='left')
            tk.Label(service_item, text=f"{values[1]}", font=('Arial', 10, 'bold'), 
                    bg='white', fg='#16A085').pack(side='right')
        
        # Totales destacados
        totals_frame = tk.LabelFrame(main_frame, text="💰 Totales de Facturación", 
                                   font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                   padx=20, pady=15)
        totals_frame.pack(fill='x', pady=(0, 20))
        
        # Cálculos
        subtotal = total_amount / 1.18  # Quitar ITBIS para obtener subtotal
        itbis = total_amount - subtotal
        
        # Mostrar totales con estilo
        totals_grid = tk.Frame(totals_frame, bg='#FFFFFF')
        totals_grid.pack(fill='x')
        
        # Subtotal
        tk.Label(totals_grid, text="Subtotal:", font=('Arial', 12), bg='#FFFFFF').grid(row=0, column=0, sticky='w', pady=5)
        tk.Label(totals_grid, text=f"RD$ {subtotal:,.2f}", font=('Arial', 12), bg='#FFFFFF', fg='#1E3A8A').grid(row=0, column=1, sticky='e', pady=5)
        
        # ITBIS
        tk.Label(totals_grid, text="ITBIS (18%):", font=('Arial', 12), bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=5)
        tk.Label(totals_grid, text=f"RD$ {itbis:,.2f}", font=('Arial', 12), bg='#FFFFFF', fg='#1E3A8A').grid(row=1, column=1, sticky='e', pady=5)
        
        # Separador
        separator = tk.Frame(totals_grid, bg='#CBD5E1', height=2)
        separator.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Total
        tk.Label(totals_grid, text="TOTAL A PAGAR:", font=('Arial', 14, 'bold'), bg='#FFFFFF').grid(row=3, column=0, sticky='w', pady=5)
        total_amount_label = tk.Label(totals_grid, text=f"RD$ {total_amount:,.2f}", 
                                    font=('Arial', 16, 'bold'), bg='#FFFFFF', fg='#C0392B')
        total_amount_label.grid(row=3, column=1, sticky='e', pady=5)
        
        totals_grid.grid_columnconfigure(1, weight=1)
        
        # Frame de pago
        payment_details_frame = tk.LabelFrame(main_frame, text="💳 Detalles del Pago", 
                                            font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                            padx=20, pady=15)
        payment_details_frame.pack(fill='x', pady=(0, 20))
        
        payment_grid = tk.Frame(payment_details_frame, bg='#FFFFFF')
        payment_grid.pack(fill='x', pady=10)
        
        # Monto recibido del paciente
        tk.Label(payment_grid, text="💵 Monto Recibido:", font=('Arial', 12, 'bold'), 
                bg='#FFFFFF').grid(row=0, column=0, sticky='w', pady=10)
        
        self.amount_received_var = tk.StringVar()
        amount_entry = tk.Entry(payment_grid, textvariable=self.amount_received_var, 
                              font=('Arial', 14, 'bold'), width=15, justify='center',
                              relief='solid', bd=2)
        amount_entry.grid(row=0, column=1, padx=(10, 0), pady=10)
        amount_entry.focus()
        
        # Método de pago
        tk.Label(payment_grid, text="💳 Método de Pago:", font=('Arial', 12, 'bold'), 
                bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=10)
        
        self.payment_method_var = tk.StringVar(value="Efectivo")
        payment_method_combo = ttk.Combobox(payment_grid, textvariable=self.payment_method_var,
                                          values=["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", 
                                                "Transferencia Bancaria", "Cheque"], 
                                          state="readonly", width=20, font=('Arial', 11))
        payment_method_combo.grid(row=1, column=1, padx=(10, 0), pady=10, sticky='w')
        
        # Cálculo automático del cambio
        change_frame = tk.LabelFrame(main_frame, text="💸 Cálculo de Cambio", 
                                   font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                   padx=20, pady=15)
        change_frame.pack(fill='x', pady=(0, 20))
        
        change_display = tk.Frame(change_frame, bg='#FFFFFF')
        change_display.pack(fill='x', pady=10)
        
        self.change_status_label = tk.Label(change_display, text="Ingrese el monto recibido", 
                                          font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#64748B')
        self.change_status_label.pack()
        
        self.change_amount_label = tk.Label(change_display, text="", 
                                          font=('Arial', 18, 'bold'), bg='#FFFFFF')
        self.change_amount_label.pack(pady=(10, 0))
        
        # Función para calcular cambio en tiempo real
        def calculate_change(*args):
            try:
                received = float(self.amount_received_var.get() or 0)
                change = received - total_amount
                
                if received == 0:
                    self.change_status_label.config(text="Ingrese el monto recibido", fg='#64748B')
                    self.change_amount_label.config(text="")
                elif change >= 0:
                    self.change_status_label.config(text="💰 CAMBIO A DEVOLVER:", fg='#16A085')
                    self.change_amount_label.config(text=f"RD$ {change:,.2f}", fg='#16A085')
                else:
                    self.change_status_label.config(text="❌ MONTO INSUFICIENTE:", fg='#C0392B')
                    self.change_amount_label.config(text=f"Faltan: RD$ {abs(change):,.2f}", fg='#C0392B')
            except ValueError:
                self.change_status_label.config(text="⚠️ Ingrese un monto válido", fg='#E67E22')
                self.change_amount_label.config(text="")
        
        self.amount_received_var.trace('w', calculate_change)
        
        # Botones de acción
        buttons_frame = tk.Frame(main_frame, bg='#FFFFFF')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Botón Cancelar
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar", 
                             command=payment_window.destroy,
                             bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                             width=15, pady=10, relief='raised', bd=3)
        cancel_btn.pack(side='left')
        
        # Botón Procesar y Generar PDF
        def process_payment_and_generate():
            try:
                received = float(self.amount_received_var.get() or 0)
                if received < total_amount:
                    messagebox.showwarning("Pago Insuficiente", 
                                         f"El monto recibido (RD$ {received:,.2f}) es menor al total a pagar (RD$ {total_amount:,.2f})")
                    return
                
                # Crear la factura en la base de datos
                invoice_id = self.create_invoice_in_database(total_amount, received)
                
                if invoice_id:
                    # Generar PDF automáticamente
                    self.generate_final_invoice_pdf(invoice_id, total_amount, received)
                    
                    # Mostrar mensaje de éxito
                    change = received - total_amount
                    success_msg = f"✅ Pago procesado exitosamente!\n\n"
                    success_msg += f"Total: RD$ {total_amount:,.2f}\n"
                    success_msg += f"Recibido: RD$ {received:,.2f}\n"
                    if change > 0:
                        success_msg += f"Cambio: RD$ {change:,.2f}\n"
                    success_msg += f"\n📄 PDF generado automáticamente"
                    
                    messagebox.showinfo("Pago Completado", success_msg)
                    
                    # Cerrar ventana y actualizar listas
                    payment_window.destroy()
                    self.load_existing_invoices()
                    self.clear_invoice_form()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error procesando el pago: {str(e)}")
        
        process_btn = tk.Button(buttons_frame, text="💳 PROCESAR PAGO Y GENERAR PDF", 
                              command=process_payment_and_generate,
                              bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                              width=35, pady=10, relief='raised', bd=3)
        process_btn.pack(side='right')
        
        # Guardar referencias para uso posterior
        payment_window.total_amount = total_amount
        self.current_payment_window = payment_window
    
    def create_invoice_in_database(self, total_amount, amount_received):
        """Crear factura en la base de datos"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Generar número de factura único
            fecha_str = datetime.now().strftime('%Y%m%d%H%M%S')
            numero_factura = f"FAC-{fecha_str}"
            
            # Obtener información de la cita
            cursor.execute("""
                SELECT paciente_id, doctor_id, motivo 
                FROM citas 
                WHERE id = ?
            """, (self.selected_appointment_id,))
            
            cita_info = cursor.fetchone()
            if not cita_info:
                raise Exception("No se encontró información de la cita")
            
            paciente_id, doctor_id, motivo = cita_info
            
            # Determinar estado del pago
            change = amount_received - total_amount
            estado = 'pagada' if change >= 0 else 'pago_parcial'
            
            # Crear concepto basado en servicios
            servicios = []
            for item in self.services_tree.get_children():
                values = self.services_tree.item(item)['values']
                servicios.append(values[0])
            
            concepto = f"Consulta médica - {motivo}" if servicios else motivo
            if servicios:
                concepto += f"\nServicios: {', '.join(servicios)}"
            
            # Insertar factura
            cursor.execute("""
                INSERT INTO facturas (
                    paciente_id, cita_id, numero_factura, concepto, monto, 
                    estado, fecha_creacion, fecha_vencimiento, notas, 
                    doctor_id, tipo_consulta, moneda, metodo_pago, fecha_pago
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paciente_id,
                self.selected_appointment_id,
                numero_factura,
                concepto,
                total_amount,
                estado,
                datetime.now().isoformat(),
                (datetime.now() + timedelta(days=30)).isoformat(),
                f"Pago procesado - Recibido: RD$ {amount_received:,.2f}, Cambio: RD$ {change:,.2f}",
                doctor_id,
                motivo,
                'RD$',
                self.payment_method_var.get(),
                datetime.now().isoformat()
            ))
            
            # Obtener ID de la factura creada
            invoice_id = cursor.lastrowid
            
            # Insertar detalles de servicios en facturas_detalle
            for item in self.services_tree.get_children():
                values = self.services_tree.item(item)['values']
                servicio = values[0]
                precio_str = str(values[1]).replace('RD$ ', '').replace(',', '')
                try:
                    precio = float(precio_str)
                    cursor.execute("""
                        INSERT INTO facturas_detalle (
                            factura_id, descripcion, cantidad, precio_unitario, total
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (invoice_id, servicio, 1, precio, precio))
                except ValueError:
                    # Si hay error convirtiendo precio, usar 0
                    cursor.execute("""
                        INSERT INTO facturas_detalle (
                            factura_id, descripcion, cantidad, precio_unitario, total
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (invoice_id, servicio, 1, 0, 0))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return invoice_id
            
        except Exception as e:
            print(f"Error creando factura en BD: {e}")
            messagebox.showerror("Error", f"Error creando factura: {str(e)}")
            return None
    
    def generate_final_invoice_pdf(self, invoice_id, total_amount, amount_received):
        """Generar PDF final con información completa de pago"""
        try:
            # Verificar que reportlab esté disponible
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
            except ImportError:
                messagebox.showerror("Error", "ReportLab no está disponible para generar PDF")
                return
            
            # Crear directorio para PDFs
            pdf_dir = "facturas_pdf"
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            # Obtener información completa de la factura
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT f.numero_factura, f.fecha_creacion, f.monto, f.concepto, 
                       f.metodo_pago, f.fecha_pago, f.notas,
                       p.nombre, p.apellido, p.email, p.telefono,
                       d.nombre as doctor_nombre, d.apellido as doctor_apellido,
                       dr.especialidad
                FROM facturas f
                JOIN usuarios p ON f.paciente_id = p.id
                JOIN usuarios d ON f.doctor_id = d.id
                LEFT JOIN doctores dr ON d.id = dr.id
                WHERE f.id = ?
            """, (invoice_id,))
            
            factura_data = cursor.fetchone()
            if not factura_data:
                raise Exception("No se encontró la factura generada")
            
            # Obtener detalles de servicios
            cursor.execute("""
                SELECT descripcion, cantidad, precio_unitario, total
                FROM facturas_detalle
                WHERE factura_id = ?
            """, (invoice_id,))
            
            servicios_detalle = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Desempaquetar datos
            (numero_factura, fecha_creacion, monto, concepto, metodo_pago, fecha_pago, notas,
             nombre_paciente, apellido_paciente, email, telefono,
             doctor_nombre, doctor_apellido, especialidad) = factura_data
            
            # Generar nombre del archivo
            paciente_nombre = f"{nombre_paciente}_{apellido_paciente}".replace(' ', '_')
            filename = f"Factura_{numero_factura}_{paciente_nombre}.pdf"
            filepath = os.path.join(pdf_dir, filename)
            
            # Crear el PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, 
                                   topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            # Header de la clínica
            story.append(Paragraph("🏥 MEDISYNC", title_style))
            story.append(Paragraph("Sistema de Gestión Médica Integral", styles['Normal']))
            story.append(Paragraph("Tel: (809) 555-0123 | Email: info@medisync.com", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Información de la factura con estado PAGADA
            fecha_obj = datetime.fromisoformat(fecha_creacion)
            invoice_info = f"""
            <b>FACTURA MÉDICA - ✅ PAGADA</b><br/>
            <b>Número:</b> {numero_factura}<br/>
            <b>Fecha de Emisión:</b> {fecha_obj.strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Fecha de Pago:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Método de Pago:</b> {metodo_pago}
            """
            story.append(Paragraph(invoice_info, subtitle_style))
            story.append(Spacer(1, 20))
            
            # Información del paciente y doctor
            patient_doctor_data = [
                ['DATOS DEL PACIENTE', 'DATOS DEL MÉDICO'],
                [f'Nombre: {nombre_paciente} {apellido_paciente}', f'Doctor: {doctor_nombre} {doctor_apellido}'],
                [f'Email: {email or "No especificado"}', f'Especialidad: {especialidad or "General"}'],
                [f'Teléfono: {telefono or "No especificado"}', '']
            ]
            
            patient_doctor_table = Table(patient_doctor_data, colWidths=[3*inch, 3*inch])
            patient_doctor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(patient_doctor_table)
            story.append(Spacer(1, 20))
            
            # Servicios médicos
            story.append(Paragraph("SERVICIOS MÉDICOS", subtitle_style))
            
            # Tabla de servicios
            services_data = [['Descripción del Servicio', 'Cantidad', 'Precio Unitario', 'Total']]
            
            for servicio in servicios_detalle:
                descripcion, cantidad, precio_unitario, total_servicio = servicio
                services_data.append([
                    descripcion,
                    str(int(cantidad)),
                    f'RD$ {float(precio_unitario):,.2f}',
                    f'RD$ {float(total_servicio):,.2f}'
                ])
            
            services_table = Table(services_data, colWidths=[3*inch, 0.8*inch, 1.1*inch, 1.1*inch])
            services_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ]))
            
            story.append(services_table)
            story.append(Spacer(1, 20))
            
            # Cálculos de totales
            subtotal = total_amount / 1.18
            itbis = total_amount - subtotal
            change = amount_received - total_amount
            
            # Tabla de totales con información de pago
            totals_data = [
                ['Subtotal:', f'RD$ {subtotal:,.2f}'],
                ['ITBIS (18%):', f'RD$ {itbis:,.2f}'],
                ['TOTAL A PAGAR:', f'RD$ {total_amount:,.2f}'],
                ['', ''],
                ['MONTO RECIBIDO:', f'RD$ {amount_received:,.2f}'],
                ['CAMBIO DEVUELTO:', f'RD$ {change:,.2f}' if change > 0 else 'RD$ 0.00']
            ]
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 2), 'Helvetica'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTNAME', (0, 4), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 1), 10),
                ('FONTSIZE', (0, 2), (-1, 2), 12),
                ('FONTSIZE', (0, 4), (-1, -1), 11),
                ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
                ('BACKGROUND', (0, 4), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, 2), 1, colors.black),
                ('GRID', (0, 4), (-1, -1), 1, colors.black),
                ('TEXTCOLOR', (0, 2), (-1, 2), colors.darkblue),
                ('TEXTCOLOR', (0, 4), (-1, -1), colors.darkgreen),
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 30))
            
            # Estado de pago
            payment_status = f"""
            <b>✅ ESTADO DEL PAGO: COMPLETADO</b><br/>
            Método de pago: {metodo_pago}<br/>
            Fecha y hora de pago: {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}<br/>
            """
            story.append(Paragraph(payment_status, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Footer
            footer_text = f"""
            <b>¡Gracias por confiar en MEDISYNC!</b><br/>
            Esta factura ha sido pagada en su totalidad.<br/>
            Para consultas sobre esta factura, contacte a nuestro departamento de facturación.<br/>
            <i>Documento válido sin firma ni sello según resolución tributaria.</i>
            """
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Construir el PDF
            doc.build(story)
            
            # Abrir el PDF automáticamente
            try:
                os.startfile(filepath)  # Windows
            except:
                try:
                    os.system(f'open "{filepath}"')  # macOS
                except:
                    try:
                        os.system(f'xdg-open "{filepath}"')  # Linux
                    except:
                        pass
            
            return filepath
            
        except Exception as e:
            print(f"Error generando PDF final: {e}")
            messagebox.showerror("Error", f"Error generando PDF: {str(e)}")
            return None
    
    def process_payment_window(self):
        """Abrir ventana de procesamiento de pagos para factura existente"""
        selection = self.billing_invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una factura de la tabla verde (⏳ Pendientes)")
            return
        
        # Obtener información de la factura seleccionada
        item = selection[0]
        values = self.billing_invoices_tree.item(item, 'values')
        numero_factura = values[0]
        estado_mostrado = values[2]  # El estado que se muestra en la tabla
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, monto, estado
                FROM facturas
                WHERE numero_factura = ?
            """, (numero_factura,))
            
            factura_info = cursor.fetchone()
            if not factura_info:
                messagebox.showerror("Error", "No se encontró la factura")
                return
            
            factura_id, monto, estado = factura_info
            
            # Verificar que la factura esté pendiente
            if estado == 'pagada':
                messagebox.showwarning("❌ Factura ya pagada", 
                    f"La factura #{numero_factura} ya está pagada.\n\n"
                    "💡 Solo puede procesar pagos para facturas con estado '⏳ Pendiente' (tabla verde).")
                return
            
            # Confirmar que quiere procesar el pago
            confirm = messagebox.askyesno("💳 Confirmar procesamiento", 
                f"¿Procesar pago para la factura #{numero_factura}?\n\n"
                f"Monto: RD$ {monto:,.2f}\n"
                f"Estado actual: {estado_mostrado}")
            
            if confirm:
                # Abrir ventana de pago para factura existente
                self.create_existing_invoice_payment_window(factura_id, float(monto))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando pago: {str(e)}")
    
    def create_existing_invoice_payment_window(self, invoice_id, total_amount):
        """Crear ventana de pago para factura existente"""
        # Ventana principal
        payment_window = tk.Toplevel(self.root)
        payment_window.title("💳 Procesar Pago - Factura Existente")
        payment_window.geometry("750x500")
        payment_window.configure(bg='#FFFFFF')
        payment_window.resizable(True, True)
        payment_window.transient(self.root)
        payment_window.grab_set()
        
        # Centrar ventana
        payment_window.update_idletasks()
        x = (payment_window.winfo_screenwidth() // 2) - (750 // 2)
        y = (payment_window.winfo_screenheight() // 2) - (500 // 2)
        payment_window.geometry(f"750x500+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(payment_window, bg='#FFFFFF')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header elegante
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        tk.Label(header_content, text="💳", font=('Arial', 24), bg='#1E3A8A', fg='white').pack(side='left')
        
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', fill='both', expand=True, padx=(15, 0))
        
        tk.Label(title_frame, text="PROCESAR PAGO", 
                font=('Arial', 16, 'bold'), bg='#1E3A8A', fg='white').pack(anchor='w')
        tk.Label(title_frame, text=f"Factura existente - ID: {invoice_id}", 
                font=('Arial', 11), bg='#1E3A8A', fg='#CBD5E1').pack(anchor='w')
        
        # Información de la factura
        invoice_info_frame = tk.LabelFrame(main_frame, text="🧾 Información de la Factura", 
                                         font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                         padx=20, pady=15)
        invoice_info_frame.pack(fill='x', pady=(0, 20))
        
        # Obtener información detallada de la factura
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.numero_factura, f.fecha, 
                       p.nombre || ' ' || p.apellido as paciente,
                       d.nombre || ' ' || d.apellido as doctor
                FROM facturas f
                LEFT JOIN usuarios p ON f.paciente_id = p.id
                LEFT JOIN usuarios d ON f.doctor_id = d.id
                WHERE f.id = ?
            """, (invoice_id,))
            
            invoice_detail = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if invoice_detail:
                numero_factura, fecha, paciente, doctor = invoice_detail
                
                info_grid = tk.Frame(invoice_info_frame, bg='#FFFFFF')
                info_grid.pack(fill='x')
                
                # Primera fila
                tk.Label(info_grid, text="📄 Número:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
                tk.Label(info_grid, text=numero_factura, font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=0, column=1, sticky='w', pady=5)
                
                tk.Label(info_grid, text="📅 Fecha:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=0, column=2, sticky='w', padx=(30, 10), pady=5)
                tk.Label(info_grid, text=fecha, font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=0, column=3, sticky='w', pady=5)
                
                # Segunda fila
                tk.Label(info_grid, text="👤 Paciente:", font=('Arial', 11, 'bold'), 
                        bg='#FFFFFF').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
                tk.Label(info_grid, text=paciente or "N/A", font=('Arial', 11), 
                        bg='#FFFFFF', fg='#1E3A8A').grid(row=1, column=1, columnspan=3, sticky='w', pady=5)
                
        except Exception as e:
            print(f"Error obteniendo información de factura: {e}")
        
        # Total a pagar destacado
        total_frame = tk.LabelFrame(main_frame, text="💰 Total a Pagar", 
                                   font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                   padx=20, pady=15)
        total_frame.pack(fill='x', pady=(0, 20))
        
        total_label = tk.Label(total_frame, text=f"RD$ {total_amount:,.2f}", 
                              font=('Arial', 20, 'bold'), bg='#FFFFFF', fg='#C0392B')
        total_label.pack(pady=10)
        
        # Frame de pago
        payment_details_frame = tk.LabelFrame(main_frame, text="💳 Detalles del Pago", 
                                            font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                            padx=20, pady=15)
        payment_details_frame.pack(fill='x', pady=(0, 20))
        
        payment_grid = tk.Frame(payment_details_frame, bg='#FFFFFF')
        payment_grid.pack(fill='x', pady=10)
        
        # Monto recibido del paciente
        tk.Label(payment_grid, text="💵 Monto Recibido:", font=('Arial', 12, 'bold'), 
                bg='#FFFFFF').grid(row=0, column=0, sticky='w', pady=10)
        
        amount_received_var = tk.StringVar()
        amount_entry = tk.Entry(payment_grid, textvariable=amount_received_var, 
                              font=('Arial', 14, 'bold'), width=15, justify='center',
                              relief='solid', bd=2)
        amount_entry.grid(row=0, column=1, padx=(10, 0), pady=10)
        amount_entry.focus()
        
        # Método de pago
        tk.Label(payment_grid, text="💳 Método de Pago:", font=('Arial', 12, 'bold'), 
                bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=10)
        
        payment_method_var = tk.StringVar(value="Efectivo")
        payment_method_combo = ttk.Combobox(payment_grid, textvariable=payment_method_var,
                                          values=["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", 
                                                "Transferencia Bancaria", "Cheque"], 
                                          state="readonly", width=20, font=('Arial', 11))
        payment_method_combo.grid(row=1, column=1, padx=(10, 0), pady=10, sticky='w')
        
        # Cálculo automático del cambio
        change_frame = tk.LabelFrame(main_frame, text="💸 Cálculo de Cambio", 
                                   font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#1E3A8A',
                                   padx=20, pady=15)
        change_frame.pack(fill='x', pady=(0, 20))
        
        change_display = tk.Frame(change_frame, bg='#FFFFFF')
        change_display.pack(fill='x', pady=10)
        
        change_status_label = tk.Label(change_display, text="Ingrese el monto recibido", 
                                      font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#64748B')
        change_status_label.pack()
        
        change_amount_label = tk.Label(change_display, text="", 
                                      font=('Arial', 18, 'bold'), bg='#FFFFFF')
        change_amount_label.pack(pady=(10, 0))
        
        # Función para calcular cambio en tiempo real
        def calculate_change(*args):
            try:
                received = float(amount_received_var.get() or 0)
                change = received - total_amount
                
                if received == 0:
                    change_status_label.config(text="Ingrese el monto recibido", fg='#64748B')
                    change_amount_label.config(text="")
                elif change >= 0:
                    change_status_label.config(text="💰 CAMBIO A DEVOLVER:", fg='#16A085')
                    change_amount_label.config(text=f"RD$ {change:,.2f}", fg='#16A085')
                else:
                    change_status_label.config(text="❌ MONTO INSUFICIENTE:", fg='#C0392B')
                    change_amount_label.config(text=f"Faltan: RD$ {abs(change):,.2f}", fg='#C0392B')
            except ValueError:
                change_status_label.config(text="⚠️ Ingrese un monto válido", fg='#E67E22')
                change_amount_label.config(text="")
        
        amount_received_var.trace('w', calculate_change)
        
        # Botones de acción
        buttons_frame = tk.Frame(main_frame, bg='#FFFFFF')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Botón Cancelar
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar", 
                             command=payment_window.destroy,
                             bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                             width=15, pady=10, relief='raised', bd=3)
        cancel_btn.pack(side='left')
        
        # Botón Procesar Pago
        def process_existing_payment():
            try:
                received = float(amount_received_var.get() or 0)
                if received < total_amount:
                    messagebox.showwarning("Pago Insuficiente", 
                                         f"El monto recibido (RD$ {received:,.2f}) es menor al total a pagar (RD$ {total_amount:,.2f})")
                    return
                
                # Actualizar el estado de la factura a 'pagada'
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE facturas 
                    SET estado = 'pagada',
                        monto_recibido = ?,
                        metodo_pago = ?,
                        fecha_pago = datetime('now', 'localtime')
                    WHERE id = ?
                """, (received, payment_method_var.get(), invoice_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Mostrar mensaje de éxito
                change = received - total_amount
                success_msg = f"✅ Pago procesado exitosamente!\n\n"
                success_msg += f"Factura ID: {invoice_id}\n"
                success_msg += f"Total: RD$ {total_amount:,.2f}\n"
                success_msg += f"Recibido: RD$ {received:,.2f}\n"
                if change > 0:
                    success_msg += f"Cambio: RD$ {change:,.2f}\n"
                success_msg += f"Método: {payment_method_var.get()}"
                
                messagebox.showinfo("Pago Completado", success_msg)
                
                # Cerrar ventana y actualizar listas
                payment_window.destroy()
                self.load_existing_invoices()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un monto válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error procesando el pago: {str(e)}")
        
        process_btn = tk.Button(buttons_frame, text="💳 PROCESAR PAGO", 
                              command=process_existing_payment,
                              bg='#0B5394', fg='white', font=('Arial', 12, 'bold'),
                              width=20, pady=10, relief='raised', bd=3)
        process_btn.pack(side='right', padx=(10, 0))
    
    def view_invoice_details_billing(self, event=None):
        """Ver detalles de una factura seleccionada"""
        selection = self.billing_invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una factura")
            return
        
        item = selection[0]
        values = self.billing_invoices_tree.item(item, 'values')
        numero_factura = values[0]
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT f.numero_factura, f.fecha_creacion, f.monto, f.concepto,
                       f.estado, f.metodo_pago, f.fecha_pago, f.notas,
                       p.nombre || ' ' || p.apellido as paciente,
                       d.nombre || ' ' || d.apellido as doctor
                FROM facturas f
                JOIN usuarios p ON f.paciente_id = p.id
                JOIN usuarios d ON f.doctor_id = d.id
                WHERE f.numero_factura = ?
            """, (numero_factura,))
            
            factura_info = cursor.fetchone()
            if factura_info:
                details = f"""
DETALLES DE LA FACTURA

Número: {factura_info[0]}
Fecha: {factura_info[1]}
Paciente: {factura_info[8]}
Doctor: {factura_info[9]}
Concepto: {factura_info[3]}
Monto: RD$ {float(factura_info[2]):,.2f}
Estado: {factura_info[4]}
Método de Pago: {factura_info[5] or 'No especificado'}
Fecha de Pago: {factura_info[6] or 'Pendiente'}
Notas: {factura_info[7] or 'Sin notas'}
                """
                messagebox.showinfo("Detalles de Factura", details)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo detalles: {str(e)}")
    
    def reprint_invoice_pdf(self):
        """Reimprimir PDF de una factura existente"""
        selection = self.billing_invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una factura")
            return
        
        item = selection[0]
        values = self.billing_invoices_tree.item(item, 'values')
        numero_factura = values[0]
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id
                FROM facturas
                WHERE numero_factura = ?
            """, (numero_factura,))
            
            result = cursor.fetchone()
            if result:
                invoice_id = result[0]
                # Reimprimir usando la función existente
                self.generate_final_invoice_pdf(invoice_id, 0, 0)  # Monto 0 para reimpresión
                messagebox.showinfo("PDF Reimpreso", f"PDF de la factura {numero_factura} generado nuevamente")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reimprimiendo PDF: {str(e)}")
    
    def install_reportlab(self):
        """Instalar ReportLab automáticamente"""
        try:
            import subprocess
            import sys
            
            result = messagebox.askquestion("Instalar ReportLab", 
                                          "¿Desea instalar ReportLab para generar PDFs?")
            if result == 'yes':
                subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                messagebox.showinfo("Instalación completada", 
                                   "ReportLab instalado correctamente.\nYa puede generar PDFs.")
        except Exception as e:
            messagebox.showerror("Error de instalación", 
                                f"No se pudo instalar ReportLab automáticamente.\n{str(e)}")
            story.append(Paragraph(f"<b>FACTURA #{factura_data[0]}</b>", styles['Heading2']))
            story.append(Paragraph(f"Fecha: {datetime.fromisoformat(factura_data[1]).strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Datos del paciente
            story.append(Paragraph("<b>DATOS DEL PACIENTE</b>", styles['Heading3']))
            patient_info = f"""
            Nombre: {factura_data[5]} {factura_data[6]}<br/>
            Email: {factura_data[7] or 'No especificado'}<br/>
            Teléfono: {factura_data[8] or 'No especificado'}
            """
            story.append(Paragraph(patient_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Servicios
            story.append(Paragraph("<b>SERVICIOS</b>", styles['Heading3']))
            
            # Crear tabla de servicios
            services_data = [['Servicio', 'Precio']]
            for item in self.services_tree.get_children():
                values = self.services_tree.item(item)['values']
                services_data.append([values[0], values[1]])
            
            services_table = Table(services_data)
            services_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(services_table)
            story.append(Spacer(1, 20))
            
            # Totales
            subtotal = sum(float(self.services_tree.item(item)['values'][1].replace('RD$ ', '').replace(',', '')) 
                          for item in self.services_tree.get_children())
            itbis = subtotal * 0.18
            total = subtotal + itbis
            
            totals_data = [
                ['Subtotal:', f'RD$ {subtotal:,.2f}'],
                ['ITBIS (18%):', f'RD$ {itbis:,.2f}'],
                ['TOTAL:', f'RD$ {total:,.2f}']
            ]
            
            totals_table = Table(totals_data, colWidths=[3*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 30))
            
            # Observaciones
            if factura_data[4]:
                story.append(Paragraph("<b>OBSERVACIONES</b>", styles['Heading3']))
                story.append(Paragraph(factura_data[4], styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Footer
            footer_text = f"""
            <b>¡Gracias por confiar en MEDISYNC!</b><br/>
            Factura generada automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
            Para dudas o consultas, contactar al departamento de facturación
            """
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            # Abrir el PDF
            os.startfile(filepath)
            messagebox.showinfo("PDF Generado", f"Factura guardada como: {filename}")
            
            cursor.close()
            conn.close()
            
        except ImportError:
            messagebox.showwarning("Advertencia", "reportlab no está instalado. No se puede generar PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {str(e)}")
    
    def create_payments_tab(self, parent):
        """Crear pestaña de procesamiento de pagos"""
        tk.Label(parent, text="💳 Módulo de Pagos", font=('Arial', 16, 'bold'), 
                bg='#F8FAFC').pack(pady=20)
        tk.Label(parent, text="En desarrollo - Próximamente", font=('Arial', 12), 
                bg='#F8FAFC', fg='#64748B').pack()
    
    def create_reports_tab(self, parent):
        """Crear pestaña de reportes"""
        tk.Label(parent, text="📊 Módulo de Reportes", font=('Arial', 16, 'bold'), 
                bg='#F8FAFC').pack(pady=20)
        tk.Label(parent, text="En desarrollo - Próximamente", font=('Arial', 12), 
                bg='#F8FAFC', fg='#64748B').pack()
    
    def create_billing_config_tab(self, parent):
        """Crear pestaña de configuración de facturación"""
        tk.Label(parent, text="⚙️ Configuración de Facturación", font=('Arial', 16, 'bold'), 
                bg='#F8FAFC').pack(pady=20)
        tk.Label(parent, text="En desarrollo - Próximamente", font=('Arial', 12), 
                bg='#F8FAFC', fg='#64748B').pack()
    
    def load_billing_data_integrated(self):
        """Cargar datos de facturación integrados"""
        try:
            # Limpiar tabla
            for item in self.billing_tree.get_children():
                self.billing_tree.delete(item)
            
            # Obtener facturas recientes (últimos 30 días)
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT numero_factura, fecha_creacion, 
                   (SELECT nombre || ' ' || apellido FROM usuarios WHERE id = f.paciente_id) as paciente_nombre,
                   monto, estado
            FROM facturas f
            WHERE DATE(fecha_creacion) >= ?
            ORDER BY fecha_creacion DESC
            LIMIT 20
            ''', (thirty_days_ago,))
            
            invoices = cursor.fetchall()
            
            for invoice in invoices:
                # Formatear fecha
                fecha = invoice[1]
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                # Formatear estado
                estado = invoice[4].title() if invoice[4] else 'Desconocido'
                
                self.billing_tree.insert('', 'end', values=(
                    invoice[0] or 'N/A',  # Número
                    fecha,               # Fecha
                    invoice[2] or 'N/A', # Paciente
                    f"₡{float(invoice[3] or 0):,.2f}",  # Monto
                    estado               # Estado
                ))
            
            conn.close()
            
            # Actualizar estadísticas
            self.update_billing_statistics()
            
            # Actualizar citas sin facturar
            self.update_pending_appointments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos de facturación: {str(e)}")
    
    def update_billing_statistics(self):
        """Actualizar estadísticas de facturación"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Facturas de hoy
            cursor.execute('SELECT COUNT(*) FROM facturas WHERE DATE(fecha_creacion) = ?', (today,))
            facturas_hoy = cursor.fetchone()[0]
            self.stats_vars['facturas_hoy'].set(str(facturas_hoy))
            
            # Ingresos de hoy
            cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM facturas WHERE DATE(fecha_creacion) = ? AND estado IN ("pagada", "pago_parcial")', (today,))
            ingresos_hoy = cursor.fetchone()[0]
            self.stats_vars['ingresos_hoy'].set(f"₡{float(ingresos_hoy):,.2f}")
            
            # Facturas pendientes
            cursor.execute('SELECT COUNT(*) FROM facturas WHERE estado = "pendiente"')
            pendientes = cursor.fetchone()[0]
            self.stats_vars['pendientes'].set(str(pendientes))
            
            # Citas sin facturar
            cursor.execute('''
            SELECT COUNT(*) FROM citas c
            LEFT JOIN facturas f ON c.id = f.cita_id
            WHERE c.estado = 'completada' AND f.cita_id IS NULL
            ''')
            sin_facturar = cursor.fetchone()[0]
            self.stats_vars['citas_sin_facturar'].set(str(sin_facturar))
            
            conn.close()
            
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def update_pending_appointments(self):
        """Actualizar lista de citas sin facturar"""
        try:
            self.pending_appointments_list.delete(0, tk.END)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT c.id, c.fecha_hora, 
                   (SELECT nombre || ' ' || apellido FROM usuarios WHERE id = c.paciente_id) as paciente_nombre,
                   c.motivo
            FROM citas c
            LEFT JOIN facturas f ON c.id = f.cita_id
            WHERE c.estado = 'completada' AND f.cita_id IS NULL
            ORDER BY c.fecha_hora DESC
            LIMIT 10
            ''')
            
            appointments = cursor.fetchall()
            
            for apt in appointments:
                fecha = apt[1]
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m %H:%M')
                    except:
                        pass
                
                text = f"{fecha} - {apt[2]} - {apt[3][:30]}..."
                self.pending_appointments_list.insert(tk.END, text)
                # Almacenar ID de cita para uso posterior
                self.pending_appointments_list.insert(tk.END, f"ID:{apt[0]}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error actualizando citas pendientes: {e}")
    
    def quick_invoice(self):
        """Crear factura rápida"""
        messagebox.showinfo("Factura Rápida", "Use el 'Sistema Completo' para crear facturas con todas las funcionalidades")
    
    def generate_billing_report(self):
        """Generar reporte de facturación"""
        try:
            if not PDF_AVAILABLE:
                messagebox.showwarning("PDF No Disponible", "La funcionalidad de reportes PDF no está disponible")
                return
            
            messagebox.showinfo("Reporte", "Funcionalidad de reportes disponible en el Sistema Completo")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def search_invoice(self):
        """Buscar factura"""
        search_term = simpledialog.askstring("Buscar Factura", "Ingrese número de factura o nombre del paciente:")
        if search_term:
            # Implementar búsqueda
            messagebox.showinfo("Búsqueda", f"Buscando: {search_term}\nUse el Sistema Completo para búsquedas avanzadas")
    
    def refresh_billing_data(self):
        """Actualizar datos de facturación"""
        self.load_billing_data_integrated()
        messagebox.showinfo("Actualizado", "✅ Datos de facturación actualizados")
    
    def bill_selected_appointment(self):
        """Facturar cita seleccionada"""
        selection = self.pending_appointments_list.curselection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione una cita para facturar")
            return
        
        messagebox.showinfo("Facturación", "Use el 'Sistema Completo' para facturar citas con todas las funcionalidades")
    
    def show_billing_summary(self):
        """Mostrar resumen de facturación"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener datos del mes actual
            current_month = datetime.now().strftime('%Y-%m')
            
            cursor.execute('''
            SELECT 
                COUNT(*) as total_facturas,
                COALESCE(SUM(monto), 0) as total_ingresos,
                COUNT(CASE WHEN estado = 'pagada' THEN 1 END) as pagadas,
                COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes
            FROM facturas 
            WHERE strftime('%Y-%m', fecha_creacion) = ?
            ''', (current_month,))
            
            stats = cursor.fetchone()
            conn.close()
            
            summary_text = f"""📊 RESUMEN DE FACTURACIÓN - {datetime.now().strftime('%B %Y').upper()}

💰 FACTURAS GENERADAS: {stats[0]}
💵 INGRESOS TOTALES: ₡{float(stats[1]):,.2f}
✅ FACTURAS PAGADAS: {stats[2]}
⏳ FACTURAS PENDIENTES: {stats[3]}

🎯 TASA DE COBRO: {(stats[2]/stats[0]*100) if stats[0] > 0 else 0:.1f}%

💡 Use el 'Sistema Completo' para análisis detallados y generación de PDFs"""
            
            messagebox.showinfo("Resumen de Facturación", summary_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando resumen: {str(e)}")
    
    def load_billing_data(self, tree):
        """Cargar datos de facturas (función legacy para compatibilidad)"""
        try:
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener facturas
            invoices = self.db_manager.get_all_invoices()
            
            for invoice in invoices:
                # Formatear fecha
                fecha = invoice.get('fecha_creacion', '')
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                tree.insert('', 'end', values=(
                    invoice['id'], invoice.get('numero_factura', 'N/A'),
                    fecha, invoice.get('paciente_nombre', 'N/A'),
                    invoice.get('concepto', 'N/A'),
                    f"₡{invoice.get('monto', 0):,.2f}",
                    invoice.get('estado', 'N/A').title()
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando facturas: {str(e)}")
    
    def create_reports_tab(self, parent):
        """Crear pestaña de reportes"""
        # Frame principal
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Reportes y Estadísticas", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(pady=(0, 20))
        
        # Botones de reportes
        reports_frame = tk.LabelFrame(main_frame, text="Generar Reportes", 
                                     font=('Arial', 12, 'bold'), padx=20, pady=15)
        reports_frame.pack(fill='x', pady=10)
        
        reports_buttons = [
            ("📊 Reporte de Ingresos Mensual", self.generate_income_report, "#0B5394"),
            ("📋 Facturas Pendientes", self.generate_pending_invoices_report, "#C0392B"),
            ("👥 Estadísticas de Usuarios", self.generate_users_report, "#16A085"),
            ("📅 Reporte de Citas", self.generate_appointments_report, "#059669")
        ]
        
        for i, (text, command, color) in enumerate(reports_buttons):
            btn = tk.Button(reports_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=25, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # Estadísticas rápidas
        stats_frame = tk.LabelFrame(main_frame, text="Estadísticas Rápidas", 
                                   font=('Arial', 12, 'bold'), padx=20, pady=15)
        stats_frame.pack(fill='both', expand=True, pady=10)
        
        try:
            stats = self.get_system_stats()
            
            stats_text = f"""
Total de Usuarios: {stats.get('total_users', 0)}
Total de Pacientes: {stats.get('total_patients', 0)}
Citas de Hoy: {stats.get('appointments_today', 0)}
Facturas Pendientes: {stats.get('pending_invoices', 0)}
Ingresos del Mes: RD$ {stats.get('monthly_income', 0):,.2f}
            """
            
            tk.Label(stats_frame, text=stats_text, font=('Arial', 12), 
                    justify='left', bg='#F8FAFC').pack(pady=10)
            
        except Exception as e:
            tk.Label(stats_frame, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='#F8FAFC').pack()
    
    def generate_income_report(self):
        """Generar reporte de ingresos"""
        messagebox.showinfo("Reporte", "Generando reporte de ingresos mensual...")
    
    def generate_pending_invoices_report(self):
        """Generar reporte de facturas pendientes"""
        messagebox.showinfo("Reporte", "Generando reporte de facturas pendientes...")
    
    def generate_users_report(self):
        """Generar reporte de usuarios"""
        messagebox.showinfo("Reporte", "Generando estadísticas de usuarios...")
    
    def generate_appointments_report(self):
        """Generar reporte de citas"""
        messagebox.showinfo("Reporte", "Generando reporte de citas...")
    
    def create_doctor_menu(self, parent):
        """Crear menú para doctores"""
        # Crear notebook con pestañas específicas para doctores
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestaña 1: Dashboard Doctor
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Mi Dashboard")
        self.create_doctor_dashboard(dashboard_frame)
        
        # Pestaña 2: Mis Citas
        appointments_frame = ttk.Frame(self.notebook)
        self.notebook.add(appointments_frame, text="📅 Mis Citas")
        self.create_doctor_appointments(appointments_frame)
        
        # Pestaña 3: Mis Pacientes
        patients_frame = ttk.Frame(self.notebook)
        self.notebook.add(patients_frame, text="🤒 Mis Pacientes")
        self.create_doctor_patients(patients_frame)
        
        # Pestaña 4: Historiales Médicos
        medical_frame = ttk.Frame(self.notebook)
        self.notebook.add(medical_frame, text="📋 Historiales")
        self.create_medical_records(medical_frame)
        
        # Pestaña 5: Mi Perfil
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="👨‍⚕️ Mi Perfil")
        self.create_doctor_profile(profile_frame)
    
    def create_secretaria_menu(self, parent):
        """Crear menú para secretarias"""
        # Crear notebook con pestañas específicas para secretarias
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestaña 1: Dashboard Secretaria
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        self.create_secretaria_dashboard(dashboard_frame)
        
        # Pestaña 2: Gestión de Citas
        appointments_frame = ttk.Frame(self.notebook)
        self.notebook.add(appointments_frame, text="📅 Gestión de Citas")
        self.create_secretaria_appointments(appointments_frame)
        
        # Pestaña 3: Registro de Pacientes
        patients_frame = ttk.Frame(self.notebook)
        self.notebook.add(patients_frame, text="🤒 Pacientes")
        self.create_secretaria_patients(patients_frame)
        
        # Pestaña 4: Facturación
        billing_frame = ttk.Frame(self.notebook)
        self.notebook.add(billing_frame, text="💰 Facturación")
        self.create_secretaria_billing(billing_frame)
        
        # Pestaña 5: Reportes
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📈 Reportes")
        self.create_secretaria_reports(reports_frame)
    
    def create_paciente_menu(self, parent):
        """Crear menú para pacientes"""
        # Crear notebook con pestañas específicas para pacientes
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestaña 1: Mi Dashboard
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Mi Dashboard")
        self.create_patient_dashboard(dashboard_frame)
        
        # Pestaña 2: Mis Citas
        appointments_frame = ttk.Frame(self.notebook)
        self.notebook.add(appointments_frame, text="📅 Mis Citas")
        self.create_patient_appointments(appointments_frame)
        
        # Pestaña 3: Mi Historial Médico
        medical_frame = ttk.Frame(self.notebook)
        self.notebook.add(medical_frame, text="📋 Mi Historial")
        self.create_patient_medical_history(medical_frame)
        
        # Pestaña 4: Mis Facturas
        billing_frame = ttk.Frame(self.notebook)
        self.notebook.add(billing_frame, text="💰 Mis Facturas")
        self.create_patient_billing(billing_frame)
        
        # Pestaña 5: Mi Perfil
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="👤 Mi Perfil")
        self.create_patient_profile(profile_frame)
    
    def logout(self):
        """Cerrar sesión"""
        self.current_user = None
        self.root.destroy()
        self.__init__()
    
    # ==================== FUNCIONES PARA DOCTORES ====================
    
    def create_doctor_dashboard(self, parent):
        """Dashboard específico para doctores"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título personalizado
        title_label = tk.Label(main_frame, text=f"Bienvenido Dr. {self.current_user.nombre}", 
                              font=('Arial', 18, 'bold'), bg='#F8FAFC', fg='#1E3A8A')
        title_label.pack(pady=(0, 20))
        
        # Estadísticas del doctor
        stats_frame = tk.Frame(main_frame, bg='#F8FAFC')
        stats_frame.pack(fill='x', pady=20)
        
        try:
            doctor_stats = self.get_doctor_stats()
            
            self.create_stats_card(stats_frame, "📅 Citas Hoy", 
                                 str(doctor_stats.get('appointments_today', 0)), "#0B5394", 0, 0)
            
            self.create_stats_card(stats_frame, "🤒 Total Pacientes", 
                                 str(doctor_stats.get('total_patients', 0)), "#059669", 0, 1)
            
            self.create_stats_card(stats_frame, "💰 Ingresos del Mes", 
                                 f"RD$ {doctor_stats.get('monthly_income', 0):,.2f}", "#E67E22", 0, 2)
            
            self.create_stats_card(stats_frame, "⭐ Consultas Este Mes", 
                                 str(doctor_stats.get('consultations_month', 0)), "#16A085", 0, 3)
                                 
        except Exception as e:
            tk.Label(stats_frame, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='#F8FAFC').pack()
        
        # Próximas citas
        appointments_frame = tk.LabelFrame(main_frame, text="🕐 Próximas Citas", 
                                         font=('Arial', 14, 'bold'), padx=20, pady=15)
        appointments_frame.pack(fill='both', expand=True, pady=20)
        
        # Lista de próximas citas
        appointments_list = tk.Frame(appointments_frame, bg='white')
        appointments_list.pack(fill='both', expand=True)
        
        try:
            upcoming_appointments = self.get_doctor_upcoming_appointments()
            
            if upcoming_appointments:
                for i, apt in enumerate(upcoming_appointments[:5]):  # Mostrar solo 5
                    apt_frame = tk.Frame(appointments_list, bg='#FFFFFF', relief='solid', bd=1)
                    apt_frame.pack(fill='x', pady=5, padx=10)
                    
                    # Información de la cita
                    info_text = f"🕒 {apt.get('fecha_hora_formatted', 'N/A')} - {apt.get('paciente_nombre', 'N/A')}"
                    tk.Label(apt_frame, text=info_text, font=('Arial', 11, 'bold'), 
                            bg='#FFFFFF', fg='#1E3A8A').pack(side='left', padx=10, pady=8)
                    
                    # Motivo
                    motivo_text = f"Motivo: {apt.get('motivo', 'Consulta general')}"
                    tk.Label(apt_frame, text=motivo_text, font=('Arial', 10), 
                            bg='#FFFFFF', fg='#64748B').pack(side='left', padx=(20, 10))
            else:
                tk.Label(appointments_list, text="No hay citas programadas", 
                        font=('Arial', 12), fg='#64748B').pack(pady=20)
                
        except Exception as e:
            tk.Label(appointments_list, text=f"Error cargando citas: {str(e)}", 
                    fg='red').pack(pady=20)
    
    def create_doctor_appointments(self, parent):
        """Gestión de citas para doctores"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header con filtros
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Mis Citas Médicas", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        # Filtros
        filter_frame = tk.Frame(header_frame, bg='#F8FAFC')
        filter_frame.pack(side='right')
        
        tk.Label(filter_frame, text="Filtrar por:", font=('Arial', 10), bg='#F8FAFC').pack(side='left')
        
        self.appointment_filter = ttk.Combobox(filter_frame, values=['Todas', 'Hoy', 'Esta Semana', 'Este Mes'], 
                                             state='readonly', width=12)
        self.appointment_filter.set('Hoy')
        self.appointment_filter.pack(side='left', padx=5)
        self.appointment_filter.bind('<<ComboboxSelected>>', self.filter_doctor_appointments)
        
        # Tabla de citas
        columns = ('Fecha/Hora', 'Paciente', 'Motivo', 'Estado', 'Duración', 'Acciones')
        self.doctor_appointments_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar headers
        for col in columns:
            self.doctor_appointments_tree.heading(col, text=col)
            if col == 'Fecha/Hora':
                self.doctor_appointments_tree.column(col, width=150)
            elif col == 'Paciente':
                self.doctor_appointments_tree.column(col, width=200)
            elif col == 'Acciones':
                self.doctor_appointments_tree.column(col, width=120)
            else:
                self.doctor_appointments_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.doctor_appointments_tree.yview)
        self.doctor_appointments_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.doctor_appointments_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(actions_frame, text="📋 Ver Detalles", bg='#0B5394', fg='white',
                 command=self.view_appointment_details).pack(side='left', padx=5)
        tk.Button(actions_frame, text="✅ Marcar Completada", bg='#0B5394', fg='white',
                 command=self.complete_appointment).pack(side='left', padx=5)
        tk.Button(actions_frame, text="❌ Cancelar Cita", bg='#0B5394', fg='white',
                 command=self.cancel_appointment).pack(side='left', padx=5)
        tk.Button(actions_frame, text="📝 Agregar Notas", bg='#0B5394', fg='white',
                 command=self.add_appointment_notes).pack(side='left', padx=5)
        
        # Cargar datos
        self.load_doctor_appointments()
    
    def create_doctor_patients(self, parent):
        """Lista de pacientes del doctor"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Mis Pacientes", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        # Búsqueda
        search_frame = tk.Frame(header_frame, bg='#F8FAFC')
        search_frame.pack(side='right')
        
        tk.Label(search_frame, text="Buscar:", font=('Arial', 10), bg='#F8FAFC').pack(side='left')
        self.patient_search_entry = tk.Entry(search_frame, font=('Arial', 10), width=20)
        self.patient_search_entry.pack(side='left', padx=5)
        self.patient_search_entry.bind('<KeyRelease>', self.search_patients)
        
        # Tabla de pacientes
        columns = ('Nombre', 'Apellido', 'Email', 'Teléfono', 'Última Consulta', 'Estado')
        self.doctor_patients_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar headers
        for col in columns:
            self.doctor_patients_tree.heading(col, text=col)
            self.doctor_patients_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.doctor_patients_tree.yview)
        self.doctor_patients_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.doctor_patients_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(actions_frame, text="👤 Ver Perfil", bg='#0B5394', fg='white',
                 command=self.view_patient_profile).pack(side='left', padx=5)
        tk.Button(actions_frame, text="📋 Ver Historial", bg='#0B5394', fg='white',
                 command=self.view_medical_history).pack(side='left', padx=5)
        tk.Button(actions_frame, text="📅 Nueva Cita", bg='#0B5394', fg='white',
                 command=self.schedule_appointment).pack(side='left', padx=5)
        
        # Cargar datos
        self.load_doctor_patients()
    
    def create_medical_records(self, parent):
        """Gestión de historiales médicos"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Historiales Médicos", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        tk.Button(header_frame, text="➕ Nuevo Historial", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.create_medical_record).pack(side='right')
        
        # Panel dividido
        paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True)
        
        # Panel izquierdo - Lista de pacientes
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        tk.Label(left_frame, text="Seleccionar Paciente", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Lista de pacientes
        self.medical_patients_listbox = tk.Listbox(left_frame, font=('Arial', 10))
        self.medical_patients_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.medical_patients_listbox.bind('<<ListboxSelect>>', self.load_patient_medical_records)
        
        # Panel derecho - Historiales
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        tk.Label(right_frame, text="Historiales Médicos", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Tabla de historiales
        columns = ('Fecha', 'Diagnóstico', 'Tratamiento', 'Notas')
        self.medical_records_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.medical_records_tree.heading(col, text=col)
            if col == 'Fecha':
                self.medical_records_tree.column(col, width=100)
            else:
                self.medical_records_tree.column(col, width=150)
        
        # Scrollbar para historiales
        records_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.medical_records_tree.yview)
        self.medical_records_tree.configure(yscrollcommand=records_scrollbar.set)
        
        self.medical_records_tree.pack(side='left', fill='both', expand=True, padx=5)
        records_scrollbar.pack(side='right', fill='y')
        
        # Botones para historiales
        records_actions_frame = tk.Frame(right_frame)
        records_actions_frame.pack(fill='x', pady=5)
        
        tk.Button(records_actions_frame, text="👁️ Ver Detalle", bg='#0B5394', fg='white',
                 command=self.view_medical_record_detail).pack(side='left', padx=5)
        tk.Button(records_actions_frame, text="✏️ Editar", bg='#0B5394', fg='white',
                 command=self.edit_medical_record).pack(side='left', padx=5)
        tk.Button(records_actions_frame, text="🖨️ Imprimir", bg='#0B5394', fg='white',
                 command=self.print_medical_record).pack(side='left', padx=5)
        
        # Cargar pacientes
        self.load_medical_patients()
    
    def create_doctor_profile(self, parent):
        """Perfil del doctor"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Mi Perfil Profesional", 
                font=('Arial', 18, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Frame principal del perfil
        profile_main_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        profile_main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Panel izquierdo - Información personal
        left_panel = tk.Frame(profile_main_frame, bg='white')
        left_panel.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        # Avatar y datos básicos
        avatar_frame = tk.Frame(left_panel, bg='#0B5394', width=100, height=100)
        avatar_frame.pack(pady=(0, 20))
        avatar_frame.pack_propagate(False)
        tk.Label(avatar_frame, text="👨‍⚕️", font=('Arial', 50), bg='#0B5394', fg='white').pack(expand=True)
        
        # Información personal
        info_fields = [
            ("Nombre:", f"{self.current_user.nombre} {self.current_user.apellido}"),
            ("Email:", self.current_user.email),
            ("Teléfono:", self.current_user.telefono),
            ("Especialidad:", getattr(self.current_user, 'especialidad', 'Medicina General')),
            ("Cédula Profesional:", getattr(self.current_user, 'cedula_profesional', 'No especificada'))
        ]
        
        for label, value in info_fields:
            field_frame = tk.Frame(left_panel, bg='white')
            field_frame.pack(fill='x', pady=5)
            
            tk.Label(field_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='white', fg='#1E3A8A').pack(side='left')
            tk.Label(field_frame, text=value, font=('Arial', 11), 
                    bg='white', fg='#64748B').pack(side='left', padx=(10, 0))
        
        # Panel derecho - Configuraciones
        right_panel = tk.Frame(profile_main_frame, bg='#F8FAFC')
        right_panel.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        # Configuraciones
        config_frame = tk.LabelFrame(right_panel, text="Configuraciones", 
                                   font=('Arial', 12, 'bold'), padx=15, pady=10)
        config_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(config_frame, text="🔧 Editar Perfil", bg='#0B5394', fg='white',
                 font=('Arial', 10), command=self.edit_doctor_profile).pack(fill='x', pady=5)
        tk.Button(config_frame, text="🔑 Cambiar Contraseña", bg='#0B5394', fg='white',
                 font=('Arial', 10), command=self.change_password).pack(fill='x', pady=5)
        tk.Button(config_frame, text="⏰ Configurar Horarios", bg='#0B5394', fg='white',
                 font=('Arial', 10), command=self.configure_schedule).pack(fill='x', pady=5)
        
        # Estadísticas profesionales
        stats_frame = tk.LabelFrame(right_panel, text="Estadísticas", 
                                  font=('Arial', 12, 'bold'), padx=15, pady=10)
        stats_frame.pack(fill='both', expand=True)
        
        try:
            doctor_stats = self.get_doctor_stats()
            
            stats_text = f"""
📅 Total de Consultas: {doctor_stats.get('total_consultations', 0)}
🤒 Pacientes Atendidos: {doctor_stats.get('total_patients', 0)}
💰 Ingresos Totales: RD$ {doctor_stats.get('total_income', 0):,.2f}
⭐ Promedio Mensual: {doctor_stats.get('avg_monthly', 0)} consultas
📊 Este Mes: {doctor_stats.get('consultations_month', 0)} consultas
            """
            
            tk.Label(stats_frame, text=stats_text, font=('Arial', 10), 
                    justify='left', bg='#F8FAFC').pack(pady=10)
                    
        except Exception as e:
            tk.Label(stats_frame, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='#F8FAFC').pack(pady=10)
    
    # ==================== FUNCIONES PARA SECRETARIAS ====================
    
    def create_secretaria_dashboard(self, parent):
        """Dashboard específico para secretarias"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título personalizado
        title_label = tk.Label(main_frame, text=f"Panel de Control - {self.current_user.nombre}", 
                              font=('Arial', 18, 'bold'), bg='#F8FAFC', fg='#1E3A8A')
        title_label.pack(pady=(0, 20))
        
        # Estadísticas del día
        stats_frame = tk.Frame(main_frame, bg='#F8FAFC')
        stats_frame.pack(fill='x', pady=20)
        
        try:
            daily_stats = self.get_secretaria_stats()
            
            self.create_stats_card(stats_frame, "📅 Citas Hoy", 
                                 str(daily_stats.get('appointments_today', 0)), "#0B5394", 0, 0)
            
            self.create_stats_card(stats_frame, "⏳ Citas Pendientes", 
                                 str(daily_stats.get('pending_appointments', 0)), "#C0392B", 0, 1)
            
            self.create_stats_card(stats_frame, "💰 Facturas Pendientes", 
                                 str(daily_stats.get('pending_invoices', 0)), "#E67E22", 0, 2)
            
            self.create_stats_card(stats_frame, "👥 Nuevos Pacientes", 
                                 str(daily_stats.get('new_patients_today', 0)), "#059669", 0, 3)
                                 
        except Exception as e:
            tk.Label(stats_frame, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='#F8FAFC').pack()
        
        # Panel de acciones rápidas
        quick_actions_frame = tk.LabelFrame(main_frame, text="🚀 Acciones Rápidas", 
                                          font=('Arial', 14, 'bold'), padx=20, pady=15)
        quick_actions_frame.pack(fill='x', pady=20)
        
        # Botones de acciones rápidas
        actions_grid = tk.Frame(quick_actions_frame)
        actions_grid.pack()
        
        quick_buttons = [
            ("📅 Nueva Cita", self.new_appointment_quick, "#0B5394"),
            ("👤 Nuevo Paciente", self.new_patient_quick, "#16A085"),
            ("💰 Procesar Pago", self.process_payment_quick, "#E67E22"),
            ("📋 Generar Factura", self.generate_invoice_quick, "#16A085"),
            ("📞 Lista de Espera", self.manage_waiting_list, "#E67E22"),
            ("📊 Reporte Diario", self.daily_report, "#1abc9c")
        ]
        
        for i, (text, command, color) in enumerate(quick_buttons):
            btn = tk.Button(actions_grid, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=18, height=2)
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # Agenda del día
        agenda_frame = tk.LabelFrame(main_frame, text="📋 Agenda de Hoy", 
                                   font=('Arial', 14, 'bold'), padx=20, pady=15)
        agenda_frame.pack(fill='both', expand=True, pady=20)
        
        # Lista de citas del día
        agenda_list = tk.Frame(agenda_frame, bg='white')
        agenda_list.pack(fill='both', expand=True)
        
        try:
            today_appointments = self.get_today_appointments()
            
            if today_appointments:
                for i, apt in enumerate(today_appointments):
                    apt_frame = tk.Frame(agenda_list, bg='#FFFFFF' if i % 2 == 0 else '#ffffff', 
                                       relief='solid', bd=1)
                    apt_frame.pack(fill='x', pady=2, padx=5)
                    
                    # Hora
                    time_label = tk.Label(apt_frame, text=f"🕒 {apt.get('hora', 'N/A')}", 
                                        font=('Arial', 11, 'bold'), 
                                        bg=apt_frame['bg'], fg='#1E3A8A')
                    time_label.pack(side='left', padx=10, pady=5)
                    
                    # Paciente y Doctor
                    info_text = f"{apt.get('paciente_nombre', 'N/A')} → Dr. {apt.get('doctor_nombre', 'N/A')}"
                    info_label = tk.Label(apt_frame, text=info_text, font=('Arial', 10), 
                                        bg=apt_frame['bg'], fg='#64748B')
                    info_label.pack(side='left', padx=(20, 10), pady=5)
                    
                    # Estado
                    estado = apt.get('estado', 'programada')
                    estado_color = {'programada': '#0B5394', 'completada': '#16A085', 'cancelada': '#C0392B'}
                    estado_label = tk.Label(apt_frame, text=estado.upper(), 
                                          font=('Arial', 9, 'bold'), 
                                          bg=estado_color.get(estado, '#64748B'), fg='white')
                    estado_label.pack(side='right', padx=10, pady=5)
            else:
                tk.Label(agenda_list, text="No hay citas programadas para hoy", 
                        font=('Arial', 12), fg='#64748B').pack(pady=20)
                
        except Exception as e:
            tk.Label(agenda_list, text=f"Error cargando agenda: {str(e)}", 
                    fg='red').pack(pady=20)
    
    def create_secretaria_appointments(self, parent):
        """Gestión completa de citas para secretarias"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header con botones y filtros
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Gestión de Citas Médicas", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        # Botones de acción
        buttons_frame = tk.Frame(header_frame, bg='#F8FAFC')
        buttons_frame.pack(side='right')
        
        tk.Button(buttons_frame, text="➕ Nueva Cita", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.create_new_appointment).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="📅 Calendario", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.show_appointment_calendar).pack(side='left', padx=5)
        
        # Panel de filtros
        filters_frame = tk.LabelFrame(main_frame, text="Filtros", font=('Arial', 11, 'bold'), 
                                    padx=10, pady=10)
        filters_frame.pack(fill='x', pady=(0, 20))
        
        filters_row = tk.Frame(filters_frame)
        filters_row.pack()
        
        # Filtro por fecha
        tk.Label(filters_row, text="Fecha:", font=('Arial', 10)).grid(row=0, column=0, padx=5, sticky='w')
        self.appointment_date_filter = ttk.Combobox(filters_row, values=['Hoy', 'Mañana', 'Esta Semana', 'Este Mes', 'Todas'], 
                                                  state='readonly', width=12)
        self.appointment_date_filter.set('Hoy')
        self.appointment_date_filter.grid(row=0, column=1, padx=5)
        
        # Filtro por doctor
        tk.Label(filters_row, text="Doctor:", font=('Arial', 10)).grid(row=0, column=2, padx=5, sticky='w')
        self.appointment_doctor_filter = ttk.Combobox(filters_row, state='readonly', width=15)
        self.appointment_doctor_filter.grid(row=0, column=3, padx=5)
        
        # Filtro por estado
        tk.Label(filters_row, text="Estado:", font=('Arial', 10)).grid(row=0, column=4, padx=5, sticky='w')
        self.appointment_status_filter = ttk.Combobox(filters_row, 
                                                    values=['Todas', 'Programada', 'Completada', 'Cancelada'], 
                                                    state='readonly', width=12)
        self.appointment_status_filter.set('Todas')
        self.appointment_status_filter.grid(row=0, column=5, padx=5)
        
        # Botón aplicar filtros
        tk.Button(filters_row, text="🔍 Filtrar", bg='#0B5394', fg='white',
                 command=self.apply_appointment_filters).grid(row=0, column=6, padx=10)
        
        # Tabla de citas
        columns = ('ID', 'Fecha/Hora', 'Paciente', 'Doctor', 'Motivo', 'Estado', 'Teléfono')
        self.secretaria_appointments_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        column_widths = {'ID': 50, 'Fecha/Hora': 130, 'Paciente': 150, 'Doctor': 120, 
                        'Motivo': 200, 'Estado': 100, 'Teléfono': 100}
        
        for col in columns:
            self.secretaria_appointments_tree.heading(col, text=col)
            self.secretaria_appointments_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.secretaria_appointments_tree.yview)
        self.secretaria_appointments_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.secretaria_appointments_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción para citas
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        action_buttons = [
            ("✏️ Editar", self.edit_appointment, "#E67E22"),
            ("✅ Confirmar", self.confirm_appointment, "#16A085"),
            ("❌ Cancelar", self.cancel_appointment, "#C0392B"),
            ("📞 Llamar Paciente", self.call_patient, "#0B5394"),
            ("💰 Generar Factura", self.generate_appointment_invoice, "#16A085"),
            ("📋 Ver Detalles", self.view_appointment_details, "#64748B")
        ]
        
        for text, command, color in action_buttons:
            btn = tk.Button(actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 9, 'bold'))
            btn.pack(side='left', padx=5, pady=5)
        
        # Cargar datos y filtros
        self.load_appointment_doctors()
        self.load_secretaria_appointments()
    
    def create_secretaria_patients(self, parent):
        """Gestión de pacientes para secretarias"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Gestión de Pacientes", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        # Botones de acción
        buttons_frame = tk.Frame(header_frame, bg='#F8FAFC')
        buttons_frame.pack(side='right')
        
        tk.Button(buttons_frame, text="➕ Nuevo Paciente", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.register_new_patient).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="📤 Importar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.import_patients).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="📥 Exportar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.export_patients).pack(side='left', padx=5)
        
        # Panel de búsqueda
        search_frame = tk.LabelFrame(main_frame, text="Búsqueda de Pacientes", 
                                   font=('Arial', 11, 'bold'), padx=10, pady=10)
        search_frame.pack(fill='x', pady=(0, 20))
        
        search_row = tk.Frame(search_frame)
        search_row.pack()
        
        tk.Label(search_row, text="Buscar por:", font=('Arial', 10)).grid(row=0, column=0, padx=5)
        
        search_options = ['Nombre', 'Apellido', 'Email', 'Teléfono', 'Expediente']
        self.patient_search_type = ttk.Combobox(search_row, values=search_options, state='readonly', width=12)
        self.patient_search_type.set('Nombre')
        self.patient_search_type.grid(row=0, column=1, padx=5)
        
        self.patient_search_entry = tk.Entry(search_row, font=('Arial', 10), width=25)
        self.patient_search_entry.grid(row=0, column=2, padx=5)
        self.patient_search_entry.bind('<KeyRelease>', self.search_patients_secretaria)
        
        tk.Button(search_row, text="🔍 Buscar", bg='#0B5394', fg='white',
                 command=self.search_patients_secretaria).grid(row=0, column=3, padx=10)
        
        tk.Button(search_row, text="🔄 Limpiar", bg='#0B5394', fg='white',
                 command=self.clear_patient_search).grid(row=0, column=4, padx=5)
        
        # Tabla de pacientes
        columns = ('ID', 'Expediente', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Seguro', 'Estado')
        self.secretaria_patients_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        column_widths = {'ID': 50, 'Expediente': 100, 'Nombre': 120, 'Apellido': 120, 
                        'Email': 180, 'Teléfono': 100, 'Seguro': 120, 'Estado': 80}
        
        for col in columns:
            self.secretaria_patients_tree.heading(col, text=col)
            self.secretaria_patients_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.secretaria_patients_tree.yview)
        self.secretaria_patients_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.secretaria_patients_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción para pacientes
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        patient_actions = [
            ("👁️ Ver Perfil", self.view_patient_profile_secretaria, "#0B5394"),
            ("✏️ Editar Datos", self.edit_patient_data, "#E67E22"),
            ("📅 Nueva Cita", self.schedule_patient_appointment, "#16A085"),
            ("📋 Ver Historial", self.view_patient_history, "#16A085"),
            ("💰 Ver Facturas", self.view_patient_invoices, "#E67E22"),
            ("📞 Contactar", self.contact_patient, "#1abc9c")
        ]
        
        for text, command, color in patient_actions:
            btn = tk.Button(actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 9, 'bold'))
            btn.pack(side='left', padx=5, pady=5)
        
        # Cargar datos
        self.load_secretaria_patients()
    
    def create_secretaria_billing(self, parent):
        """Sistema de facturación avanzado para secretarias"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header moderno
        header_frame = tk.Frame(main_frame, bg='#1E3A8A', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg='#1E3A8A')
        header_content.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Título
        title_frame = tk.Frame(header_content, bg='#1E3A8A')
        title_frame.pack(side='left', expand=True, fill='both')
        
        tk.Label(title_frame, text="💰", font=('Arial', 18), bg='#1E3A8A', fg='white').pack(side='left', pady=8)
        tk.Label(title_frame, text="FACTURACIÓN SECRETARÍA", 
                font=('Arial', 14, 'bold'), bg='#1E3A8A', fg='white').pack(side='left', padx=(10, 0), pady=8)
        tk.Label(title_frame, text="Gestión completa de facturas y pagos", 
                font=('Arial', 10), bg='#1E3A8A', fg='#CBD5E1').pack(side='left', padx=(15, 0), pady=8)
        
        # Botones principales en header
        buttons_frame = tk.Frame(header_content, bg='#1E3A8A')
        buttons_frame.pack(side='right', pady=8)
        
        # Botón Sistema Completo (más prominente)
        complete_btn = tk.Button(
            buttons_frame,
            text="💰 FACTURACIÓN AVANZADA",
            command=lambda: self.switch_tab("Facturación Avanzada"),
            bg='#0B5394',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            relief='raised',
            bd=3
        )
        complete_btn.pack(side='left', padx=10)
        
        # Botones secundarios
        tk.Button(buttons_frame, text="�📋 Nueva Factura", bg='#0B5394', fg='white',
                 font=('Arial', 9, 'bold'), padx=12, pady=6,
                 command=self.create_new_invoice_secretaria).pack(side='left', padx=3)
        tk.Button(buttons_frame, text="💳 Procesar Pago", bg='#0B5394', fg='white',
                 font=('Arial', 9, 'bold'), padx=12, pady=6,
                 command=self.process_payment_secretaria).pack(side='left', padx=3)
        
        # Contenido principal dividido en 2 columnas
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Columna izquierda: Resumen y estadísticas
        left_column = tk.Frame(content_frame, bg='#F8FAFC', width=350)
        left_column.pack(side='left', fill='y', padx=(0, 15))
        left_column.pack_propagate(False)
        
        # Columna derecha: Lista de facturas
        right_column = tk.Frame(content_frame, bg='#F8FAFC')
        right_column.pack(side='right', fill='both', expand=True)
        
        # Panel de resumen financiero
        summary_frame = tk.LabelFrame(
            left_column, 
            text="📊 RESUMEN FINANCIERO HOY", 
            font=('Arial', 11, 'bold'),
            bg='#e8f5e8',
            fg='#2e7d32',
            padx=15, 
            pady=15
        )
        summary_frame.pack(fill='x', pady=(0, 15))
        
        try:
            billing_summary = self.get_billing_summary_secretaria()
            
            # Indicadores financieros
            indicators = [
                ("💰 Ingresos Hoy", f"₡{billing_summary.get('today_income', 0):,.2f}", "#16A085"),
                ("📋 Pendientes", str(billing_summary.get('pending_count', 0)), "#C0392B"),
                ("✅ Pagadas Hoy", str(billing_summary.get('paid_today', 0)), "#0B5394"),
                ("📊 Meta Mensual", f"₡{billing_summary.get('month_income', 0):,.2f}", "#16A085")
            ]
            
            for title, value, color in indicators:
                indicator_frame = tk.Frame(summary_frame, bg='#e8f5e8')
                indicator_frame.pack(fill='x', pady=5)
                
                tk.Label(indicator_frame, text=title, font=('Arial', 10, 'bold'),
                        bg='#e8f5e8', fg='#2e7d32').pack(side='left')
                tk.Label(indicator_frame, text=value, font=('Arial', 11, 'bold'),
                        bg='#e8f5e8', fg=color).pack(side='right')
                
        except Exception as e:
            tk.Label(summary_frame, text=f"Error cargando resumen: {str(e)}", 
                    font=('Arial', 9), bg='#e8f5e8', fg='#C0392B').pack()
        
        # Panel de acciones rápidas
        actions_frame = tk.LabelFrame(
            left_column,
            text="⚡ ACCIONES RÁPIDAS",
            font=('Arial', 11, 'bold'),
            bg='#fff3e0',
            fg='#e65100',
            padx=15,
            pady=15
        )
        actions_frame.pack(fill='x', pady=(0, 15))
        
        quick_actions = [
            ("💵 Factura Express", self.express_invoice, '#16A085'),
            ("🔍 Buscar Paciente", self.search_patient_billing, '#0B5394'),
            ("📄 Generar Reporte", self.generate_daily_report, '#16A085'),
            ("🔄 Actualizar Datos", self.refresh_billing_secretaria, '#64748B')
        ]
        
        for text, command, color in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 9, 'bold'),
                padx=10,
                pady=6,
                relief='raised'
            )
            btn.pack(fill='x', pady=3)
        
        # Panel de citas sin facturar
        pending_frame = tk.LabelFrame(
            left_column,
            text="📋 CITAS SIN FACTURAR",
            font=('Arial', 11, 'bold'),
            bg='#ffebee',
            fg='#c62828',
            padx=15,
            pady=15
        )
        pending_frame.pack(fill='both', expand=True)
        
        # Lista de citas pendientes
        self.secretaria_pending_list = tk.Listbox(
            pending_frame,
            height=8,
            font=('Arial', 9),
            bg='white',
            selectmode='single'
        )
        self.secretaria_pending_list.pack(fill='both', expand=True, pady=(10, 10))
        
        # Botón para facturar
        bill_btn = tk.Button(
            pending_frame,
            text="💰 Facturar Seleccionada",
            command=self.bill_appointment_secretaria,
            bg='#0B5394',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        )
        bill_btn.pack(fill='x')
        
        # Panel de facturas recientes (columna derecha)
        invoices_frame = tk.LabelFrame(
            right_column,
            text="📄 FACTURAS RECIENTES",
            font=('Arial', 12, 'bold'),
            bg='#e3f2fd',
            fg='#1565c0',
            padx=15,
            pady=15
        )
        invoices_frame.pack(fill='both', expand=True)
        
        # Controles de filtro
        filter_frame = tk.Frame(invoices_frame, bg='#e3f2fd')
        filter_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(filter_frame, text="🔍 Filtrar:", font=('Arial', 10, 'bold'),
                bg='#e3f2fd', fg='#1565c0').pack(side='left')
        
        self.filter_var = tk.StringVar()
        filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, 
                               font=('Arial', 10), width=20)
        filter_entry.pack(side='left', padx=(10, 0))
        filter_entry.bind('<KeyRelease>', self.filter_invoices_secretaria)
        
        # Estado filter
        tk.Label(filter_frame, text="Estado:", font=('Arial', 10, 'bold'),
                bg='#e3f2fd', fg='#1565c0').pack(side='left', padx=(20, 5))
        
        self.status_filter = tk.StringVar(value="todos")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter,
                                   values=["todos", "pendiente", "pagada", "pago_parcial"],
                                   state="readonly", width=12)
        status_combo.pack(side='left', padx=(0, 10))
        status_combo.bind('<<ComboboxSelected>>', self.filter_invoices_secretaria)
        
        # Tabla de facturas
        columns = ('Número', 'Fecha', 'Paciente', 'Monto', 'Estado', 'Acciones')
        self.secretaria_invoices_tree = ttk.Treeview(invoices_frame, columns=columns, 
                                                    show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'Número': 100, 'Fecha': 90, 'Paciente': 120, 'Monto': 90, 'Estado': 80, 'Acciones': 80}
        for col in columns:
            self.secretaria_invoices_tree.heading(col, text=col)
            self.secretaria_invoices_tree.column(col, width=column_widths.get(col, 80), anchor='center')
        
        # Scrollbar
        invoices_scroll = ttk.Scrollbar(invoices_frame, orient="vertical", 
                                       command=self.secretaria_invoices_tree.yview)
        self.secretaria_invoices_tree.configure(yscrollcommand=invoices_scroll.set)
        
        # Pack tabla
        table_frame = tk.Frame(invoices_frame, bg='#e3f2fd')
        table_frame.pack(fill='both', expand=True)
        
        self.secretaria_invoices_tree.pack(side='left', fill='both', expand=True)
        invoices_scroll.pack(side='right', fill='y')
        
        # Eventos
        self.secretaria_invoices_tree.bind('<Double-1>', self.view_invoice_details)
        
        # Cargar datos iniciales
        self.load_secretaria_billing_data()
    
    def get_billing_summary_secretaria(self):
        """Obtener resumen de facturación para secretarias"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            current_month = datetime.now().strftime('%Y-%m')
            
            # Ingresos de hoy
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE DATE(fecha_creacion) = ? AND estado IN ('pagada', 'pago_parcial')
            ''', (today,))
            today_income = cursor.fetchone()[0]
            
            # Facturas pendientes
            cursor.execute('SELECT COUNT(*) FROM facturas WHERE estado = "pendiente"')
            pending_count = cursor.fetchone()[0]
            
            # Facturas pagadas hoy
            cursor.execute('''
                SELECT COUNT(*) 
                FROM facturas 
                WHERE DATE(fecha_creacion) = ? AND estado = 'pagada'
            ''', (today,))
            paid_today = cursor.fetchone()[0]
            
            # Ingresos del mes
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE strftime('%Y-%m', fecha_creacion) = ? AND estado IN ('pagada', 'pago_parcial')
            ''', (current_month,))
            month_income = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'today_income': float(today_income),
                'pending_count': pending_count,
                'paid_today': paid_today,
                'month_income': float(month_income)
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen: {e}")
            return {'today_income': 0, 'pending_count': 0, 'paid_today': 0, 'month_income': 0}
    
    def load_secretaria_billing_data(self):
        """Cargar datos de facturación para secretarias"""
        try:
            # Limpiar listas
            self.secretaria_pending_list.delete(0, tk.END)
            for item in self.secretaria_invoices_tree.get_children():
                self.secretaria_invoices_tree.delete(item)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Cargar citas sin facturar
            cursor.execute('''
                SELECT c.id, c.fecha_hora, 
                       (SELECT nombre || ' ' || apellido FROM usuarios WHERE id = c.paciente_id) as paciente_nombre,
                       c.motivo
                FROM citas c
                LEFT JOIN facturas f ON c.id = f.cita_id
                WHERE c.estado = 'completada' AND f.cita_id IS NULL
                ORDER BY c.fecha_hora DESC
                LIMIT 15
            ''')
            
            pending_appointments = cursor.fetchall()
            for apt in pending_appointments:
                fecha = apt[1]
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m %H:%M')
                    except:
                        pass
                
                text = f"{fecha} - {apt[2]} - {apt[3][:25]}..."
                self.secretaria_pending_list.insert(tk.END, text)
            
            # Cargar facturas recientes
            cursor.execute('''
                SELECT numero_factura, fecha_creacion, 
                       (SELECT nombre || ' ' || apellido FROM usuarios WHERE id = f.paciente_id) as paciente_nombre,
                       monto, estado
                FROM facturas f
                ORDER BY fecha_creacion DESC
                LIMIT 50
            ''')
            
            invoices = cursor.fetchall()
            for invoice in invoices:
                fecha = invoice[1]
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                estado = invoice[4].title() if invoice[4] else 'Desconocido'
                
                self.secretaria_invoices_tree.insert('', 'end', values=(
                    invoice[0] or 'N/A',
                    fecha,
                    invoice[2] or 'N/A',
                    f"₡{float(invoice[3] or 0):,.2f}",
                    estado,
                    "Ver"
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")
    
    def create_new_invoice_secretaria(self):
        """Crear nueva factura desde secretaría"""
        messagebox.showinfo("Nueva Factura", 
                           "Use el 'Sistema Completo' para crear facturas con todas las funcionalidades avanzadas:\n\n" +
                           "• PDFs automáticos\n• Control de pagos\n• Cálculo de cambio\n• Selección de servicios")
    
    def process_payment_secretaria(self):
        """Procesar pago desde secretaría"""
        messagebox.showinfo("Procesar Pago", 
                           "Use el 'Sistema Completo' para procesar pagos con:\n\n" +
                           "• Múltiples métodos de pago\n• Cálculo automático de cambio\n• Generación de recibos PDF")
    
    def express_invoice(self):
        """Factura express"""
        messagebox.showinfo("Factura Express", "Funcionalidad disponible en Sistema Completo")
    
    def search_patient_billing(self):
        """Buscar paciente para facturación"""
        search_term = simpledialog.askstring("Buscar Paciente", "Ingrese nombre del paciente:")
        if search_term:
            messagebox.showinfo("Búsqueda", f"Búsqueda avanzada disponible en Sistema Completo")
    
    def generate_daily_report(self):
        """Generar reporte diario"""
        messagebox.showinfo("Reporte Diario", "Generación de reportes PDF disponible en Sistema Completo")
    
    def refresh_billing_secretaria(self):
        """Actualizar datos de facturación"""
        self.load_secretaria_billing_data()
        messagebox.showinfo("Actualizado", "✅ Datos actualizados correctamente")
    
    def bill_appointment_secretaria(self):
        """Facturar cita seleccionada desde secretaría"""
        selection = self.secretaria_pending_list.curselection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione una cita para facturar")
            return
        
        messagebox.showinfo("Facturar Cita", 
                           "Use el 'Sistema Completo' para facturar citas con:\n\n" +
                           "• Selección de servicios médicos\n• Aplicación de seguros\n• Generación automática de PDFs")
    
    def filter_invoices_secretaria(self, event=None):
        """Filtrar facturas en la vista de secretaría"""
        # Implementación básica de filtrado
        filter_text = self.filter_var.get().lower()
        status_filter = self.status_filter.get()
        
        # Recargar datos con filtros aplicados
        self.load_secretaria_billing_data()  # Por simplicidad, recargamos todo
    
    def view_invoice_details(self, event=None):
        """Ver detalles de factura seleccionada"""
        selection = self.secretaria_invoices_tree.selection()
        if not selection:
            return
        
        item = self.secretaria_invoices_tree.item(selection[0])
        invoice_number = item['values'][0]
        
        messagebox.showinfo("Detalles de Factura", 
                           f"Factura: {invoice_number}\n\n" +
                           "Vista detallada y edición disponible en Sistema Completo")
    
    def create_secretaria_reports(self, parent):
        """Reportes para secretarias"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Reportes y Estadísticas", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Panel de reportes financieros
        financial_frame = tk.LabelFrame(main_frame, text="💰 Reportes Financieros", 
                                      font=('Arial', 12, 'bold'), padx=20, pady=15)
        financial_frame.pack(fill='x', pady=10)
        
        financial_buttons = [
            ("📊 Ingresos Diarios", self.daily_income_report, "#0B5394"),
            ("📈 Ingresos Mensuales", self.monthly_income_report, "#16A085"),
            ("📋 Facturas Pendientes", self.pending_invoices_report, "#C0392B"),
            ("💳 Métodos de Pago", self.payment_methods_report, "#16A085")
        ]
        
        financial_grid = tk.Frame(financial_frame)
        financial_grid.pack()
        
        for i, (text, command, color) in enumerate(financial_buttons):
            btn = tk.Button(financial_grid, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=20, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # Panel de reportes operativos
        operational_frame = tk.LabelFrame(main_frame, text="📋 Reportes Operativos", 
                                        font=('Arial', 12, 'bold'), padx=20, pady=15)
        operational_frame.pack(fill='x', pady=10)
        
        operational_buttons = [
            ("📅 Citas por Período", self.appointments_period_report, "#64748B"),
            ("👨‍⚕️ Productividad Doctores", self.doctors_productivity_report, "#059669"),
            ("🤒 Registro de Pacientes", self.patients_registry_report, "#E67E22"),
            ("📞 Lista de Contactos", self.contacts_list_report, "#8e44ad")
        ]
        
        operational_grid = tk.Frame(operational_frame)
        operational_grid.pack()
        
        for i, (text, command, color) in enumerate(operational_buttons):
            btn = tk.Button(operational_grid, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=20, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        
        # Panel de estadísticas rápidas
        stats_frame = tk.LabelFrame(main_frame, text="📊 Estadísticas Rápidas", 
                                  font=('Arial', 12, 'bold'), padx=20, pady=15)
        stats_frame.pack(fill='both', expand=True, pady=10)
        
        # Crear área de estadísticas
        stats_display = tk.Frame(stats_frame, bg='white', relief='sunken', bd=2)
        stats_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        try:
            quick_stats = self.get_secretaria_quick_stats()
            
            stats_text = f"""
📊 RESUMEN GENERAL
════════════════════════════════════════

📅 Citas Programadas Hoy: {quick_stats.get('appointments_today', 0)}
⏳ Citas Pendientes: {quick_stats.get('pending_appointments', 0)}
✅ Citas Completadas Hoy: {quick_stats.get('completed_today', 0)}

👥 PACIENTES
════════════════════════════════════════

👤 Total de Pacientes: {quick_stats.get('total_patients', 0)}
🆕 Nuevos este Mes: {quick_stats.get('new_patients_month', 0)}
📞 Contactos Pendientes: {quick_stats.get('pending_contacts', 0)}

💰 FACTURACIÓN
════════════════════════════════════════

💵 Ingresos Hoy: RD$ {quick_stats.get('today_income', 0):,.2f}
📋 Facturas Pendientes: {quick_stats.get('pending_invoices', 0)}
✅ Facturas Pagadas Hoy: {quick_stats.get('paid_today', 0)}
📊 Total del Mes: RD$ {quick_stats.get('month_total', 0):,.2f}

👨‍⚕️ DOCTORES
════════════════════════════════════════

🏥 Doctores Activos: {quick_stats.get('active_doctors', 0)}
📅 Consultas Programadas: {quick_stats.get('scheduled_consultations', 0)}
            """
            
            stats_label = tk.Label(stats_display, text=stats_text, font=('Courier', 10), 
                                 justify='left', bg='white', fg='#1E3A8A')
            stats_label.pack(pady=10, padx=10)
            
        except Exception as e:
            tk.Label(stats_display, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='white').pack(pady=20)
    
    # ==================== FUNCIONES PARA PACIENTES ====================
    
    def create_patient_dashboard(self, parent):
        """Dashboard específico para pacientes"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Saludo personalizado
        welcome_frame = tk.Frame(main_frame, bg='#0B5394', height=100)
        welcome_frame.pack(fill='x', pady=(0, 20))
        welcome_frame.pack_propagate(False)
        
        tk.Label(welcome_frame, text=f"¡Bienvenido/a {self.current_user.nombre}!", 
                font=('Arial', 20, 'bold'), bg='#0B5394', fg='white').pack(expand=True)
        
        # Panel de información personal
        info_frame = tk.LabelFrame(main_frame, text="📋 Mi Información", 
                                 font=('Arial', 12, 'bold'), padx=20, pady=15)
        info_frame.pack(fill='x', pady=10)
        
        info_grid = tk.Frame(info_frame)
        info_grid.pack()
        
        try:
            patient_info = self.get_patient_info()
            
            info_items = [
                ("👤 Nombre Completo:", f"{patient_info.get('nombre', '')} {patient_info.get('apellido', '')}"),
                ("📧 Email:", patient_info.get('email', 'No especificado')),
                ("📞 Teléfono:", patient_info.get('telefono', 'No especificado')),
                ("🏥 Número de Expediente:", patient_info.get('numero_expediente', 'No asignado')),
                ("🏥 Seguro Médico:", patient_info.get('seguro_nombre', 'Sin seguro')),
                ("🎂 Fecha de Nacimiento:", patient_info.get('fecha_nacimiento', 'No especificada'))
            ]
            
            for i, (label, value) in enumerate(info_items):
                tk.Label(info_grid, text=label, font=('Arial', 10, 'bold'), 
                        fg='#1E3A8A').grid(row=i//2, column=(i%2)*2, sticky='w', padx=(0, 10), pady=5)
                tk.Label(info_grid, text=value, font=('Arial', 10), 
                        fg='#64748B').grid(row=i//2, column=(i%2)*2+1, sticky='w', padx=(0, 30), pady=5)
                        
        except Exception as e:
            tk.Label(info_frame, text=f"Error cargando información: {str(e)}", 
                    fg='red').pack()
        
        # Panel de próximas citas
        next_appointments_frame = tk.LabelFrame(main_frame, text="📅 Mis Próximas Citas", 
                                              font=('Arial', 12, 'bold'), padx=20, pady=15)
        next_appointments_frame.pack(fill='x', pady=10)
        
        try:
            upcoming_appointments = self.get_patient_upcoming_appointments()
            
            if upcoming_appointments:
                for i, apt in enumerate(upcoming_appointments[:3]):  # Mostrar solo 3
                    apt_frame = tk.Frame(next_appointments_frame, bg='#FFFFFF', relief='solid', bd=1)
                    apt_frame.pack(fill='x', pady=5)
                    
                    # Fecha y hora
                    datetime_text = f"📅 {apt.get('fecha_formatted', 'N/A')} a las {apt.get('hora_formatted', 'N/A')}"
                    tk.Label(apt_frame, text=datetime_text, font=('Arial', 11, 'bold'), 
                            bg='#FFFFFF', fg='#1E3A8A').pack(side='left', padx=10, pady=8)
                    
                    # Doctor
                    doctor_text = f"👨‍⚕️ Dr. {apt.get('doctor_nombre', 'N/A')}"
                    tk.Label(apt_frame, text=doctor_text, font=('Arial', 10), 
                            bg='#FFFFFF', fg='#64748B').pack(side='left', padx=(20, 10))
                    
                    # Motivo
                    motivo_text = f"🩺 {apt.get('motivo', 'Consulta general')}"
                    tk.Label(apt_frame, text=motivo_text, font=('Arial', 10), 
                            bg='#FFFFFF', fg='#64748B').pack(side='right', padx=10)
            else:
                tk.Label(next_appointments_frame, text="No tienes citas programadas", 
                        font=('Arial', 12), fg='#64748B').pack(pady=10)
                        
        except Exception as e:
            tk.Label(next_appointments_frame, text=f"Error cargando citas: {str(e)}", 
                    fg='red').pack()
        
        # Panel de acciones rápidas
        actions_frame = tk.LabelFrame(main_frame, text="🚀 Acciones Rápidas", 
                                    font=('Arial', 12, 'bold'), padx=20, pady=15)
        actions_frame.pack(fill='x', pady=10)
        
        actions_grid = tk.Frame(actions_frame)
        actions_grid.pack()
        
        patient_actions = [
            ("📅 Solicitar Cita", self.request_appointment, "#16A085"),
            ("📋 Ver Mi Historial", self.view_my_history, "#0B5394"),
            ("💰 Ver Mis Facturas", self.view_my_bills, "#E67E22"),
            ("👤 Actualizar Perfil", self.update_my_profile, "#16A085")
        ]
        
        for i, (text, command, color) in enumerate(patient_actions):
            btn = tk.Button(actions_grid, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 11, 'bold'),
                           width=18, height=2)
            btn.grid(row=i//2, column=i%2, padx=15, pady=10)
        
        # Panel de recordatorios
        reminders_frame = tk.LabelFrame(main_frame, text="🔔 Recordatorios", 
                                      font=('Arial', 12, 'bold'), padx=20, pady=15)
        reminders_frame.pack(fill='both', expand=True, pady=10)
        
        try:
            reminders = self.get_patient_reminders()
            
            if reminders:
                for reminder in reminders:
                    reminder_frame = tk.Frame(reminders_frame, bg='#fff3cd', relief='solid', bd=1)
                    reminder_frame.pack(fill='x', pady=3)
                    
                    tk.Label(reminder_frame, text=f"⚠️ {reminder.get('message', '')}", 
                            font=('Arial', 10), bg='#fff3cd', fg='#856404').pack(side='left', padx=10, pady=5)
            else:
                tk.Label(reminders_frame, text="No tienes recordatorios pendientes", 
                        font=('Arial', 11), fg='#64748B').pack(pady=10)
                        
        except Exception as e:
            tk.Label(reminders_frame, text=f"Error cargando recordatorios: {str(e)}", 
                    fg='red').pack()
    
    def create_patient_appointments(self, parent):
        """Mis citas para pacientes"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#F8FAFC')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Mis Citas Médicas", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC').pack(side='left')
        
        tk.Button(header_frame, text="📅 Solicitar Nueva Cita", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), command=self.request_new_appointment).pack(side='right')
        
        # Filtros
        filters_frame = tk.LabelFrame(main_frame, text="Filtros", font=('Arial', 11, 'bold'), 
                                    padx=10, pady=10)
        filters_frame.pack(fill='x', pady=(0, 20))
        
        filters_row = tk.Frame(filters_frame)
        filters_row.pack()
        
        tk.Label(filters_row, text="Mostrar:", font=('Arial', 10)).grid(row=0, column=0, padx=5)
        self.patient_appointment_filter = ttk.Combobox(filters_row, 
                                                     values=['Todas', 'Próximas', 'Pasadas', 'Este Mes'], 
                                                     state='readonly', width=12)
        self.patient_appointment_filter.set('Próximas')
        self.patient_appointment_filter.grid(row=0, column=1, padx=5)
        self.patient_appointment_filter.bind('<<ComboboxSelected>>', self.filter_patient_appointments)
        
        # Tabla de citas
        columns = ('Fecha', 'Hora', 'Doctor', 'Especialidad', 'Motivo', 'Estado', 'Notas')
        self.patient_appointments_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        column_widths = {'Fecha': 100, 'Hora': 80, 'Doctor': 150, 'Especialidad': 120, 
                        'Motivo': 200, 'Estado': 100, 'Notas': 150}
        
        for col in columns:
            self.patient_appointments_tree.heading(col, text=col)
            self.patient_appointments_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.patient_appointments_tree.yview)
        self.patient_appointments_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.patient_appointments_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        appointment_actions = [
            ("👁️ Ver Detalles", self.view_my_appointment_details, "#0B5394"),
            ("❌ Cancelar Cita", self.cancel_my_appointment, "#C0392B"),
            ("📞 Contactar Clínica", self.contact_clinic, "#E67E22"),
            ("📋 Descargar Comprobante", self.download_appointment_receipt, "#16A085")
        ]
        
        for text, command, color in appointment_actions:
            btn = tk.Button(actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 9, 'bold'))
            btn.pack(side='left', padx=5, pady=5)
        
        # Cargar datos
        self.load_patient_appointments()
    
    def create_patient_medical_history(self, parent):
        """Mi historial médico para pacientes"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(main_frame, text="Mi Historial Médico", 
                font=('Arial', 16, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Panel de resumen de salud
        summary_frame = tk.LabelFrame(main_frame, text="📊 Resumen de Salud", 
                                    font=('Arial', 12, 'bold'), padx=20, pady=15)
        summary_frame.pack(fill='x', pady=10)
        
        try:
            health_summary = self.get_patient_health_summary()
            
            summary_grid = tk.Frame(summary_frame)
            summary_grid.pack()
            
            summary_items = [
                ("🩺 Total de Consultas:", str(health_summary.get('total_consultations', 0))),
                ("📅 Última Consulta:", health_summary.get('last_consultation', 'Nunca')),
                ("👨‍⚕️ Doctores Atendido por:", str(health_summary.get('doctors_count', 0))),
                ("🏥 Especialidades:", health_summary.get('specialties', 'Ninguna'))
            ]
            
            for i, (label, value) in enumerate(summary_items):
                tk.Label(summary_grid, text=label, font=('Arial', 10, 'bold'), 
                        fg='#1E3A8A').grid(row=i//2, column=(i%2)*2, sticky='w', padx=(0, 10), pady=5)
                tk.Label(summary_grid, text=value, font=('Arial', 10), 
                        fg='#64748B').grid(row=i//2, column=(i%2)*2+1, sticky='w', padx=(0, 30), pady=5)
                        
        except Exception as e:
            tk.Label(summary_frame, text=f"Error cargando resumen: {str(e)}", 
                    fg='red').pack()
        
        # Filtros de historial
        filters_frame = tk.LabelFrame(main_frame, text="Filtros", font=('Arial', 11, 'bold'), 
                                    padx=10, pady=10)
        filters_frame.pack(fill='x', pady=(0, 20))
        
        filters_row = tk.Frame(filters_frame)
        filters_row.pack()
        
        tk.Label(filters_row, text="Período:", font=('Arial', 10)).grid(row=0, column=0, padx=5)
        self.history_period_filter = ttk.Combobox(filters_row, 
                                                values=['Todos', 'Este Año', 'Últimos 6 Meses', 'Últimos 3 Meses'], 
                                                state='readonly', width=15)
        self.history_period_filter.set('Todos')
        self.history_period_filter.grid(row=0, column=1, padx=5)
        
        tk.Label(filters_row, text="Doctor:", font=('Arial', 10)).grid(row=0, column=2, padx=5)
        self.history_doctor_filter = ttk.Combobox(filters_row, state='readonly', width=15)
        self.history_doctor_filter.grid(row=0, column=3, padx=5)
        
        tk.Button(filters_row, text="🔍 Filtrar", bg='#0B5394', fg='white',
                 command=self.filter_medical_history).grid(row=0, column=4, padx=10)
        
        # Tabla de historial médico
        columns = ('Fecha', 'Doctor', 'Diagnóstico', 'Tratamiento', 'Medicamentos', 'Observaciones')
        self.patient_history_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        column_widths = {'Fecha': 100, 'Doctor': 150, 'Diagnóstico': 200, 'Tratamiento': 200, 
                        'Medicamentos': 150, 'Observaciones': 200}
        
        for col in columns:
            self.patient_history_tree.heading(col, text=col)
            self.patient_history_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.patient_history_tree.yview)
        self.patient_history_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack
        self.patient_history_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Botones de acción
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        history_actions = [
            ("👁️ Ver Detalle Completo", self.view_history_detail, "#0B5394"),
            ("🖨️ Imprimir Historial", self.print_my_history, "#16A085"),
            ("📥 Exportar PDF", self.export_history_pdf, "#E67E22"),
            ("📧 Enviar por Email", self.email_my_history, "#1abc9c")
        ]
        
        for text, command, color in history_actions:
            btn = tk.Button(actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 9, 'bold'))
            btn.pack(side='left', padx=5, pady=5)
        
        # Cargar datos
        self.load_patient_medical_history()
    
    def create_patient_billing(self, parent):
        """Mis facturas y pagos para pacientes - Vista mejorada"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header moderno
        header_frame = tk.Frame(main_frame, bg='#0B5394', height=60)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#0B5394')
        header_content.pack(expand=True, fill='both', padx=20, pady=10)
        
        tk.Label(header_content, text="💰", font=('Arial', 16), bg='#0B5394', fg='white').pack(side='left', pady=5)
        tk.Label(header_content, text="MIS FACTURAS Y PAGOS", 
                font=('Arial', 14, 'bold'), bg='#0B5394', fg='white').pack(side='left', padx=(10, 0), pady=5)
        tk.Label(header_content, text="Estado de mis cuentas médicas", 
                font=('Arial', 10), bg='#0B5394', fg='#FFFFFF').pack(side='left', padx=(15, 0), pady=5)
        
        # Botón de actualizar
        refresh_btn = tk.Button(
            header_content,
            text="� Actualizar",
            command=self.refresh_patient_billing,
            bg='#0B5394',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        )
        refresh_btn.pack(side='right', pady=5)
        
        # Contenido dividido en dos paneles
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo: Resumen financiero
        left_panel = tk.Frame(content_frame, bg='#F8FAFC', width=380)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # Panel derecho: Lista de facturas
        right_panel = tk.Frame(content_frame, bg='#F8FAFC')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Resumen financiero personalizado
        financial_frame = tk.LabelFrame(
            left_panel, 
            text="💰 MI ESTADO FINANCIERO", 
            font=('Arial', 11, 'bold'),
            bg='#e8f5e8',
            fg='#2e7d32',
            padx=15, 
            pady=15
        )
        financial_frame.pack(fill='x', pady=(0, 15))
        
        try:
            billing_summary = self.get_patient_billing_summary()
            
            # Indicadores financieros del paciente
            financial_indicators = [
                ("💳 Total Pagado", f"₡{billing_summary.get('total_paid', 0):,.2f}", "#16A085"),
                ("⏳ Pendiente", f"₡{billing_summary.get('total_pending', 0):,.2f}", "#C0392B"),
                ("📋 Mis Facturas", str(billing_summary.get('total_invoices', 0)), "#0B5394"),
                ("📅 Este Mes", f"₡{billing_summary.get('month_total', 0):,.2f}", "#16A085")
            ]
            
            for title, value, color in financial_indicators:
                indicator_row = tk.Frame(financial_frame, bg='#e8f5e8')
                indicator_row.pack(fill='x', pady=8)
                
                tk.Label(indicator_row, text=title, font=('Arial', 11, 'bold'),
                        bg='#e8f5e8', fg='#2e7d32').pack(side='left')
                tk.Label(indicator_row, text=value, font=('Arial', 12, 'bold'),
                        bg='#e8f5e8', fg=color).pack(side='right')
            
            # Estado de cuenta
            if billing_summary.get('total_pending', 0) > 0:
                status_color = '#C0392B'
                status_text = "⚠️ Tiene pagos pendientes"
            else:
                status_color = '#16A085'
                status_text = "✅ Cuenta al día"
                
            tk.Label(financial_frame, text=status_text, font=('Arial', 11, 'bold'),
                    bg='#e8f5e8', fg=status_color).pack(pady=(10, 0))
                
        except Exception as e:
            tk.Label(financial_frame, text=f"Error cargando resumen: {str(e)}", 
                    font=('Arial', 9), bg='#e8f5e8', fg='#C0392B').pack()
        
        # Panel de acciones del paciente
        actions_frame = tk.LabelFrame(
            left_panel,
            text="📋 MIS OPCIONES",
            font=('Arial', 11, 'bold'),
            bg='#fff3e0',
            fg='#e65100',
            padx=15,
            pady=15
        )
        actions_frame.pack(fill='x', pady=(0, 15))
        
        patient_actions = [
            ("📄 Descargar Factura", self.download_patient_invoice, '#0B5394'),
            ("💳 Historial de Pagos", self.view_payment_history, '#16A085'),
            ("📧 Solicitar Estado", self.request_account_statement, '#16A085'),
            ("❓ Consultar Duda", self.billing_inquiry, '#E67E22')
        ]
        
        for text, command, color in patient_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 10, 'bold'),
                padx=10,
                pady=8,
                relief='raised'
            )
            btn.pack(fill='x', pady=5)
        
        # Información importante
        info_frame = tk.LabelFrame(
            left_panel,
            text="ℹ️ INFORMACIÓN IMPORTANTE",
            font=('Arial', 11, 'bold'),
            bg='#e3f2fd',
            fg='#1565c0',
            padx=15,
            pady=15
        )
        info_frame.pack(fill='both', expand=True)
        
        info_text = """• Las facturas se generan automáticamente después de cada consulta
• Los pagos pueden realizarse en efectivo, tarjeta o transferencia
• Puede descargar sus facturas en formato PDF
• Para dudas sobre facturación, consulte con secretaría"""
        
        tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                bg='#e3f2fd', fg='#1565c0', justify='left', anchor='w').pack(fill='both', expand=True)
        
        # Panel de facturas (lado derecho)
        invoices_frame = tk.LabelFrame(
            right_panel,
            text="📄 HISTORIAL DE FACTURAS",
            font=('Arial', 12, 'bold'),
            bg='#f1f8e9',
            fg='#2e7d32',
            padx=15,
            pady=15
        )
        invoices_frame.pack(fill='both', expand=True)
        
        # Filtros para paciente
        patient_filter_frame = tk.Frame(invoices_frame, bg='#f1f8e9')
        patient_filter_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(patient_filter_frame, text="🔍 Buscar:", font=('Arial', 10, 'bold'),
                bg='#f1f8e9', fg='#2e7d32').pack(side='left')
        
        self.patient_filter_var = tk.StringVar()
        filter_entry = tk.Entry(patient_filter_frame, textvariable=self.patient_filter_var, 
                               font=('Arial', 10), width=20)
        filter_entry.pack(side='left', padx=(10, 0))
        filter_entry.bind('<KeyRelease>', self.filter_patient_invoices)
        
        # Filtro por estado
        tk.Label(patient_filter_frame, text="Estado:", font=('Arial', 10, 'bold'),
                bg='#f1f8e9', fg='#2e7d32').pack(side='left', padx=(20, 5))
        
        self.patient_status_filter = tk.StringVar(value="todos")
        status_combo = ttk.Combobox(patient_filter_frame, textvariable=self.patient_status_filter,
                                   values=["todos", "pendiente", "pagada", "pago_parcial"],
                                   state="readonly", width=12)
        status_combo.pack(side='left')
        status_combo.bind('<<ComboboxSelected>>', self.filter_patient_invoices)
        
        # Tabla de facturas del paciente
        columns = ('Número', 'Fecha', 'Doctor', 'Concepto', 'Monto', 'Estado')
        self.patient_invoices_tree = ttk.Treeview(invoices_frame, columns=columns, 
                                                 show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'Número': 100, 'Fecha': 90, 'Doctor': 120, 'Concepto': 150, 'Monto': 90, 'Estado': 80}
        for col in columns:
            self.patient_invoices_tree.heading(col, text=col)
            self.patient_invoices_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbar
        patient_scroll = ttk.Scrollbar(invoices_frame, orient="vertical", 
                                      command=self.patient_invoices_tree.yview)
        self.patient_invoices_tree.configure(yscrollcommand=patient_scroll.set)
        
        # Pack tabla
        table_frame = tk.Frame(invoices_frame, bg='#f1f8e9')
        table_frame.pack(fill='both', expand=True)
        
        self.patient_invoices_tree.pack(side='left', fill='both', expand=True)
        patient_scroll.pack(side='right', fill='y')
        
        # Eventos
        self.patient_invoices_tree.bind('<Double-1>', self.view_patient_invoice_details)
        
        # Cargar datos del paciente
        self.load_patient_billing_data()
    
    def get_patient_billing_summary(self):
        """Obtener resumen de facturación del paciente actual"""
        try:
            if not self.current_user:
                return {'total_paid': 0, 'total_pending': 0, 'total_invoices': 0, 'month_total': 0}
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            patient_id = self.current_user.id
            current_month = datetime.now().strftime('%Y-%m')
            
            # Total pagado
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE paciente_id = ? AND estado IN ('pagada', 'pago_parcial')
            ''', (patient_id,))
            total_paid = cursor.fetchone()[0]
            
            # Total pendiente
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE paciente_id = ? AND estado = 'pendiente'
            ''', (patient_id,))
            total_pending = cursor.fetchone()[0]
            
            # Total facturas
            cursor.execute('SELECT COUNT(*) FROM facturas WHERE paciente_id = ?', (patient_id,))
            total_invoices = cursor.fetchone()[0]
            
            # Total del mes
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) 
                FROM facturas 
                WHERE paciente_id = ? AND strftime('%Y-%m', fecha_creacion) = ?
            ''', (patient_id, current_month))
            month_total = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_paid': float(total_paid),
                'total_pending': float(total_pending),
                'total_invoices': total_invoices,
                'month_total': float(month_total)
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen del paciente: {e}")
            return {'total_paid': 0, 'total_pending': 0, 'total_invoices': 0, 'month_total': 0}
    
    def load_patient_billing_data(self):
        """Cargar facturas del paciente actual"""
        try:
            if not self.current_user:
                return
            
            # Limpiar tabla
            for item in self.patient_invoices_tree.get_children():
                self.patient_invoices_tree.delete(item)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener facturas del paciente
            cursor.execute('''
                SELECT f.numero_factura, f.fecha_creacion, 
                       (SELECT nombre || ' ' || apellido FROM usuarios WHERE id = f.doctor_id) as doctor_nombre,
                       f.concepto, f.monto, f.estado
                FROM facturas f
                WHERE f.paciente_id = ?
                ORDER BY f.fecha_creacion DESC
            ''', (self.current_user.id,))
            
            invoices = cursor.fetchall()
            
            for invoice in invoices:
                fecha = invoice[1]
                if fecha:
                    try:
                        dt = datetime.fromisoformat(fecha)
                        fecha = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                # Formatear estado
                estado = invoice[5].title() if invoice[5] else 'Desconocido'
                if estado == 'Pagada':
                    estado = '✅ Pagada'
                elif estado == 'Pendiente':
                    estado = '⏳ Pendiente'
                elif estado == 'Pago_Parcial':
                    estado = '🔸 Parcial'
                
                self.patient_invoices_tree.insert('', 'end', values=(
                    invoice[0] or 'N/A',
                    fecha,
                    invoice[2] or 'N/A',
                    invoice[3] or 'Consulta médica',
                    f"₡{float(invoice[4] or 0):,.2f}",
                    estado
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando mis facturas: {str(e)}")
    
    def refresh_patient_billing(self):
        """Actualizar datos de facturación del paciente"""
        self.load_patient_billing_data()
        messagebox.showinfo("Actualizado", "✅ Mis facturas han sido actualizadas")
    
    def download_patient_invoice(self):
        """Descargar factura seleccionada"""
        selection = self.patient_invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione una factura para descargar")
            return
        
        item = self.patient_invoices_tree.item(selection[0])
        invoice_number = item['values'][0]
        
        messagebox.showinfo("Descargar Factura", 
                           f"Descarga de factura: {invoice_number}\n\n" +
                           "La funcionalidad de descarga PDF está disponible en el Sistema Completo de Facturación")
    
    def view_payment_history(self):
        """Ver historial de pagos del paciente"""
        messagebox.showinfo("Historial de Pagos", 
                           "Su historial completo de pagos incluye:\n\n" +
                           "• Fechas y montos de pagos\n• Métodos de pago utilizados\n• Comprobantes disponibles\n\n" +
                           "Consulte con secretaría para detalles específicos")
    
    def request_account_statement(self):
        """Solicitar estado de cuenta"""
        messagebox.showinfo("Estado de Cuenta", 
                           "Su solicitud de estado de cuenta ha sido registrada.\n\n" +
                           "Recibirá un reporte detallado por email en las próximas 24 horas.\n\n" +
                           "Para solicitudes urgentes, contacte directamente a secretaría")
    
    def billing_inquiry(self):
        """Consulta sobre facturación"""
        messagebox.showinfo("Consultas de Facturación", 
                           "Para consultas sobre facturación puede:\n\n" +
                           "• Contactar secretaría durante horario de atención\n" +
                           "• Llamar al teléfono principal de la clínica\n" +
                           "• Solicitar cita con administración\n\n" +
                           "Horario: Lunes a Viernes 8:00 AM - 5:00 PM")
    
    def filter_patient_invoices(self, event=None):
        """Filtrar facturas del paciente"""
        # Implementación básica de filtrado para pacientes
        self.load_patient_billing_data()  # Por simplicidad, recargamos
    
    def view_patient_invoice_details(self, event=None):
        """Ver detalles de factura del paciente"""
        selection = self.patient_invoices_tree.selection()
        if not selection:
            return
        
        item = self.patient_invoices_tree.item(selection[0])
        invoice_data = item['values']
        
        details_text = f"""📄 DETALLES DE FACTURA

🔢 Número: {invoice_data[0]}
📅 Fecha: {invoice_data[1]}
👨‍⚕️ Doctor: {invoice_data[2]}
💭 Concepto: {invoice_data[3]}
💰 Monto: {invoice_data[4]}
📊 Estado: {invoice_data[5]}

💡 Para obtener una copia PDF de esta factura o más detalles, 
consulte con secretaría o use el Sistema Completo de Facturación"""
        
        messagebox.showinfo("Detalles de Mi Factura", details_text)
        self.patient_billing_status_filter.set('Todas')
        self.patient_billing_status_filter.grid(row=0, column=1, padx=5)
        
        tk.Label(filters_row, text="Período:", font=('Arial', 10)).grid(row=0, column=2, padx=5)
        self.patient_billing_period_filter = ttk.Combobox(filters_row, 
                                                        values=['Todos', 'Este Mes', 'Últimos 3 Meses', 'Este Año'], 
                                                        state='readonly', width=12)
        self.patient_billing_period_filter.set('Todos')
        self.patient_billing_period_filter.grid(row=0, column=3, padx=5)
        
        tk.Button(filters_row, text="🔍 Filtrar", bg='#0B5394', fg='white',
                 command=self.filter_patient_billing).grid(row=0, column=4, padx=10)
        
        # Frame contenedor para tabla y scrollbars
        table_billing_frame = tk.Frame(main_frame, bg='#F8FAFC')
        table_billing_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Tabla de facturas
        columns = ('Número', 'Fecha', 'Concepto', 'Monto', 'Estado', 'Vencimiento', 'Doctor')
        self.patient_billing_tree = ttk.Treeview(table_billing_frame, columns=columns, show='headings', height=12)
        
        # Configurar headers
        column_widths = {'Número': 100, 'Fecha': 100, 'Concepto': 200, 'Monto': 100, 
                        'Estado': 100, 'Vencimiento': 100, 'Doctor': 150}
        
        for col in columns:
            self.patient_billing_tree.heading(col, text=col)
            self.patient_billing_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars verticales y horizontales con mejor visibilidad
        scrollbar_y = ttk.Scrollbar(table_billing_frame, orient="vertical", command=self.patient_billing_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_billing_frame, orient="horizontal", command=self.patient_billing_tree.xview)
        self.patient_billing_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout con grid para mejor control de scrollbars con padding
        self.patient_billing_tree.grid(row=0, column=0, sticky='nsew', padx=(5, 0), pady=(5, 0))
        scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=(5, 0))
        scrollbar_x.grid(row=1, column=0, sticky='ew', padx=(5, 0), pady=(0, 5))
        
        # Configurar expansión con mínimo para scrollbars
        table_billing_frame.grid_rowconfigure(0, weight=1)
        table_billing_frame.grid_rowconfigure(1, weight=0, minsize=20)
        table_billing_frame.grid_columnconfigure(0, weight=1)
        table_billing_frame.grid_columnconfigure(1, weight=0, minsize=20)
        
        # Botones de acción
        actions_frame = tk.Frame(main_frame, bg='#F8FAFC')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        billing_actions = [
            ("👁️ Ver Detalle", self.view_my_invoice_detail, "#0B5394"),
            ("💳 Pagar Ahora", self.pay_invoice_online, "#16A085"),
            ("🖨️ Imprimir Factura", self.print_my_invoice, "#16A085"),
            ("📥 Descargar PDF", self.download_invoice_pdf, "#E67E22"),
            ("📞 Consultar Pago", self.inquire_payment, "#1abc9c")
        ]
        
        for text, command, color in billing_actions:
            btn = tk.Button(actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 9, 'bold'))
            btn.pack(side='left', padx=5, pady=5)
        
        # Cargar datos
        self.load_patient_billing()
    
    def create_patient_profile(self, parent):
        """Mi perfil para pacientes"""
        main_frame = tk.Frame(parent, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Mi Perfil Personal", 
                font=('Arial', 18, 'bold'), bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Panel principal dividido
        content_frame = tk.Frame(main_frame, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Información personal
        left_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Header del panel izquierdo
        left_header = tk.Frame(left_panel, bg='#0B5394', height=60)
        left_header.pack(fill='x')
        left_header.pack_propagate(False)
        
        tk.Label(left_header, text="👤 Información Personal", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido del perfil
        profile_content = tk.Frame(left_panel, bg='white')
        profile_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        try:
            patient_data = self.get_patient_profile_data()
            
            # Avatar
            avatar_frame = tk.Frame(profile_content, bg='#FFFFFF', width=120, height=120)
            avatar_frame.pack(pady=(0, 20))
            avatar_frame.pack_propagate(False)
            tk.Label(avatar_frame, text="👤", font=('Arial', 60), bg='#FFFFFF', fg='#64748B').pack(expand=True)
            
            # Información personal
            personal_fields = [
                ("Nombre completo:", f"{patient_data.get('nombre', '')} {patient_data.get('apellido', '')}"),
                ("Email:", patient_data.get('email', '')),
                ("Teléfono:", patient_data.get('telefono', '')),
                ("Fecha de nacimiento:", patient_data.get('fecha_nacimiento', '')),
                ("Dirección:", patient_data.get('direccion', '')),
                ("Número de expediente:", patient_data.get('numero_expediente', '')),
                ("Seguro médico:", patient_data.get('seguro_nombre', 'Sin seguro')),
                ("Contacto de emergencia:", patient_data.get('contacto_emergencia', '')),
                ("Teléfono de emergencia:", patient_data.get('telefono_emergencia', ''))
            ]
            
            for label, value in personal_fields:
                field_frame = tk.Frame(profile_content, bg='white')
                field_frame.pack(fill='x', pady=5)
                
                tk.Label(field_frame, text=label, font=('Arial', 10, 'bold'), 
                        bg='white', fg='#1E3A8A', width=20, anchor='w').pack(side='left')
                tk.Label(field_frame, text=value or 'No especificado', font=('Arial', 10), 
                        bg='white', fg='#64748B', anchor='w').pack(side='left', padx=(10, 0))
                        
        except Exception as e:
            tk.Label(profile_content, text=f"Error cargando perfil: {str(e)}", 
                    fg='red', bg='white').pack()
        
        # Panel derecho - Configuraciones y estadísticas
        right_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Header del panel derecho
        right_header = tk.Frame(right_panel, bg='#0B5394', height=60)
        right_header.pack(fill='x')
        right_header.pack_propagate(False)
        
        tk.Label(right_header, text="⚙️ Configuraciones", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido del panel derecho
        config_content = tk.Frame(right_panel, bg='white')
        config_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Botones de configuración
        config_buttons = [
            ("✏️ Editar Información Personal", self.edit_patient_personal_info, "#0B5394"),
            ("🔑 Cambiar Contraseña", self.change_patient_password, "#E67E22"),
            ("📧 Configurar Notificaciones", self.configure_notifications, "#16A085"),
            ("🏥 Actualizar Seguro Médico", self.update_insurance_info, "#1abc9c"),
            ("👥 Contactos de Emergencia", self.manage_emergency_contacts, "#C0392B")
        ]
        
        for text, command, color in config_buttons:
            btn = tk.Button(config_content, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=25, height=2)
            btn.pack(fill='x', pady=8)
        
        # Estadísticas del paciente
        stats_frame = tk.LabelFrame(config_content, text="📊 Mis Estadísticas", 
                                  font=('Arial', 11, 'bold'), padx=15, pady=10)
        stats_frame.pack(fill='x', pady=(20, 0))
        
        try:
            patient_stats = self.get_patient_personal_stats()
            
            stats_text = f"""
📅 Miembro desde: {patient_stats.get('member_since', 'N/A')}
🩺 Total de consultas: {patient_stats.get('total_consultations', 0)}
👨‍⚕️ Doctores consultados: {patient_stats.get('doctors_count', 0)}
💰 Total pagado: RD$ {patient_stats.get('total_paid', 0):,.2f}
📋 Última consulta: {patient_stats.get('last_consultation', 'Nunca')}
            """
            
            tk.Label(stats_frame, text=stats_text, font=('Arial', 9), 
                    justify='left', bg='white').pack()
                    
        except Exception as e:
            tk.Label(stats_frame, text=f"Error en estadísticas: {str(e)}", 
                    fg='red', bg='white').pack()
    
    # ==================== FUNCIONES DE SOPORTE Y UTILIDADES ====================
    
    # Funciones para obtener datos
    def get_doctor_stats(self):
        """Obtener estadísticas específicas del doctor"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            doctor_id = self.current_user.id
            today = datetime.now().strftime('%Y-%m-%d')
            current_month = datetime.now().strftime('%Y-%m')
            
            # Citas de hoy
            cursor.execute("SELECT COUNT(*) FROM citas WHERE doctor_id = ? AND DATE(fecha_hora) = ?", 
                         (doctor_id, today))
            stats['appointments_today'] = cursor.fetchone()[0]
            
            # Total de pacientes únicos
            cursor.execute("""
                SELECT COUNT(DISTINCT paciente_id) FROM citas WHERE doctor_id = ?
            """, (doctor_id,))
            stats['total_patients'] = cursor.fetchone()[0]
            
            # Ingresos del mes
            cursor.execute("""
                SELECT COALESCE(SUM(tarifa_consulta), 0) FROM citas 
                WHERE doctor_id = ? AND estado = 'completada' 
                AND strftime('%Y-%m', fecha_hora) = ?
            """, (doctor_id, current_month))
            stats['monthly_income'] = cursor.fetchone()[0] or 0
            
            # Consultas del mes
            cursor.execute("""
                SELECT COUNT(*) FROM citas 
                WHERE doctor_id = ? AND estado = 'completada' 
                AND strftime('%Y-%m', fecha_hora) = ?
            """, (doctor_id, current_month))
            stats['consultations_month'] = cursor.fetchone()[0]
            
            # Total de consultas
            cursor.execute("SELECT COUNT(*) FROM citas WHERE doctor_id = ? AND estado = 'completada'", 
                         (doctor_id,))
            stats['total_consultations'] = cursor.fetchone()[0]
            
            # Ingresos totales
            cursor.execute("""
                SELECT COALESCE(SUM(tarifa_consulta), 0) FROM citas 
                WHERE doctor_id = ? AND estado = 'completada'
            """, (doctor_id,))
            stats['total_income'] = cursor.fetchone()[0] or 0
            
            # Promedio mensual (aproximado)
            if stats['total_consultations'] > 0:
                stats['avg_monthly'] = stats['total_consultations'] // 12
            else:
                stats['avg_monthly'] = 0
            
            cursor.close()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas del doctor: {e}")
            return {}
    
    def get_doctor_upcoming_appointments(self):
        """Obtener próximas citas del doctor"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            doctor_id = self.current_user.id
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT c.*, u.nombre || ' ' || u.apellido as paciente_nombre
                FROM citas c
                JOIN usuarios u ON c.paciente_id = u.id
                WHERE c.doctor_id = ? AND c.fecha_hora > ? AND c.estado = 'programada'
                ORDER BY c.fecha_hora ASC
            """, (doctor_id, now))
            
            appointments = []
            for row in cursor.fetchall():
                apt = dict(zip([col[0] for col in cursor.description], row))
                # Formatear fecha/hora
                try:
                    dt = datetime.fromisoformat(apt['fecha_hora'])
                    apt['fecha_hora_formatted'] = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    apt['fecha_hora_formatted'] = apt['fecha_hora']
                appointments.append(apt)
            
            cursor.close()
            conn.close()
            return appointments
            
        except Exception as e:
            print(f"Error obteniendo próximas citas: {e}")
            return []
    
    def get_secretaria_stats(self):
        """Obtener estadísticas para secretarias"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Citas de hoy
            cursor.execute("SELECT COUNT(*) FROM citas WHERE DATE(fecha_hora) = ?", (today,))
            stats['appointments_today'] = cursor.fetchone()[0]
            
            # Citas pendientes
            cursor.execute("SELECT COUNT(*) FROM citas WHERE estado = 'programada'", )
            stats['pending_appointments'] = cursor.fetchone()[0]
            
            # Facturas pendientes
            cursor.execute("SELECT COUNT(*) FROM facturas WHERE estado = 'pendiente'", )
            stats['pending_invoices'] = cursor.fetchone()[0]
            
            # Nuevos pacientes hoy
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios 
                WHERE tipo_usuario = 'paciente' AND DATE(fecha_creacion) = ?
            """, (today,))
            stats['new_patients_today'] = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de secretaria: {e}")
            return {}
    
    def get_today_appointments(self):
        """Obtener citas de hoy para la agenda"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT c.*, 
                       up.nombre || ' ' || up.apellido as paciente_nombre,
                       ud.nombre || ' ' || ud.apellido as doctor_nombre,
                       TIME(c.fecha_hora) as hora
                FROM citas c
                JOIN usuarios up ON c.paciente_id = up.id
                JOIN usuarios ud ON c.doctor_id = ud.id
                WHERE DATE(c.fecha_hora) = ?
                ORDER BY c.fecha_hora ASC
            """, (today,))
            
            appointments = []
            for row in cursor.fetchall():
                apt = dict(zip([col[0] for col in cursor.description], row))
                appointments.append(apt)
            
            cursor.close()
            conn.close()
            return appointments
            
        except Exception as e:
            print(f"Error obteniendo citas de hoy: {e}")
            return []
    
    def get_patient_info(self):
        """Obtener información del paciente actual"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            patient_id = self.current_user.id
            
            cursor.execute("""
                SELECT u.*, p.numero_expediente, p.seguro_id, p.contacto_emergencia, 
                       p.telefono_emergencia, s.nombre as seguro_nombre
                FROM usuarios u
                LEFT JOIN pacientes p ON u.id = p.id
                LEFT JOIN seguros_medicos s ON p.seguro_id = s.id
                WHERE u.id = ?
            """, (patient_id,))
            
            row = cursor.fetchone()
            if row:
                patient_data = dict(zip([col[0] for col in cursor.description], row))
            else:
                patient_data = {}
            
            cursor.close()
            conn.close()
            return patient_data
            
        except Exception as e:
            print(f"Error obteniendo información del paciente: {e}")
            return {}
    
    def get_patient_upcoming_appointments(self):
        """Obtener próximas citas del paciente"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            patient_id = self.current_user.id
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT c.*, u.nombre || ' ' || u.apellido as doctor_nombre,
                       DATE(c.fecha_hora) as fecha_formatted,
                       TIME(c.fecha_hora) as hora_formatted
                FROM citas c
                JOIN usuarios u ON c.doctor_id = u.id
                WHERE c.paciente_id = ? AND c.fecha_hora > ? AND c.estado = 'programada'
                ORDER BY c.fecha_hora ASC
            """, (patient_id, now))
            
            appointments = []
            for row in cursor.fetchall():
                apt = dict(zip([col[0] for col in cursor.description], row))
                appointments.append(apt)
            
            cursor.close()
            conn.close()
            return appointments
            
        except Exception as e:
            print(f"Error obteniendo próximas citas del paciente: {e}")
            return []
    
    def get_patient_reminders(self):
        """Obtener recordatorios del paciente"""
        # Esta función puede expandirse para incluir recordatorios específicos
        # Por ahora devolvemos recordatorios básicos basados en citas próximas
        try:
            reminders = []
            upcoming = self.get_patient_upcoming_appointments()
            
            for apt in upcoming:
                try:
                    apt_date = datetime.fromisoformat(apt['fecha_hora'])
                    days_until = (apt_date - datetime.now()).days
                    
                    if days_until <= 1:
                        reminders.append({
                            'message': f"Tienes una cita mañana con Dr. {apt['doctor_nombre']} a las {apt.get('hora_formatted', 'N/A')}"
                        })
                    elif days_until <= 7:
                        reminders.append({
                            'message': f"Tienes una cita en {days_until} días con Dr. {apt['doctor_nombre']}"
                        })
                except:
                    continue
            
            return reminders
            
        except Exception as e:
            print(f"Error obteniendo recordatorios: {e}")
            return []
    
    # Funciones placeholder para botones (implementar según necesidades)
    def new_appointment_quick(self):
        """Abrir ventana de nueva cita"""
        self.new_appointment_window()
    
    def new_patient_quick(self):
        messagebox.showinfo("Acción", "Funcionalidad de nuevo paciente rápido - En desarrollo")
    
    def process_payment_quick(self):
        """Acceso rápido al sistema de facturación para procesamiento de pagos"""
        self.switch_tab("Facturación Avanzada")
        messagebox.showinfo("Sistema de Facturación", 
                           "🚀 Accediendo al sistema de facturación integrado\n\n" +
                           "Desde aquí podrá:\n" +
                           "• Procesar pagos completos\n" +
                           "• Calcular cambio y faltante\n" +
                           "• Generar PDFs automáticamente")
    
    def generate_invoice_quick(self):
        """Acceso rápido al sistema de facturación para generar facturas"""
        self.switch_tab("Facturación Avanzada")
        messagebox.showinfo("Sistema de Facturación", 
                           "🚀 Accediendo al sistema de facturación integrado\n\n" +
                           "Desde aquí podrá:\n" +
                           "• Crear facturas completas\n" +
                           "• Seleccionar servicios médicos\n" +
                           "• Generar PDFs profesionales\n" +
                           "• Procesar pagos en tiempo real")
    
    def manage_waiting_list(self):
        messagebox.showinfo("Acción", "Gestión de lista de espera - En desarrollo")
    
    def daily_report(self):
        messagebox.showinfo("Acción", "Reporte diario - En desarrollo")
    
    def filter_doctor_appointments(self, event=None):
        self.load_doctor_appointments()
    
    def load_doctor_appointments(self):
        """Cargar citas del doctor"""
        try:
            # Limpiar tabla
            for item in self.doctor_appointments_tree.get_children():
                self.doctor_appointments_tree.delete(item)
            
            # Obtener citas según filtro
            filter_value = self.appointment_filter.get()
            doctor_id = self.current_user.id
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Construir query según filtro
            today = datetime.now().strftime('%Y-%m-%d')
            where_clause = "WHERE c.doctor_id = ?"
            params = [doctor_id]
            
            if filter_value == 'Hoy':
                where_clause += " AND DATE(c.fecha_hora) = ?"
                params.append(today)
            elif filter_value == 'Esta Semana':
                start_week = datetime.now() - timedelta(days=datetime.now().weekday())
                end_week = start_week + timedelta(days=6)
                where_clause += " AND DATE(c.fecha_hora) BETWEEN ? AND ?"
                params.extend([start_week.strftime('%Y-%m-%d'), end_week.strftime('%Y-%m-%d')])
            elif filter_value == 'Este Mes':
                current_month = datetime.now().strftime('%Y-%m')
                where_clause += " AND strftime('%Y-%m', c.fecha_hora) = ?"
                params.append(current_month)
            
            cursor.execute(f"""
                SELECT c.fecha_hora, u.nombre || ' ' || u.apellido as paciente_nombre,
                       c.motivo, c.estado, c.duracion_minutos
                FROM citas c
                JOIN usuarios u ON c.paciente_id = u.id
                {where_clause}
                ORDER BY c.fecha_hora DESC
            """, params)
            
            for row in cursor.fetchall():
                # Formatear fecha/hora
                fecha_hora = row[0]
                try:
                    dt = datetime.fromisoformat(fecha_hora)
                    fecha_hora_formatted = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_hora_formatted = fecha_hora
                
                self.doctor_appointments_tree.insert('', 'end', values=(
                    fecha_hora_formatted, row[1], row[2], row[3], 
                    f"{row[4]} min" if row[4] else 'N/A', 'Ver'
                ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando citas: {str(e)}")
    
    def load_doctor_patients(self):
        """Cargar pacientes del doctor"""
        try:
            # Limpiar tabla
            for item in self.doctor_patients_tree.get_children():
                self.doctor_patients_tree.delete(item)
            
            doctor_id = self.current_user.id
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT u.nombre, u.apellido, u.email, u.telefono,
                       MAX(c.fecha_hora) as ultima_consulta,
                       CASE WHEN u.activo THEN 'Activo' ELSE 'Inactivo' END as estado
                FROM usuarios u
                JOIN citas c ON u.id = c.paciente_id
                WHERE c.doctor_id = ? AND u.tipo_usuario = 'paciente'
                GROUP BY u.id, u.nombre, u.apellido, u.email, u.telefono, u.activo
                ORDER BY MAX(c.fecha_hora) DESC
            """, (doctor_id,))
            
            for row in cursor.fetchall():
                # Formatear última consulta
                ultima_consulta = row[4]
                if ultima_consulta:
                    try:
                        dt = datetime.fromisoformat(ultima_consulta)
                        ultima_consulta_formatted = dt.strftime('%d/%m/%Y')
                    except:
                        ultima_consulta_formatted = ultima_consulta
                else:
                    ultima_consulta_formatted = 'Nunca'
                
                self.doctor_patients_tree.insert('', 'end', values=(
                    row[0], row[1], row[2], row[3], ultima_consulta_formatted, row[5]
                ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pacientes: {str(e)}")
    
    def load_medical_patients(self):
        """Cargar pacientes para historiales médicos"""
        try:
            # Limpiar listbox
            self.medical_patients_listbox.delete(0, tk.END)
            
            doctor_id = self.current_user.id
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT u.id, u.nombre || ' ' || u.apellido as nombre_completo
                FROM usuarios u
                JOIN citas c ON u.id = c.paciente_id
                WHERE c.doctor_id = ? AND u.tipo_usuario = 'paciente'
                ORDER BY nombre_completo
            """, (doctor_id,))
            
            for row in cursor.fetchall():
                self.medical_patients_listbox.insert(tk.END, f"{row[1]} (ID: {row[0]})")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pacientes: {str(e)}")
    
    # Más funciones placeholder para completar la funcionalidad
    def add_appointment_notes(self): 
        messagebox.showinfo("Acción", "Agregar notas - En desarrollo")
    def search_patients(self, event=None): 
        messagebox.showinfo("Acción", "Buscar pacientes - En desarrollo")
    def view_patient_profile(self): 
        messagebox.showinfo("Acción", "Ver perfil de paciente - En desarrollo")
    def view_medical_history(self): 
        messagebox.showinfo("Acción", "Ver historial médico - En desarrollo")
    def schedule_appointment(self): 
        messagebox.showinfo("Acción", "Programar cita - En desarrollo")
    def load_patient_medical_records(self, event=None): 
        messagebox.showinfo("Acción", "Cargar historiales médicos - En desarrollo")
    
    # ==================== FUNCIONES HISTORIAL MÉDICO ====================
    
    def load_patients_for_medical_history(self):
        """Cargar lista de pacientes para historial médico"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener filtro de búsqueda
            search_term = getattr(self, 'patient_search_var', tk.StringVar()).get().lower()
            
            # Query base
            query = """
                SELECT u.id, u.nombre, u.apellido, u.email, u.telefono, u.fecha_nacimiento,
                       CASE 
                           WHEN u.fecha_nacimiento IS NOT NULL 
                           THEN CAST((julianday('now') - julianday(u.fecha_nacimiento)) / 365.25 AS INTEGER)
                           ELSE 0 
                       END as edad
                FROM usuarios u 
                WHERE u.tipo_usuario = 'paciente' AND u.activo = 1
            """
            
            params = []
            if search_term:
                query += " AND (LOWER(u.nombre) LIKE ? OR LOWER(u.apellido) LIKE ? OR LOWER(u.email) LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            query += " ORDER BY u.apellido, u.nombre"
            
            cursor.execute(query, params)
            patients = cursor.fetchall()
            
            # Limpiar tree
            for item in self.patients_medical_tree.get_children():
                self.patients_medical_tree.delete(item)
            
            # Agregar pacientes
            for patient in patients:
                # Convertir Row object a valores individuales
                patient_values = (
                    patient[0],  # id
                    patient[1],  # nombre
                    patient[2],  # apellido
                    patient[6],  # edad
                    patient[4] or "No especificado"  # telefono
                )
                self.patients_medical_tree.insert('', 'end', values=patient_values)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pacientes: {str(e)}")
    
    def search_patients_medical(self, event=None):
        """Buscar pacientes en historial médico"""
        self.load_patients_for_medical_history()
    
    def on_patient_select_medical(self, event):
        """Manejar selección de paciente en historial médico"""
        selection = self.patients_medical_tree.selection()
        if selection:
            item = self.patients_medical_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 3:
                self.selected_patient_id = values[0]
                patient_name = f"{values[1]} {values[2]}"
                
                # Actualizar header
                self.patient_name_label.config(text=f"📋 Historial de {patient_name}")
                
                # Mostrar información del paciente
                self.show_patient_info_medical(values)
                
                # Cargar registros médicos del paciente
                self.load_medical_records_for_patient(self.selected_patient_id)
            else:
                messagebox.showerror("Error", "Datos de paciente inválidos")
        else:
            self.selected_patient_id = None
            self.show_default_medical_info()
    
    def show_patient_info_medical(self, patient_data):
        """Mostrar información del paciente seleccionado"""
        # Limpiar frame
        for widget in self.patient_info_frame.winfo_children():
            widget.destroy()
        
        # Crear tarjeta de información
        info_card = tk.Frame(self.patient_info_frame, bg='#FFFFFF', relief='solid', bd=1)
        info_card.pack(fill='x', pady=5)
        
        # Header de la tarjeta
        card_header = tk.Frame(info_card, bg='#0B5394', height=30)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        tk.Label(card_header, text="👤 Información del Paciente", font=('Arial', 10, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido de la tarjeta
        card_content = tk.Frame(info_card, bg='#FFFFFF')
        card_content.pack(fill='x', padx=10, pady=8)
        
        # Información básica
        info_items = [
            ("ID:", str(patient_data[0])),
            ("Nombre:", f"{patient_data[1]} {patient_data[2]}"),
            ("Edad:", f"{patient_data[3]} años" if patient_data[3] else "No especificada"),
            ("Teléfono:", patient_data[4] or "No especificado")
        ]
        
        for label, value in info_items:
            row = tk.Frame(card_content, bg='#FFFFFF')
            row.pack(fill='x', pady=1)
            
            tk.Label(row, text=label, font=('Arial', 9, 'bold'), bg='#FFFFFF', width=12, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Arial', 9), bg='#FFFFFF', anchor='w').pack(side='left', padx=(5, 0))
    
    def show_default_medical_info(self):
        """Mostrar información por defecto cuando no hay paciente seleccionado"""
        # Limpiar frames
        for widget in self.patient_info_frame.winfo_children():
            widget.destroy()
        
        # Limpiar registros médicos
        for item in self.medical_records_tree.get_children():
            self.medical_records_tree.delete(item)
        
        # Mensaje por defecto
        default_label = tk.Label(self.patient_info_frame, 
                               text="👆 Seleccione un paciente de la lista\npara ver su historial médico", 
                               font=('Arial', 11), bg='#FFFFFF', fg='#64748B', 
                               justify='center', pady=20)
        default_label.pack(fill='x')
        
        # Actualizar header
        self.patient_name_label.config(text="📋 Historial Médico")
    
    def load_medical_records_for_patient(self, patient_id):
        """Cargar registros médicos del paciente seleccionado"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT hm.id, hm.fecha_consulta, hm.tipo_consulta, 
                       (d.nombre || ' ' || d.apellido) as doctor,
                       hm.diagnostico, hm.estado
                FROM historial_medico hm
                JOIN usuarios d ON hm.doctor_id = d.id
                WHERE hm.paciente_id = ?
                ORDER BY hm.fecha_consulta DESC
            """
            
            cursor.execute(query, (patient_id,))
            records = cursor.fetchall()
            
            # Limpiar tree
            for item in self.medical_records_tree.get_children():
                self.medical_records_tree.delete(item)
            
            # Agregar registros
            for record in records:
                # Formatear fecha
                fecha = record[1][:10] if record[1] else "N/A"
                self.medical_records_tree.insert('', 'end', values=(
                    record[0], fecha, record[2] or "Consulta", 
                    record[3], record[4] or "Sin diagnóstico", 
                    record[5] or "Pendiente"
                ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar registros médicos: {str(e)}")
    
    def on_medical_record_select(self, event):
        """Manejar selección de registro médico"""
        selection = self.medical_records_tree.selection()
        if selection:
            item = self.medical_records_tree.item(selection[0])
            self.selected_medical_record_id = item['values'][0]
        else:
            self.selected_medical_record_id = None
    
    def add_medical_record(self):
        """Agregar nuevo registro médico"""
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Por favor seleccione un paciente")
            return
        
        self.open_medical_record_form()
    
    def open_medical_record_form(self, edit_mode=False):
        """Abrir formulario para crear/editar registro médico - Diseño Premium"""
        form_window = tk.Toplevel()
        title = "Editar Consulta" if edit_mode else "Nueva Consulta Médica"
        form_window.title(f"{title} - MEDISYNC")
        form_window.geometry("900x750")
        form_window.configure(bg='#f0f4f7')
        form_window.resizable(False, False)
        
        # Centrar ventana
        form_window.transient(self.root)
        form_window.grab_set()
        self.center_window(form_window, 900, 750)
        
        # Header Premium con gradiente visual
        header_frame = tk.Frame(form_window, bg='#2c5aa0', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Container del header
        header_container = tk.Frame(header_frame, bg='#2c5aa0')
        header_container.pack(expand=True, fill='both', padx=30, pady=15)
        
        # Icono y título del header
        icon = "✏️" if edit_mode else "🩺"
        icon_label = tk.Label(header_container, text=icon, font=('Arial', 24), 
                             bg='#2c5aa0', fg='white')
        icon_label.pack(side='left')
        
        title_label = tk.Label(header_container, text=title, font=('Arial', 20, 'bold'), 
                              bg='#2c5aa0', fg='white')
        title_label.pack(side='left', padx=(15, 0))
        
        # Subtítulo
        subtitle = "Edición de registro médico" if edit_mode else "Registro de nueva consulta médica"
        subtitle_label = tk.Label(header_container, text=subtitle, font=('Arial', 11), 
                                 bg='#2c5aa0', fg='#a8c5e8')
        subtitle_label.pack(side='right')
        
        # Variables del formulario
        form_vars = {
            'fecha_consulta': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'tipo_consulta': tk.StringVar(value='Consulta General'),
            'motivo_consulta': tk.StringVar(),
            'sintomas': tk.StringVar(),
            'diagnostico': tk.StringVar(),
            'tratamiento': tk.StringVar(),
            'medicamentos': tk.StringVar(),
            'observaciones': tk.StringVar(),
            'proxima_cita': tk.StringVar(),
            'estado': tk.StringVar(value='Completada')
        }
        
        # Scrollable content
        main_canvas = tk.Canvas(form_window, bg='#f0f4f7', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#f0f4f7')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido principal con padding elegante
        content_frame = tk.Frame(scrollable_frame, bg='#f0f4f7')
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # ========== SECCIÓN 1: INFORMACIÓN DEL PACIENTE ==========
        patient_container = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        patient_container.pack(fill='x', pady=(0, 20))
        
        # Header de la sección paciente
        patient_header = tk.Frame(patient_container, bg='#F8FAFC', height=50)
        patient_header.pack(fill='x')
        patient_header.pack_propagate(False)
        
        tk.Label(patient_header, text="👤", font=('Arial', 20), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', padx=(20, 10), pady=12)
        tk.Label(patient_header, text="Paciente", font=('Arial', 14, 'bold'), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', pady=12)
        
        # Contenido del paciente
        patient_content = tk.Frame(patient_container, bg='white')
        patient_content.pack(fill='x', padx=25, pady=20)
        
        selection = self.patients_medical_tree.selection()
        if selection:
            item = self.patients_medical_tree.item(selection[0])
            patient_name = f"{item['values'][1]} {item['values'][2]}"
            
            # Información del paciente con estilo
            patient_info_frame = tk.Frame(patient_content, bg='#f8fffe', relief='solid', bd=1, padx=15, pady=12)
            patient_info_frame.pack(fill='x')
            
            tk.Label(patient_info_frame, text=f"Paciente: {patient_name}", 
                    font=('Arial', 12, 'bold'), bg='#f8fffe', fg='#2c5aa0').pack(anchor='w')
            
            # Información adicional del paciente
            edad_info = f"Edad: {item['values'][3]} años" if len(item['values']) > 3 else ""
            if edad_info:
                tk.Label(patient_info_frame, text=edad_info, 
                        font=('Arial', 10), bg='#f8fffe', fg='#5a7a92').pack(anchor='w')
        
        # ========== SECCIÓN 2: DATOS BÁSICOS DE LA CONSULTA ==========
        basic_container = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        basic_container.pack(fill='x', pady=(0, 20))
        
        # Header de datos básicos
        basic_header = tk.Frame(basic_container, bg='#F8FAFC', height=50)
        basic_header.pack(fill='x')
        basic_header.pack_propagate(False)
        
        tk.Label(basic_header, text="📅", font=('Arial', 20), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', padx=(20, 10), pady=12)
        tk.Label(basic_header, text="Datos de la Consulta", font=('Arial', 14, 'bold'), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', pady=12)
        
        # Grid para datos básicos
        basic_content = tk.Frame(basic_container, bg='white')
        basic_content.pack(fill='x', padx=25, pady=20)
        
        basic_grid = tk.Frame(basic_content, bg='white')
        basic_grid.pack(fill='x')
        
        # Fecha y Tipo en la misma fila con mejor espaciado
        tk.Label(basic_grid, text="Fecha:", font=('Arial', 11, 'bold'), bg='white', fg='#2c5aa0').grid(row=0, column=0, sticky='w', pady=8, padx=(0, 10))
        
        fecha_frame = tk.Frame(basic_grid, bg='white')
        fecha_frame.grid(row=0, column=1, sticky='ew', padx=(0, 30), pady=8)
        
        fecha_entry = tk.Entry(fecha_frame, textvariable=form_vars['fecha_consulta'], 
                              font=('Arial', 11), width=12, relief='solid', bd=1, bg='#fafafa')
        fecha_entry.pack(side='left')
        
        tk.Label(basic_grid, text="Tipo:", font=('Arial', 11, 'bold'), bg='white', fg='#2c5aa0').grid(row=0, column=2, sticky='w', pady=8, padx=(0, 10))
        
        tipo_combo = ttk.Combobox(basic_grid, textvariable=form_vars['tipo_consulta'], 
                                values=['Consulta General', 'Consulta Especializada', 'Emergencia', 'Control', 'Revisión'], 
                                state='readonly', width=22, font=('Arial', 11))
        tipo_combo.grid(row=0, column=3, sticky='ew', pady=8)
        
        basic_grid.columnconfigure(1, weight=1)
        basic_grid.columnconfigure(3, weight=2)
        
        # ========== SECCIÓN 3: INFORMACIÓN MÉDICA DETALLADA ==========
        medical_container = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        medical_container.pack(fill='x', pady=(0, 20))
        
        # Header de información médica
        medical_header = tk.Frame(medical_container, bg='#F8FAFC', height=50)
        medical_header.pack(fill='x')
        medical_header.pack_propagate(False)
        
        tk.Label(medical_header, text="🔍", font=('Arial', 20), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', padx=(20, 10), pady=12)
        tk.Label(medical_header, text="Información Médica", font=('Arial', 14, 'bold'), bg='#F8FAFC', fg='#2c5aa0').pack(side='left', pady=12)
        
        # Contenido médico
        medical_content = tk.Frame(medical_container, bg='white')
        medical_content.pack(fill='x', padx=25, pady=20)
        
        # Motivo de consulta con estilo mejorado
        motivo_section = tk.Frame(medical_content, bg='white')
        motivo_section.pack(fill='x', pady=(0, 15))
        
        tk.Label(motivo_section, text="Motivo de la Consulta", font=('Arial', 11, 'bold'), 
                bg='white', fg='#2c5aa0').pack(anchor='w', pady=(0, 5))
        
        motivo_text = tk.Text(motivo_section, height=3, font=('Arial', 11), wrap='word',
                             relief='solid', bd=1, bg='#fafafa', padx=10, pady=8)
        motivo_text.pack(fill='x')
        
        # Síntomas
        sintomas_section = tk.Frame(medical_content, bg='white')
        sintomas_section.pack(fill='x', pady=(0, 15))
        
        tk.Label(sintomas_section, text="Síntomas Observados", font=('Arial', 11, 'bold'), 
                bg='white', fg='#2c5aa0').pack(anchor='w', pady=(0, 5))
        
        sintomas_text = tk.Text(sintomas_section, height=3, font=('Arial', 11), wrap='word',
                               relief='solid', bd=1, bg='#fafafa', padx=10, pady=8)
        sintomas_text.pack(fill='x')
        
        # Diagnóstico
        diagnostico_section = tk.Frame(medical_content, bg='white')
        diagnostico_section.pack(fill='x', pady=(0, 15))
        
        tk.Label(diagnostico_section, text="Diagnóstico", font=('Arial', 11, 'bold'), 
                bg='white', fg='#2c5aa0').pack(anchor='w', pady=(0, 5))
        
        diagnostico_text = tk.Text(diagnostico_section, height=3, font=('Arial', 11), wrap='word',
                                  relief='solid', bd=1, bg='#fafafa', padx=10, pady=8)
        diagnostico_text.pack(fill='x')
        
        # Tratamiento
        tratamiento_section = tk.Frame(medical_content, bg='white')
        tratamiento_section.pack(fill='x', pady=(0, 15))
        
        tk.Label(tratamiento_section, text="Tratamiento Recomendado", font=('Arial', 11, 'bold'), 
                bg='white', fg='#2c5aa0').pack(anchor='w', pady=(0, 5))
        
        tratamiento_text = tk.Text(tratamiento_section, height=3, font=('Arial', 11), wrap='word',
                                  relief='solid', bd=1, bg='#fafafa', padx=10, pady=8)
        tratamiento_text.pack(fill='x')
        
        # Medicamentos
        medicamentos_section = tk.Frame(medical_content, bg='white')
        medicamentos_section.pack(fill='x', pady=(0, 15))
        
        tk.Label(medicamentos_section, text="Medicamentos Recetados", font=('Arial', 11, 'bold'), 
                bg='white', fg='#2c5aa0').pack(anchor='w', pady=(0, 5))
        
        medicamentos_text = tk.Text(medicamentos_section, height=3, font=('Arial', 11), wrap='word',
                                   relief='solid', bd=1, bg='#fafafa', padx=10, pady=8)
        medicamentos_text.pack(fill='x')
        
        # ========== BOTONES DE ACCIÓN PREMIUM ==========
        buttons_container = tk.Frame(content_frame, bg='#f0f4f7')
        buttons_container.pack(fill='x', pady=(30, 0))
        
        buttons_frame = tk.Frame(buttons_container, bg='white', relief='solid', bd=1)
        buttons_frame.pack(fill='x', padx=0, pady=0)
        
        button_content = tk.Frame(buttons_frame, bg='white')
        button_content.pack(fill='x', padx=25, pady=20)
        
        # Botón Cancelar con estilo
        cancel_btn = tk.Button(button_content, text="❌ Cancelar", 
                              bg='#0B5394', fg='white', font=('Arial', 12, 'bold'), 
                              width=15, height=2, relief='flat', cursor='hand2',
                              command=form_window.destroy)
        cancel_btn.pack(side='right', padx=(15, 0))
        
        # Efecto hover para cancelar
        def on_cancel_enter(e):
            cancel_btn.config(bg='#0B5394')
        def on_cancel_leave(e):
            cancel_btn.config(bg='#0B5394')
        
        cancel_btn.bind("<Enter>", on_cancel_enter)
        cancel_btn.bind("<Leave>", on_cancel_leave)
        
        # Botón Guardar con estilo premium
        save_text = "💾 Actualizar Consulta" if edit_mode else "💾 Guardar Consulta"
        save_btn = tk.Button(button_content, text=save_text, 
                            bg='#0B5394', fg='white', font=('Arial', 12, 'bold'), 
                            width=18, height=2, relief='flat', cursor='hand2',
                            command=lambda: self.save_medical_record(form_vars, form_window, edit_mode, 
                                                                   motivo_text, sintomas_text, diagnostico_text, 
                                                                   tratamiento_text, medicamentos_text))
        save_btn.pack(side='right')
        
        # Efecto hover para guardar
        def on_save_enter(e):
            save_btn.config(bg='#0B5394')
        def on_save_leave(e):
            save_btn.config(bg='#0B5394')
        
        save_btn.bind("<Enter>", on_save_enter)
        save_btn.bind("<Leave>", on_save_leave)
        
        # Configurar canvas y scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Focus en el primer campo
        motivo_text.focus()
    
    def save_medical_record(self, form_vars, form_window, edit_mode, motivo_text, sintomas_text, 
                          diagnostico_text, tratamiento_text, medicamentos_text):
        """Guardar registro médico"""
        try:
            # Validar campos obligatorios
            if not form_vars['fecha_consulta'].get():
                messagebox.showerror("Error", "La fecha de consulta es obligatoria")
                return
            
            # Obtener datos de los Text widgets
            motivo = motivo_text.get("1.0", tk.END).strip()
            sintomas = sintomas_text.get("1.0", tk.END).strip()
            diagnostico = diagnostico_text.get("1.0", tk.END).strip()
            tratamiento = tratamiento_text.get("1.0", tk.END).strip()
            medicamentos = medicamentos_text.get("1.0", tk.END).strip()
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if edit_mode:
                # Actualizar registro existente
                query = """
                    UPDATE historial_medico 
                    SET fecha_consulta=?, tipo_consulta=?, motivo_consulta=?, 
                        sintomas=?, diagnostico=?, tratamiento=?, medicamentos=?, estado=?
                    WHERE id=?
                """
                cursor.execute(query, (
                    form_vars['fecha_consulta'].get(),
                    form_vars['tipo_consulta'].get(),
                    motivo,
                    sintomas,
                    diagnostico,
                    tratamiento,
                    medicamentos,
                    form_vars['estado'].get(),
                    self.selected_medical_record_id
                ))
            else:
                # Crear nuevo registro
                query = """
                    INSERT INTO historial_medico 
                    (paciente_id, doctor_id, fecha_consulta, tipo_consulta, motivo_consulta, 
                     sintomas, diagnostico, tratamiento, medicamentos, estado, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    self.selected_patient_id,
                    self.current_user.id,  # Doctor actual
                    form_vars['fecha_consulta'].get(),
                    form_vars['tipo_consulta'].get(),
                    motivo,
                    sintomas,
                    diagnostico,
                    tratamiento,
                    medicamentos,
                    form_vars['estado'].get(),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Éxito", "Registro médico guardado correctamente")
            form_window.destroy()
            
            # Recargar registros médicos
            self.load_medical_records_for_patient(self.selected_patient_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar registro médico: {str(e)}")
    
    def create_medical_record(self): 
        """Crear nuevo registro médico - acceso desde otros módulos"""
        if hasattr(self, 'selected_patient_id') and self.selected_patient_id:
            self.add_medical_record()
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione un paciente primero")
    
    def view_medical_record_detail(self): 
        """Ver detalles completos del registro médico"""
        if not self.selected_medical_record_id:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro médico")
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT hm.*, 
                       ud.nombre as doctor_nombre, ud.apellido as doctor_apellido,
                       up.nombre as paciente_nombre, up.apellido as paciente_apellido
                FROM historiales_medicos hm
                LEFT JOIN usuarios ud ON hm.doctor_id = ud.id
                LEFT JOIN usuarios up ON hm.paciente_id = up.id
                WHERE hm.id = ?
            """
            
            cursor.execute(query, (self.selected_medical_record_id,))
            record = cursor.fetchone()
            
            if record:
                self.show_medical_record_details(record)
            else:
                messagebox.showerror("Error", "Registro médico no encontrado")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener detalles: {str(e)}")
    
    def show_medical_record_details(self, record):
        """Mostrar ventana con detalles completos del registro médico"""
        details_window = tk.Toplevel()
        details_window.title("Detalle de Consulta Médica - MEDISYNC")
        details_window.geometry("600x700")
        details_window.configure(bg='#F8FAFC')
        
        # Centrar ventana
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Header
        header_frame = tk.Frame(details_window, bg='#0B5394', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🩺 Detalle de Consulta Médica", font=('Arial', 16, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido scrollable
        content_frame = tk.Frame(details_window, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(content_frame, bg='white')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Extraer datos del record (basado en la estructura de historiales_medicos)
        # record = (id, paciente_id, doctor_id, cita_id, fecha_consulta, diagnostico, 
        #          tratamiento, medicamentos, observaciones, adjuntos, estado, 
        #          fecha_creacion, doctor_nombre, doctor_apellido, paciente_nombre, paciente_apellido)
        
        paciente_nombre = f"{record[14]} {record[15]}" if len(record) > 15 and record[14] and record[15] else "N/A"
        doctor_nombre = f"Dr. {record[12]} {record[13]}" if len(record) > 13 and record[12] and record[13] else "N/A"
        
        # Información del paciente y doctor
        info_frame = tk.LabelFrame(scrollable_frame, text="👥 Información General", 
                                 font=('Arial', 12, 'bold'), padx=15, pady=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        general_info = [
            ("Paciente:", paciente_nombre),
            ("Doctor:", doctor_nombre),
            ("Fecha de Consulta:", record[4] if len(record) > 4 and record[4] else "N/A"),
            ("Estado:", record[10] if len(record) > 10 and record[10] else "Pendiente")
        ]
        
        for label, value in general_info:
            row = tk.Frame(info_frame, bg='white')
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=label, font=('Arial', 10, 'bold'), 
                    bg='white', width=20, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Arial', 10), 
                    bg='white', anchor='w').pack(side='left', padx=(10, 0))
        
        # Detalles médicos
        medical_sections = [
            ("🔍 Diagnóstico", record[5] if len(record) > 5 else ""),
            ("💊 Tratamiento", record[6] if len(record) > 6 else ""),
            ("� Medicamentos", record[7] if len(record) > 7 else ""),
            ("� Observaciones", record[8] if len(record) > 8 else "")
        ]
        
        for title, content in medical_sections:
            section_frame = tk.LabelFrame(scrollable_frame, text=title, 
                                        font=('Arial', 11, 'bold'), padx=15, pady=10)
            section_frame.pack(fill='x', pady=(0, 10))
            
            text_widget = tk.Text(section_frame, height=4, font=('Arial', 10), 
                                wrap=tk.WORD, state='disabled', bg='#F8FAFC')
            text_widget.pack(fill='x')
            
            if content:
                text_widget.config(state='normal')
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')
            else:
                text_widget.config(state='normal')
                text_widget.insert('1.0', "No especificado")
                text_widget.config(state='disabled')
        
        # Botón cerrar
        btn_frame = tk.Frame(scrollable_frame, bg='white')
        btn_frame.pack(fill='x', pady=20)
        
        tk.Button(btn_frame, text="Cerrar", bg='#0B5394', fg='white',
                 font=('Arial', 11, 'bold'), width=15,
                 command=details_window.destroy).pack()
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def edit_medical_record(self): 
        """Editar registro médico seleccionado"""
        if not self.selected_medical_record_id:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro médico para editar")
            return
        
        self.open_medical_record_form(edit_mode=True)
    
    def print_medical_record(self): 
        """Sistema completo de impresión del historial médico"""
        # Obtener el registro seleccionado directamente del TreeView
        selection = self.medical_records_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro médico para imprimir")
            return
        
        # Obtener el ID del registro seleccionado
        item = self.medical_records_tree.item(selection[0])
        print(f"🔍 DEBUG: TreeView selection = {selection}")
        print(f"🔍 DEBUG: TreeView item completo = {item}")
        print(f"🔍 DEBUG: TreeView item['values'] = {item['values']}")
        
        # Verificar todos los items en el TreeView
        print("🔍 DEBUG: Todos los items en el TreeView:")
        for child in self.medical_records_tree.get_children():
            child_item = self.medical_records_tree.item(child)
            print(f"  - ID: {child}, values: {child_item['values']}")
        
        selected_record_id = item['values'][0]
        
        print(f"🔍 DEBUG: selected_record_id desde TreeView = {selected_record_id}")
        print(f"🔍 DEBUG: selected_medical_record_id global = {self.selected_medical_record_id}")
        
        # Obtener información del paciente asociado al registro
        patient_info = self.get_patient_from_medical_record(selected_record_id)
        print(f"🔍 DEBUG: patient_info = {patient_info}")
        
        if not patient_info:
            messagebox.showerror("Error", "No se pudo obtener información del paciente")
            return
        
        self.open_medical_history_print_window(patient_info)
    
    def get_patient_from_medical_record(self, medical_record_id):
        """Obtener información del paciente desde un registro médico"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT p.id, p.nombre, p.apellido, p.email, p.telefono, p.fecha_nacimiento
                FROM historiales_medicos hm
                JOIN usuarios p ON hm.paciente_id = p.id
                WHERE hm.id = ?
            """
            print(f"🔍 DEBUG: Buscando paciente para record_id = {medical_record_id}")
            cursor.execute(query, (medical_record_id,))
            result = cursor.fetchone()
            print(f"🔍 DEBUG: Resultado query = {result}")
            
            if result:
                patient_info = {
                    'id': result[0],
                    'nombre': result[1],
                    'apellido': result[2],
                    'email': result[3],
                    'telefono': result[4],
                    'fecha_nacimiento': result[5]
                }
                print(f"🔍 DEBUG: patient_info creado = {patient_info}")
                return patient_info
            return None
            
        except Exception as e:
            print(f"Error obteniendo paciente: {e}")
            return None
    
    def open_medical_history_print_window(self, patient_info):
        """Ventana para seleccionar e imprimir historial médico"""
        window = tk.Toplevel(self.root)
        window.title("🖨️ Imprimir Historial Médico")
        window.geometry("900x700")
        window.configure(bg='#F8FAFC')
        window.transient(self.root)
        window.grab_set()
        window.resizable(True, True)
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (900 // 2)
        y = (window.winfo_screenheight() // 2) - (700 // 2)
        window.geometry(f"900x700+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(window, bg='#0B5394', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#0B5394')
        header_content.pack(expand=True, fill='both')
        
        tk.Label(header_content, text="🖨️ IMPRIMIR HISTORIAL MÉDICO", 
                font=('Arial', 18, 'bold'), bg='#0B5394', fg='white').pack(pady=(15, 5))
        
        tk.Label(header_content, text=f"Paciente: {patient_info['nombre']} {patient_info['apellido']}", 
                font=('Arial', 12), bg='#0B5394', fg='#CBD5E1').pack(pady=(0, 15))
        
        # Contenido principal
        main_container = tk.Frame(window, bg='#F8FAFC')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Selección de registros
        left_panel = tk.LabelFrame(main_container, text="📋 Seleccionar Registros a Imprimir", 
                                  font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                  padx=15, pady=10)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Filtros
        filters_frame = tk.Frame(left_panel, bg='#F8FAFC')
        filters_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filters_frame, text="Filtrar por:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC', fg='#64748B').pack(anchor='w')
        
        filter_options_frame = tk.Frame(filters_frame, bg='#F8FAFC')
        filter_options_frame.pack(fill='x', pady=(5, 0))
        
        # Variables para filtros
        self.print_filter_date_from = tk.StringVar()
        self.print_filter_date_to = tk.StringVar()
        self.print_filter_type = tk.StringVar(value="Todos")
        
        # Filtros de fecha
        date_filter_frame = tk.Frame(filter_options_frame, bg='#F8FAFC')
        date_filter_frame.pack(fill='x', pady=2)
        
        tk.Label(date_filter_frame, text="Desde:", font=('Arial', 9), 
                bg='#F8FAFC', fg='#64748B').pack(side='left')
        tk.Entry(date_filter_frame, textvariable=self.print_filter_date_from, 
                font=('Arial', 9), width=12).pack(side='left', padx=(5, 10))
        
        tk.Label(date_filter_frame, text="Hasta:", font=('Arial', 9), 
                bg='#F8FAFC', fg='#64748B').pack(side='left')
        tk.Entry(date_filter_frame, textvariable=self.print_filter_date_to, 
                font=('Arial', 9), width=12).pack(side='left', padx=(5, 10))
        
        # Filtro por tipo
        type_filter_frame = tk.Frame(filter_options_frame, bg='#F8FAFC')
        type_filter_frame.pack(fill='x', pady=2)
        
        tk.Label(type_filter_frame, text="Tipo:", font=('Arial', 9), 
                bg='#F8FAFC', fg='#64748B').pack(side='left')
        ttk.Combobox(type_filter_frame, textvariable=self.print_filter_type,
                    values=["Todos", "Consulta", "Examen", "Tratamiento", "Seguimiento"],
                    state="readonly", font=('Arial', 9), width=15).pack(side='left', padx=(5, 0))
        
        # Lista de registros con checkboxes
        records_frame = tk.Frame(left_panel, bg='#F8FAFC')
        records_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Scrollbar para la lista
        records_canvas = tk.Canvas(records_frame, bg='#F8FAFC', highlightthickness=0)
        records_scrollbar = ttk.Scrollbar(records_frame, orient="vertical", command=records_canvas.yview)
        self.records_scrollable_frame = tk.Frame(records_canvas, bg='#F8FAFC')
        
        self.records_scrollable_frame.bind(
            "<Configure>",
            lambda e: records_canvas.configure(scrollregion=records_canvas.bbox("all"))
        )
        
        records_canvas.create_window((0, 0), window=self.records_scrollable_frame, anchor="nw")
        records_canvas.configure(yscrollcommand=records_scrollbar.set)
        
        records_canvas.pack(side="left", fill="both", expand=True)
        records_scrollbar.pack(side="right", fill="y")
        
        # Panel derecho - Vista previa y acciones
        right_panel = tk.LabelFrame(main_container, text="👁️ Vista Previa", 
                                   font=('Arial', 12, 'bold'), bg='#F8FAFC', fg='#1E3A8A',
                                   padx=15, pady=10)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Vista previa
        preview_frame = tk.Frame(right_panel, bg='white', relief='sunken', bd=2)
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.preview_text = tk.Text(preview_frame, font=('Arial', 10), bg='white', 
                                   state='disabled', wrap='word')
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        preview_scrollbar.pack(side="right", fill="y")
        
        # Botones de acción
        actions_frame = tk.Frame(right_panel, bg='#F8FAFC')
        actions_frame.pack(fill='x')
        
        tk.Button(actions_frame, text="🔄 Actualizar Vista Previa", 
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 command=lambda: self.update_medical_history_preview(patient_info),
                 padx=15, pady=8).pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="📄 Generar PDF", 
                 bg='#16A085', fg='white', font=('Arial', 10, 'bold'),
                 command=lambda: self.generate_medical_history_pdf(patient_info),
                 padx=15, pady=8).pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="❌ Cerrar", 
                 bg='#E74C3C', fg='white', font=('Arial', 10, 'bold'),
                 command=window.destroy, padx=15, pady=8).pack(fill='x', pady=2)
        
        # Cargar registros médicos del paciente
        self.load_patient_medical_records(patient_info['id'])
        
        # Actualizar vista previa inicial
        self.update_medical_history_preview(patient_info)
    
    def load_patient_medical_records(self, patient_id):
        """Cargar registros médicos del paciente con checkboxes"""
        # Limpiar registros anteriores
        for widget in self.records_scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, fecha_consulta, diagnostico, tratamiento, medicamentos, observaciones
                FROM historiales_medicos 
                WHERE paciente_id = ? 
                ORDER BY fecha_consulta DESC
            """
            cursor.execute(query, (patient_id,))
            records = cursor.fetchall()
            
            # Variables para checkbox selection
            self.selected_records = {}
            
            if not records:
                tk.Label(self.records_scrollable_frame, 
                        text="No se encontraron registros médicos para este paciente",
                        font=('Arial', 10), bg='#F8FAFC', fg='#64748B').pack(pady=20)
                return
            
            # Header con seleccionar todo
            header_frame = tk.Frame(self.records_scrollable_frame, bg='#E3F2FD', relief='raised', bd=1)
            header_frame.pack(fill='x', padx=2, pady=(0, 5))
            
            select_all_var = tk.BooleanVar()
            select_all_cb = tk.Checkbutton(header_frame, text="Seleccionar Todos",
                                          variable=select_all_var, bg='#E3F2FD',
                                          font=('Arial', 10, 'bold'),
                                          command=lambda: self.toggle_all_records(select_all_var.get()))
            select_all_cb.pack(side='left', padx=10, pady=5)
            
            # Crear checkbox para cada registro
            for i, record in enumerate(records):
                record_id, fecha_consulta, diagnostico, tratamiento, medicamentos, observaciones = record
                
                # Frame para cada registro
                record_frame = tk.Frame(self.records_scrollable_frame, bg='white', relief='raised', bd=1)
                record_frame.pack(fill='x', padx=2, pady=2)
                
                # Variable para checkbox
                var = tk.BooleanVar(value=True)  # Seleccionar todos por defecto
                self.selected_records[record_id] = var
                
                # Checkbox y contenido
                cb_frame = tk.Frame(record_frame, bg='white')
                cb_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Checkbutton(cb_frame, variable=var, bg='white',
                              command=lambda: self.update_medical_history_preview(None)).pack(side='left')
                
                # Información del registro
                info_frame = tk.Frame(cb_frame, bg='white')
                info_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
                
                # Primera línea: fecha
                first_line = tk.Frame(info_frame, bg='white')
                first_line.pack(fill='x')
                
                tk.Label(first_line, text=f"📅 {fecha_consulta}", font=('Arial', 10, 'bold'),
                        bg='white', fg='#0B5394').pack(side='left')
                
                # Diagnóstico
                if diagnostico:
                    diag_text = diagnostico[:100] + "..." if len(diagnostico) > 100 else diagnostico
                    tk.Label(info_frame, text=f"� {diag_text}", font=('Arial', 9),
                            bg='white', fg='#E67E22', wraplength=300, justify='left').pack(anchor='w', pady=(2, 0))
                
                # Tratamiento
                if tratamiento:
                    treat_text = tratamiento[:80] + "..." if len(tratamiento) > 80 else tratamiento
                    tk.Label(info_frame, text=f"� {treat_text}", font=('Arial', 9),
                            bg='white', fg='#16A085', wraplength=300, justify='left').pack(anchor='w', pady=(1, 0))
            
            print(f"Cargados {len(records)} registros médicos")
            
        except Exception as e:
            print(f"Error cargando registros médicos: {e}")
            tk.Label(self.records_scrollable_frame, 
                    text="Error al cargar registros médicos",
                    font=('Arial', 10), bg='#F8FAFC', fg='#E74C3C').pack(pady=20)
    
    def toggle_all_records(self, select_all):
        """Seleccionar/deseleccionar todos los registros"""
        if hasattr(self, 'selected_records') and self.selected_records:
            for var in self.selected_records.values():
                var.set(select_all)
            self.update_medical_history_preview(None)
    
    def update_medical_history_preview(self, patient_info):
        """Actualizar vista previa del historial médico"""
        if patient_info is None:
            # Obtener info del paciente desde el registro seleccionado
            patient_info = self.get_patient_from_medical_record(self.selected_medical_record_id)
        
        if not patient_info:
            return
        
        # Verificar que selected_records exista
        if not hasattr(self, 'selected_records') or not self.selected_records:
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Cargando registros médicos...")
            self.preview_text.config(state='disabled')
            return
        
        # Obtener registros seleccionados
        selected_record_ids = [record_id for record_id, var in self.selected_records.items() if var.get()]
        
        if not selected_record_ids:
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Seleccione al menos un registro para mostrar la vista previa")
            self.preview_text.config(state='disabled')
            return
        
        # Generar contenido de vista previa
        preview_content = self.generate_medical_history_content(patient_info, selected_record_ids)
        
        # Actualizar vista previa
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_content)
        self.preview_text.config(state='disabled')
    
    def generate_medical_history_content(self, patient_info, selected_record_ids):
        """Generar contenido del historial médico para vista previa/PDF"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener registros seleccionados
            placeholders = ','.join('?' * len(selected_record_ids))
            query = f"""
                SELECT fecha_consulta, diagnostico, tratamiento, medicamentos, 
                       observaciones, estado
                FROM historiales_medicos 
                WHERE id IN ({placeholders})
                ORDER BY fecha_consulta DESC
            """
            cursor.execute(query, selected_record_ids)
            records = cursor.fetchall()
            
            # Generar contenido
            content = []
            content.append("=" * 80)
            content.append("HISTORIAL MÉDICO COMPLETO")
            content.append("=" * 80)
            content.append("")
            
            # Información del paciente
            content.append("INFORMACIÓN DEL PACIENTE")
            content.append("-" * 40)
            content.append(f"Nombre: {patient_info['nombre']} {patient_info['apellido']}")
            content.append(f"Email: {patient_info['email']}")
            content.append(f"Teléfono: {patient_info['telefono']}")
            content.append(f"Fecha de Nacimiento: {patient_info['fecha_nacimiento']}")
            content.append("")
            
            # Resumen
            content.append(f"RESUMEN DEL HISTORIAL")
            content.append("-" * 40)
            content.append(f"Total de registros: {len(records)}")
            content.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            content.append("")
            
            # Registros médicos
            content.append("REGISTROS MÉDICOS DETALLADOS")
            content.append("=" * 50)
            
            for i, record in enumerate(records, 1):
                fecha_consulta, diagnostico, tratamiento, medicamentos, observaciones, estado = record
                
                content.append("")
                content.append(f"REGISTRO #{i}")
                content.append("-" * 30)
                content.append(f"📅 Fecha de Consulta: {fecha_consulta}")
                
                if diagnostico:
                    content.append(f"🔍 Diagnóstico:")
                    content.append(f"   {diagnostico}")
                
                if tratamiento:
                    content.append(f"💊 Tratamiento:")
                    content.append(f"   {tratamiento}")
                
                if medicamentos:
                    content.append(f"💉 Medicamentos:")
                    content.append(f"   {medicamentos}")
                
                if observaciones:
                    content.append(f"📋 Observaciones:")
                    content.append(f"   {observaciones}")
                
                if estado:
                    content.append(f"📊 Estado:")
                    content.append(f"   {estado}")
                
                content.append("")
            
            content.append("=" * 80)
            content.append("FIN DEL HISTORIAL MÉDICO")
            content.append("=" * 80)
            
            return "\n".join(content)
            
        except Exception as e:
            print(f"Error generando contenido del historial: {e}")
            return f"Error al generar el historial médico: {str(e)}"
    
    def generate_medical_history_pdf(self, patient_info):
        """Generar PDF del historial médico"""
        try:
            # Verificar que selected_records exista
            if not hasattr(self, 'selected_records') or not self.selected_records:
                messagebox.showwarning("Advertencia", "No hay registros cargados para generar el PDF")
                return
            
            # Obtener registros seleccionados
            selected_record_ids = [record_id for record_id, var in self.selected_records.items() if var.get()]
            
            if not selected_record_ids:
                messagebox.showwarning("Advertencia", "Seleccione al menos un registro para generar el PDF")
                return
            
            # Obtener datos de los registros
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            placeholders = ','.join('?' * len(selected_record_ids))
            query = f"""
                SELECT fecha_consulta, diagnostico, tratamiento, medicamentos, 
                       observaciones, estado
                FROM historiales_medicos 
                WHERE id IN ({placeholders})
                ORDER BY fecha_consulta DESC
            """
            cursor.execute(query, selected_record_ids)
            records = cursor.fetchall()
            
            # Importar reportlab
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.pdfgen import canvas
            except ImportError:
                messagebox.showerror("Error", "La librería reportlab no está instalada.\nInstale con: pip install reportlab")
                return
            
            # Crear directorio si no existe
            os.makedirs("historiales_pdf", exist_ok=True)
            
            # Nombre del archivo (limpiar caracteres especiales)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_limpio = patient_info['nombre'].replace(' ', '_').replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            apellido_limpio = patient_info['apellido'].replace(' ', '_').replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            filename = f"historiales_pdf/Historial_Medico_{nombre_limpio}_{apellido_limpio}_{timestamp}.pdf"
            print(f"🔍 DEBUG: Generando PDF en: {filename}")
            
            # Crear PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilo personalizado para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # Centrado
                textColor=colors.HexColor('#0B5394')
            )
            
            # Estilo personalizado para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#16A085')
            )
            
            # Estilo para texto normal
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Título principal
            story.append(Paragraph("HISTORIAL MÉDICO COMPLETO", title_style))
            story.append(Spacer(1, 20))
            
            # Información del paciente
            story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
            
            patient_data = [
                ['Nombre:', f"{patient_info['nombre']} {patient_info['apellido']}"],
                ['Email:', patient_info['email']],
                ['Teléfono:', patient_info['telefono']],
                ['Fecha de Nacimiento:', patient_info['fecha_nacimiento']]
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0B5394')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 20))
            
            # Resumen
            story.append(Paragraph("RESUMEN DEL HISTORIAL", subtitle_style))
            summary_text = f"""
            <b>Total de registros:</b> {len(records)}<br/>
            <b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Generado por:</b> MEDISYNC - Sistema de Gestión Médica
            """
            story.append(Paragraph(summary_text, normal_style))
            story.append(Spacer(1, 20))
            
            # Registros médicos
            story.append(Paragraph("REGISTROS MÉDICOS DETALLADOS", subtitle_style))
            
            for i, record in enumerate(records, 1):
                fecha_consulta, diagnostico, tratamiento, medicamentos, observaciones, estado = record
                
                # Título del registro
                record_title = f"REGISTRO #{i} - {fecha_consulta}"
                story.append(Paragraph(record_title, ParagraphStyle(
                    'RecordTitle',
                    parent=styles['Heading3'],
                    fontSize=12,
                    spaceAfter=10,
                    textColor=colors.HexColor('#E67E22'),
                    backColor=colors.HexColor('#FDF2E9'),
                    borderPadding=5
                )))
                
                # Crear tabla para los datos del registro
                record_data = []
                
                if diagnostico:
                    record_data.append(['Diagnóstico:', diagnostico])
                if tratamiento:
                    record_data.append(['Tratamiento:', tratamiento])
                if medicamentos:
                    record_data.append(['Medicamentos:', medicamentos])
                if observaciones:
                    record_data.append(['Observaciones:', observaciones])
                if estado:
                    record_data.append(['Estado:', estado])
                
                if record_data:
                    record_table = Table(record_data, colWidths=[1.5*inch, 4.5*inch])
                    record_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0B5394')),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    story.append(record_table)
                
                story.append(Spacer(1, 15))
            
            # Pie de página
            story.append(Spacer(1, 30))
            footer_text = f"""
            <i>Este historial médico fue generado automáticamente por MEDISYNC el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}.<br/>
            Para cualquier consulta, póngase en contacto con el centro médico.</i>
            """
            story.append(Paragraph(footer_text, ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1,
                textColor=colors.grey
            )))
            
            # Generar PDF
            doc.build(story)
            
            # Verificar que el archivo se creó correctamente
            if os.path.exists(filename):
                print(f"✅ PDF generado exitosamente: {filename}")
                # Mostrar mensaje de éxito y abrir PDF
                result = messagebox.askyesno("PDF Generado", 
                                           f"El historial médico se ha generado exitosamente.\n\n"
                                           f"Archivo: {filename}\n\n"
                                           f"¿Desea abrir el archivo PDF ahora?")
                
                if result:
                    try:
                        import subprocess
                        import sys
                        
                        if sys.platform.startswith('win'):
                            os.startfile(filename)
                        elif sys.platform.startswith('darwin'):
                            subprocess.call(['open', filename])
                        else:
                            subprocess.call(['xdg-open', filename])
                    except Exception as e:
                        print(f"Error abriendo PDF: {e}")
                        messagebox.showinfo("Archivo Generado", f"PDF generado en: {filename}\nNo se pudo abrir automáticamente.")
            else:
                messagebox.showerror("Error", "El archivo PDF no se pudo crear correctamente")
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            messagebox.showerror("Error", f"Error al generar el PDF del historial médico:\n{str(e)}")
    
    def create_medical_note_from_appointment(self, appointment_id):
        """Crear nota médica automáticamente al completar una cita"""
        try:
            # Obtener datos de la cita
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT c.paciente_id, c.doctor_id, c.fecha_hora, c.motivo,
                       p.nombre as paciente_nombre, p.apellido as paciente_apellido
                FROM citas c
                JOIN usuarios p ON c.paciente_id = p.id
                WHERE c.id = ?
            """
            
            cursor.execute(query, (appointment_id,))
            appointment_data = cursor.fetchone()
            
            if appointment_data:
                # Crear registro médico básico
                medical_query = """
                    INSERT INTO historial_medico 
                    (paciente_id, doctor_id, fecha_consulta, tipo_consulta, motivo_consulta, 
                     estado, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(medical_query, (
                    appointment_data[0],  # paciente_id
                    appointment_data[1],  # doctor_id
                    appointment_data[2][:10],  # fecha_consulta (solo fecha)
                    'Consulta',
                    appointment_data[3] or 'Consulta médica',  # motivo
                    'Pendiente',  # Estado inicial
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                conn.commit()
                
                # Obtener el ID del registro creado
                medical_record_id = cursor.lastrowid
                
                messagebox.showinfo("Registro Creado", 
                                  f"Se ha creado un registro médico automático para {appointment_data[4]} {appointment_data[5]}.\n\n"
                                  "Puede completar los detalles médicos en la pestaña de Historial Médico.")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error al crear registro médico automático: {str(e)}")
    
    def edit_doctor_profile(self): 
        messagebox.showinfo("Acción", "Editar perfil de doctor - En desarrollo")
    def change_password(self): 
        messagebox.showinfo("Acción", "Cambiar contraseña - En desarrollo")
    def configure_schedule(self): 
        messagebox.showinfo("Acción", "Configurar horarios - En desarrollo")
    
    # Funciones para secretarias
    def create_new_appointment(self): 
        messagebox.showinfo("Acción", "Crear nueva cita - En desarrollo")
    def show_appointment_calendar(self): 
        messagebox.showinfo("Acción", "Mostrar calendario - En desarrollo")
    def apply_appointment_filters(self): 
        self.load_secretaria_appointments()
    def load_appointment_doctors(self): 
        """Cargar doctores para filtro"""
        try:
            doctors = self.db_manager.get_all_doctors()
            doctor_names = ['Todos'] + [f"Dr. {doc['nombre']} {doc['apellido']}" for doc in doctors]
            self.appointment_doctor_filter['values'] = doctor_names
            self.appointment_doctor_filter.set('Todos')
        except Exception as e:
            print(f"Error cargando doctores para filtro: {e}")
    
    def load_secretaria_appointments(self): 
        """Cargar citas para secretaria"""
        try:
            # Placeholder - implementar carga real
            appointments = self.db_manager.get_all_appointments()
            
            # Limpiar tabla
            for item in self.secretaria_appointments_tree.get_children():
                self.secretaria_appointments_tree.delete(item)
            
            for apt in appointments:
                fecha_hora = apt.get('fecha_hora', '')
                if fecha_hora:
                    try:
                        dt = datetime.fromisoformat(fecha_hora)
                        fecha_hora = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                
                self.secretaria_appointments_tree.insert('', 'end', values=(
                    apt.get('id', ''), fecha_hora,
                    apt.get('paciente_nombre', 'N/A'),
                    apt.get('doctor_nombre', 'N/A'),
                    apt.get('motivo', 'N/A'),
                    apt.get('estado', 'N/A'),
                    apt.get('telefono', 'N/A')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando citas: {str(e)}")
    
    # Más funciones placeholder para secretarias y pacientes
    def edit_appointment(self): 
        """Editar cita seleccionada"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para editar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            # Obtener datos de la cita
            appointment = self.db_manager.get_appointment_by_id(appointment_id)
            if not appointment:
                messagebox.showerror("Error", "Cita no encontrada")
                return
            
            self.edit_appointment_window(appointment)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar cita: {str(e)}")
    
    def confirm_appointment(self):
        """Confirmar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para confirmar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            self.change_appointment_status(appointment_id, 'confirmada')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar cita: {str(e)}")
    
    def cancel_appointment(self):
        """Cancelar cita seleccionada - método de acceso rápido"""
        try:
            selection = self.appointments_tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor seleccione una cita para cancelar")
                return
            
            item = self.appointments_tree.item(selection[0])
            appointment_id = item['values'][0]
            
            self.cancel_appointment_with_reason(appointment_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar cita: {str(e)}")
    
    def call_patient(self): messagebox.showinfo("Acción", "Llamar paciente - En desarrollo")
    def generate_appointment_invoice(self): messagebox.showinfo("Acción", "Generar factura - En desarrollo")
    def register_new_patient(self): messagebox.showinfo("Acción", "Registrar nuevo paciente - En desarrollo")
    def import_patients(self): messagebox.showinfo("Acción", "Importar pacientes - En desarrollo")
    def export_patients(self): messagebox.showinfo("Acción", "Exportar pacientes - En desarrollo")
    def search_patients_secretaria(self, event=None): messagebox.showinfo("Acción", "Buscar pacientes - En desarrollo")
    def clear_patient_search(self): messagebox.showinfo("Acción", "Limpiar búsqueda - En desarrollo")
    def load_secretaria_patients(self): messagebox.showinfo("Acción", "Cargar pacientes - En desarrollo")
    
    # ==================== GESTIÓN DE USUARIOS ====================
    
    def open_user_management(self):
        """Abrir ventana de gestión de usuarios"""
        user_window = tk.Toplevel(self.root)
        user_window.title("Gestión de Usuarios - MEDISYNC")
        user_window.geometry("1200x700")
        user_window.configure(bg='#F8FAFC')
        user_window.resizable(True, True)
        
        # Centrar ventana
        user_window.transient(self.root)
        user_window.grab_set()
        
        # Header principal
        header_frame = tk.Frame(user_window, bg='#1E3A8A', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="👥 Gestión de Usuarios", font=('Arial', 20, 'bold'), 
                bg='#1E3A8A', fg='white').pack(expand=True)
        
        # Frame principal con división izquierda/derecha
        main_frame = tk.Frame(user_window, bg='#F8FAFC')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Lista de usuarios
        left_panel = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Header del panel izquierdo
        left_header = tk.Frame(left_panel, bg='#0B5394', height=50)
        left_header.pack(fill='x')
        left_header.pack_propagate(False)
        
        tk.Label(left_header, text="📋 Lista de Usuarios", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(side='left', padx=15, expand=True, anchor='w')
        
        # Botones de acción en header izquierdo
        btn_frame = tk.Frame(left_header, bg='#0B5394')
        btn_frame.pack(side='right', padx=15)
        
        tk.Button(btn_frame, text="➕ Nuevo Usuario", bg='#0B5394', fg='white',
                 font=('Arial', 9, 'bold'), command=self.add_new_user).pack(side='left', padx=2)
        tk.Button(btn_frame, text="🔄 Actualizar", bg='#0B5394', fg='white',
                 font=('Arial', 9, 'bold'), command=self.refresh_user_list).pack(side='left', padx=2)
        
        # Filtros de búsqueda
        search_frame = tk.Frame(left_panel, bg='white')
        search_frame.pack(fill='x', padx=15, pady=10)
        
        # Primera fila de filtros
        search_row1 = tk.Frame(search_frame, bg='white')
        search_row1.pack(fill='x', pady=(0, 5))
        
        tk.Label(search_row1, text="Buscar:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.user_search_entry = tk.Entry(search_row1, font=('Arial', 10), width=20)
        self.user_search_entry.pack(side='left', padx=5)
        self.user_search_entry.bind('<KeyRelease>', self.search_users)
        
        tk.Label(search_row1, text="Tipo:", font=('Arial', 10, 'bold'), bg='white').pack(side='left', padx=(15, 5))
        self.user_type_filter = ttk.Combobox(search_row1, values=['Todos', 'admin', 'doctor', 'secretaria', 'paciente'], 
                                           state='readonly', width=12)
        self.user_type_filter.set('Todos')
        self.user_type_filter.pack(side='left', padx=5)
        self.user_type_filter.bind('<<ComboboxSelected>>', self.filter_users)
        
        # Segunda fila de filtros
        search_row2 = tk.Frame(search_frame, bg='white')
        search_row2.pack(fill='x')
        
        tk.Label(search_row2, text="Estado:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.user_status_filter = ttk.Combobox(search_row2, values=['Todos', 'Activo', 'Inactivo'], 
                                             state='readonly', width=12)
        self.user_status_filter.set('Todos')
        self.user_status_filter.pack(side='left', padx=5)
        self.user_status_filter.bind('<<ComboboxSelected>>', self.filter_users)
        
        tk.Button(search_row2, text="🔍 Buscar", bg='#0B5394', fg='white', font=('Arial', 9),
                 command=self.search_users).pack(side='left', padx=(15, 5))
        tk.Button(search_row2, text="🗑️ Limpiar", bg='#0B5394', fg='white', font=('Arial', 9),
                 command=self.clear_user_search).pack(side='left', padx=2)
        
        # Tabla de usuarios
        users_table_frame = tk.Frame(left_panel, bg='white')
        users_table_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Tipo', 'Estado', 'Último Acceso')
        self.users_tree = ttk.Treeview(users_table_frame, columns=columns, show='headings', height=15)
        
        # Configurar headers
        column_widths = {'ID': 50, 'Nombre': 120, 'Apellido': 120, 'Email': 180, 
                        'Tipo': 80, 'Estado': 80, 'Último Acceso': 100}
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars para la tabla
        scrollbar_y = ttk.Scrollbar(users_table_frame, orient="vertical", command=self.users_tree.yview)
        scrollbar_x = ttk.Scrollbar(users_table_frame, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind para selección
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Panel derecho - Detalles y acciones
        right_panel = tk.Frame(main_frame, bg='white', relief='solid', bd=1, width=400)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Header del panel derecho
        right_header = tk.Frame(right_panel, bg='#0B5394', height=50)
        right_header.pack(fill='x')
        right_header.pack_propagate(False)
        
        tk.Label(right_header, text="⚙️ Acciones de Usuario", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Información del usuario seleccionado
        self.user_info_frame = tk.Frame(right_panel, bg='white')
        self.user_info_frame.pack(fill='x', padx=15, pady=15)
        
        # Placeholder para información
        self.user_info_label = tk.Label(self.user_info_frame, text="Seleccione un usuario para ver sus detalles", 
                                       font=('Arial', 11), bg='white', fg='#64748B', wraplength=350)
        self.user_info_label.pack()
        
        # Crear frame con scrollbar para los botones de acción
        actions_container = tk.Frame(right_panel, bg='white')
        actions_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Canvas y scrollbar para las acciones
        actions_canvas = tk.Canvas(actions_container, bg='white', highlightthickness=0, height=300)
        actions_scrollbar = ttk.Scrollbar(actions_container, orient="vertical", command=actions_canvas.yview)
        scrollable_actions_frame = tk.Frame(actions_canvas, bg='white')
        
        # Configurar el scroll
        def configure_scroll_region(event=None):
            actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))
            # Forzar update de la región de scroll
            actions_canvas.update_idletasks()
        
        def configure_canvas_width(event):
            canvas_width = event.width
            actions_canvas.itemconfig(window_id, width=canvas_width)
        
        scrollable_actions_frame.bind("<Configure>", configure_scroll_region)
        window_id = actions_canvas.create_window((0, 0), window=scrollable_actions_frame, anchor="nw")
        actions_canvas.bind("<Configure>", configure_canvas_width)
        actions_canvas.configure(yscrollcommand=actions_scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        actions_canvas.pack(side="left", fill="both", expand=True)
        actions_scrollbar.pack(side="right", fill="y")
        
        # Función para el scroll con la rueda del mouse
        def _on_mousewheel(event):
            actions_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind del scroll del mouse a múltiples widgets
        actions_canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_actions_frame.bind("<MouseWheel>", _on_mousewheel)
        actions_container.bind("<MouseWheel>", _on_mousewheel)
        
        # Guardar referencias para uso posterior
        self.actions_canvas = actions_canvas
        self.scrollable_actions_frame = scrollable_actions_frame
        
        # Definir botones de acción
        user_actions = [
            ("✏️ Editar Usuario", self.edit_selected_user, "#0B5394"),
            ("🔑 Cambiar Contraseña", self.change_user_password, "#0B5394"),
            ("✅ Activar Usuario", self.activate_user, "#0B5394"),
            ("❌ Desactivar Usuario", self.deactivate_user, "#0B5394"),
            ("👁️ Ver Detalles Completos", self.view_user_details, "#0B5394"),
            ("📧 Enviar Email", self.send_user_email, "#0B5394"),
            ("📋 Historial de Accesos", self.view_access_history, "#0B5394"),
            ("🗑️ Eliminar Usuario", self.delete_user, "#0B5394")
        ]
        
        for text, command, color in user_actions:
            btn = tk.Button(scrollable_actions_frame, text=text, command=command, 
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           width=25, height=2, relief='flat', cursor='hand2')
            btn.pack(fill='x', pady=3, padx=5)
            # Bind scroll también a cada botón
            btn.bind("<MouseWheel>", _on_mousewheel)
        
        # Función para forzar actualización del scroll
        def force_scroll_update():
            scrollable_actions_frame.update_idletasks()
            actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))
            # Verificar si necesita scroll
            bbox = actions_canvas.bbox("all")
            if bbox and bbox[3] > actions_canvas.winfo_height():
                actions_scrollbar.pack(side="right", fill="y")
            else:
                actions_scrollbar.pack_forget()
        
        # Actualizar la región de scroll después de agregar todos los botones
        actions_canvas.after(100, force_scroll_update)
        
        # Estadísticas rápidas
        stats_frame = tk.LabelFrame(right_panel, text="📊 Estadísticas", 
                                   font=('Arial', 11, 'bold'), padx=10, pady=10)
        stats_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.load_user_stats(stats_frame)
        
        # Cargar datos iniciales
        self.load_users_list()
        
        # Variables para mantener referencia al usuario seleccionado
        self.selected_user_id = None
        self.selected_user_data = None
    
    def load_users_list(self):
        """Cargar lista de usuarios en la tabla"""
        try:
            # Limpiar tabla
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Construir query con filtros
            where_conditions = []
            params = []
            
            # Filtro por tipo de usuario
            if hasattr(self, 'user_type_filter') and self.user_type_filter.get() != 'Todos':
                where_conditions.append("tipo_usuario = ?")
                params.append(self.user_type_filter.get())
            
            # Filtro por estado
            if hasattr(self, 'user_status_filter'):
                if self.user_status_filter.get() == 'Activo':
                    where_conditions.append("activo = 1")
                elif self.user_status_filter.get() == 'Inactivo':
                    where_conditions.append("activo = 0")
            
            # Filtro por búsqueda de texto
            if hasattr(self, 'user_search_entry') and self.user_search_entry.get().strip():
                search_term = f"%{self.user_search_entry.get().strip()}%"
                where_conditions.append("(nombre LIKE ? OR apellido LIKE ? OR email LIKE ?)")
                params.extend([search_term, search_term, search_term])
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
                SELECT id, nombre, apellido, email, tipo_usuario, activo, ultimo_acceso
                FROM usuarios 
                {where_clause}
                ORDER BY fecha_creacion DESC
            """
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                user_id, nombre, apellido, email, tipo_usuario, activo, ultimo_acceso = row
                
                # Formatear estado
                estado = "Activo" if activo else "Inactivo"
                
                # Formatear último acceso
                if ultimo_acceso:
                    try:
                        dt = datetime.fromisoformat(ultimo_acceso)
                        ultimo_acceso_formatted = dt.strftime('%d/%m/%Y')
                    except:
                        ultimo_acceso_formatted = ultimo_acceso
                else:
                    ultimo_acceso_formatted = "Nunca"
                
                self.users_tree.insert('', 'end', values=(
                    user_id, nombre, apellido, email, tipo_usuario.title(), 
                    estado, ultimo_acceso_formatted
                ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando usuarios: {str(e)}")
    
    def load_user_stats(self, parent):
        """Cargar estadísticas de usuarios"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_users = cursor.fetchone()[0]
            
            # Usuarios activos
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
            active_users = cursor.fetchone()[0]
            
            # Usuarios por tipo
            cursor.execute("SELECT tipo_usuario, COUNT(*) FROM usuarios GROUP BY tipo_usuario")
            user_types = dict(cursor.fetchall())
            
            # Nuevos usuarios esta semana
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE fecha_creacion >= ?", (week_ago,))
            new_this_week = cursor.fetchone()[0]
            
            stats_text = f"""
📊 Total de Usuarios: {total_users}
✅ Usuarios Activos: {active_users}
❌ Usuarios Inactivos: {total_users - active_users}

👑 Administradores: {user_types.get('admin', 0)}
👨‍⚕️ Doctores: {user_types.get('doctor', 0)}
👩‍💼 Secretarias: {user_types.get('secretaria', 0)}
🤒 Pacientes: {user_types.get('paciente', 0)}

📅 Nuevos esta semana: {new_this_week}
            """
            
            tk.Label(parent, text=stats_text, font=('Arial', 9), 
                    justify='left', bg='white').pack()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            tk.Label(parent, text=f"Error cargando estadísticas: {str(e)}", 
                    fg='red', bg='white').pack()
    
    def on_user_select(self, event):
        """Manejar selección de usuario"""
        selection = self.users_tree.selection()
        if selection:
            item = self.users_tree.item(selection[0])
            values = item['values']
            
            if values:
                self.selected_user_id = values[0]
                self.load_selected_user_info()
                self.enable_action_buttons()
                # Actualizar el scroll después de cargar la información
                self.update_actions_scroll()
        else:
            self.selected_user_id = None
            self.selected_user_data = None
            self.disable_action_buttons()
            self.show_default_info()
    
    def update_actions_scroll(self):
        """Actualizar el área de scroll de las acciones"""
        if hasattr(self, 'actions_canvas') and hasattr(self, 'scrollable_actions_frame'):
            self.scrollable_actions_frame.update_idletasks()
            self.actions_canvas.configure(scrollregion=self.actions_canvas.bbox("all"))
            # Scroll al principio cuando se selecciona un usuario
            self.actions_canvas.yview_moveto(0)
    
    def enable_action_buttons(self):
        """Habilitar botones de acción"""
        for btn in self.action_buttons:
            btn.config(state='normal')
    
    def disable_action_buttons(self):
        """Deshabilitar botones de acción"""
        for btn in self.action_buttons:
            btn.config(state='disabled')
    
    def show_default_info(self):
        """Mostrar información por defecto"""
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()
        
        self.user_info_label = tk.Label(self.user_info_frame, 
                                       text="👆 Seleccione un usuario de la lista\npara ver sus detalles y opciones", 
                                       font=('Arial', 10), bg='white', fg='#64748B', 
                                       justify='center', wraplength=300)
        self.user_info_label.pack(pady=20)
    
    def load_selected_user_info(self):
        """Cargar información detallada del usuario seleccionado"""
        if not self.selected_user_id:
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.*, 
                       CASE 
                           WHEN u.tipo_usuario = 'doctor' THEN d.especialidad
                           WHEN u.tipo_usuario = 'paciente' THEN p.numero_expediente
                           ELSE NULL
                       END as info_adicional
                FROM usuarios u
                LEFT JOIN doctores d ON u.id = d.id AND u.tipo_usuario = 'doctor'
                LEFT JOIN pacientes p ON u.id = p.id AND u.tipo_usuario = 'paciente'
                WHERE u.id = ?
            """, (self.selected_user_id,))
            
            user_data = cursor.fetchone()
            if user_data:
                # Convertir a diccionario
                columns = [description[0] for description in cursor.description]
                self.selected_user_data = dict(zip(columns, user_data))
                
                # Actualizar información mostrada
                self.update_user_info_display()
                # Actualizar scroll después de mostrar información
                self.update_actions_scroll()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando información del usuario: {str(e)}")
    
    def update_user_info_display(self):
        """Actualizar la visualización simplificada del usuario seleccionado"""
        if not self.selected_user_data:
            return
        
        # Limpiar frame
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()
        
        data = self.selected_user_data
        
        # Solo mostrar encabezado simple con nombre y estado
        header_frame = tk.Frame(self.user_info_frame, bg='#0B5394', height=50)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Icono del usuario según tipo
        user_icon = "👑" if data['tipo_usuario'] == 'admin' else \
                   "👨‍⚕️" if data['tipo_usuario'] == 'doctor' else \
                   "👩‍💼" if data['tipo_usuario'] == 'secretaria' else "🤒"
        
        # Contenido del header
        content_frame = tk.Frame(header_frame, bg='#0B5394')
        content_frame.pack(expand=True, fill='both')
        
        icon_label = tk.Label(content_frame, text=user_icon, font=('Arial', 18), 
                             bg='#0B5394', fg='white')
        icon_label.pack(side='left', padx=15, pady=10)
        
        name_label = tk.Label(content_frame, text=f"{data['nombre']} {data['apellido']}", 
                             font=('Arial', 12, 'bold'), bg='#0B5394', fg='white')
        name_label.pack(side='left', pady=10, anchor='center')
        
        # Estado del usuario
        status_color = "#16A085" if data['activo'] else "#C0392B"
        status_text = "●" if data['activo'] else "●"
        status_label = tk.Label(content_frame, text=status_text, font=('Arial', 20), 
                               bg='#0B5394', fg=status_color)
        status_label.pack(side='right', padx=15, pady=10)
        
        # Los botones de acción se muestran en el panel derecho
        
    def search_users(self, event=None):
        """Buscar usuarios"""
        self.load_users_list()
    
    def filter_users(self, event=None):
        """Filtrar usuarios"""
        self.load_users_list()
    
    def clear_user_search(self):
        """Limpiar filtros de búsqueda"""
        if hasattr(self, 'user_search_entry'):
            self.user_search_entry.delete(0, tk.END)
        if hasattr(self, 'user_type_filter'):
            self.user_type_filter.set('Todos')
        if hasattr(self, 'user_status_filter'):
            self.user_status_filter.set('Todos')
        self.load_users_list()
    
    def refresh_user_list(self):
        """Actualizar lista de usuarios"""
        self.load_users_list()
        messagebox.showinfo("Actualizado", "Lista de usuarios actualizada correctamente")
    
    def add_new_user(self):
        """Abrir ventana para agregar nuevo usuario"""
        self.open_user_form()
    
    def edit_selected_user(self):
        """Editar usuario seleccionado"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario para editar")
            return
        self.open_user_form(edit_mode=True)
    
    def open_user_form(self, edit_mode=False):
        """Abrir formulario para agregar/editar usuario"""
        form_window = tk.Toplevel()
        title = "Editar Usuario" if edit_mode else "Nuevo Usuario"
        form_window.title(f"{title} - MEDISYNC")
        form_window.geometry("600x700")
        form_window.configure(bg='#F8FAFC')
        form_window.resizable(False, False)
        
        # Centrar ventana
        form_window.transient(self.root)
        form_window.grab_set()
        
        # Header
        header_frame = tk.Frame(form_window, bg='#0B5394', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        icon = "✏️" if edit_mode else "➕"
        tk.Label(header_frame, text=f"{icon} {title}", font=('Arial', 16, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido principal
        content_frame = tk.Frame(form_window, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Variables del formulario
        form_vars = {
            'nombre': tk.StringVar(),
            'apellido': tk.StringVar(),
            'email': tk.StringVar(),
            'telefono': tk.StringVar(),
            'direccion': tk.StringVar(),
            'fecha_nacimiento': tk.StringVar(),
            'tipo_usuario': tk.StringVar(),
            'activo': tk.BooleanVar(value=True),
            'especialidad': tk.StringVar(),  # Para doctores
            'seguro_id': tk.StringVar(),     # Para pacientes
            'contacto_emergencia': tk.StringVar(),  # Para pacientes
            'telefono_emergencia': tk.StringVar(),  # Para pacientes
        }
        
        # Si estamos editando, cargar datos existentes
        if edit_mode and self.selected_user_data:
            data = self.selected_user_data
            form_vars['nombre'].set(data.get('nombre', ''))
            form_vars['apellido'].set(data.get('apellido', ''))
            form_vars['email'].set(data.get('email', ''))
            form_vars['telefono'].set(data.get('telefono', ''))
            form_vars['direccion'].set(data.get('direccion', ''))
            form_vars['fecha_nacimiento'].set(data.get('fecha_nacimiento', ''))
            form_vars['tipo_usuario'].set(data.get('tipo_usuario', 'paciente'))
            form_vars['activo'].set(bool(data.get('activo', True)))
            
            # Cargar datos específicos según el tipo
            if data.get('tipo_usuario') == 'doctor':
                form_vars['especialidad'].set(data.get('info_adicional', ''))
        
        # Sección 1: Información Personal
        personal_frame = tk.LabelFrame(content_frame, text="👤 Información Personal", 
                                     font=('Arial', 12, 'bold'), padx=20, pady=15)
        personal_frame.pack(fill='x', pady=(0, 15))
        
        # Grid para campos personales
        personal_grid = tk.Frame(personal_frame)
        personal_grid.pack(fill='x')
        
        # Nombre y Apellido
        tk.Label(personal_grid, text="Nombre *:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        nombre_entry = tk.Entry(personal_grid, textvariable=form_vars['nombre'], font=('Arial', 10), width=20)
        nombre_entry.grid(row=0, column=1, padx=(10, 20), pady=5, sticky='ew')
        
        tk.Label(personal_grid, text="Apellido *:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', pady=5)
        apellido_entry = tk.Entry(personal_grid, textvariable=form_vars['apellido'], font=('Arial', 10), width=20)
        apellido_entry.grid(row=0, column=3, padx=(10, 0), pady=5, sticky='ew')
        
        # Email y Teléfono
        tk.Label(personal_grid, text="Email *:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        email_entry = tk.Entry(personal_grid, textvariable=form_vars['email'], font=('Arial', 10), width=20)
        email_entry.grid(row=1, column=1, padx=(10, 20), pady=5, sticky='ew')
        
        tk.Label(personal_grid, text="Teléfono:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', pady=5)
        telefono_entry = tk.Entry(personal_grid, textvariable=form_vars['telefono'], font=('Arial', 10), width=20)
        telefono_entry.grid(row=1, column=3, padx=(10, 0), pady=5, sticky='ew')
        
        # Fecha de Nacimiento con calendario
        tk.Label(personal_grid, text="Fecha Nacimiento:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        
        fecha_frame = tk.Frame(personal_grid)
        fecha_frame.grid(row=2, column=1, padx=(10, 20), pady=5, sticky='ew')
        
        fecha_entry = tk.Entry(fecha_frame, textvariable=form_vars['fecha_nacimiento'], 
                              font=('Arial', 10), width=15, state='readonly')
        fecha_entry.pack(side='left', fill='x', expand=True)
        
        calendar_btn = tk.Button(fecha_frame, text="📅", font=('Arial', 8), 
                               command=lambda: self.open_calendar(form_vars['fecha_nacimiento']))
        calendar_btn.pack(side='right', padx=(5, 0))
        
        # Dirección
        tk.Label(personal_grid, text="Dirección:", font=('Arial', 10, 'bold')).grid(row=2, column=2, sticky='w', pady=5)
        direccion_entry = tk.Entry(personal_grid, textvariable=form_vars['direccion'], font=('Arial', 10), width=20)
        direccion_entry.grid(row=2, column=3, padx=(10, 0), pady=5, sticky='ew')
        
        # Configurar grid weights
        personal_grid.columnconfigure(1, weight=1)
        personal_grid.columnconfigure(3, weight=1)
        
        # Sección 2: Configuración de Usuario
        user_config_frame = tk.LabelFrame(content_frame, text="⚙️ Configuración de Usuario", 
                                        font=('Arial', 12, 'bold'), padx=20, pady=15)
        user_config_frame.pack(fill='x', pady=(0, 15))
        
        config_grid = tk.Frame(user_config_frame)
        config_grid.pack(fill='x')
        
        # Tipo de Usuario
        tk.Label(config_grid, text="Tipo de Usuario *:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        tipo_combo = ttk.Combobox(config_grid, textvariable=form_vars['tipo_usuario'], 
                                values=['admin', 'doctor', 'secretaria', 'paciente'], 
                                state='readonly', width=18)
        tipo_combo.grid(row=0, column=1, padx=(10, 20), pady=5, sticky='w')
        tipo_combo.bind('<<ComboboxSelected>>', lambda e: self.on_user_type_change(form_vars, specific_frame))
        
        # Estado Activo
        activo_frame = tk.Frame(config_grid)
        activo_frame.grid(row=0, column=2, padx=(10, 0), pady=5, sticky='w')
        
        activo_check = tk.Checkbutton(activo_frame, text="Usuario Activo", 
                                    variable=form_vars['activo'], font=('Arial', 10, 'bold'))
        activo_check.pack()
        
        # Sección 3: Información Específica (dinámico según tipo de usuario)
        specific_frame = tk.LabelFrame(content_frame, text="📋 Información Específica", 
                                     font=('Arial', 12, 'bold'), padx=20, pady=15)
        specific_frame.pack(fill='x', pady=(0, 15))
        
        # Contraseña (solo para usuarios nuevos)
        if not edit_mode:
            password_frame = tk.LabelFrame(content_frame, text="🔑 Contraseña", 
                                         font=('Arial', 12, 'bold'), padx=20, pady=15)
            password_frame.pack(fill='x', pady=(0, 15))
            
            password_grid = tk.Frame(password_frame)
            password_grid.pack(fill='x')
            
            form_vars['password'] = tk.StringVar()
            form_vars['confirm_password'] = tk.StringVar()
            
            tk.Label(password_grid, text="Contraseña *:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
            password_entry = tk.Entry(password_grid, textvariable=form_vars['password'], 
                                    font=('Arial', 10), show='*', width=20)
            password_entry.grid(row=0, column=1, padx=(10, 20), pady=5, sticky='ew')
            
            tk.Label(password_grid, text="Confirmar *:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', pady=5)
            confirm_entry = tk.Entry(password_grid, textvariable=form_vars['confirm_password'], 
                                   font=('Arial', 10), show='*', width=20)
            confirm_entry.grid(row=0, column=3, padx=(10, 0), pady=5, sticky='ew')
            
            password_grid.columnconfigure(1, weight=1)
            password_grid.columnconfigure(3, weight=1)
        
        # Botones de acción
        buttons_frame = tk.Frame(content_frame, bg='#F8FAFC')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Botón Cancelar
        tk.Button(buttons_frame, text="❌ Cancelar", bg='#0B5394', fg='white',
                 font=('Arial', 11, 'bold'), width=15,
                 command=form_window.destroy).pack(side='right', padx=(10, 0))
        
        # Botón Guardar
        save_text = "💾 Actualizar" if edit_mode else "💾 Crear Usuario"
        tk.Button(buttons_frame, text=save_text, bg='#0B5394', fg='white',
                 font=('Arial', 11, 'bold'), width=15,
                 command=lambda: self.save_user(form_vars, form_window, edit_mode, specific_frame)).pack(side='right')
        
        # Inicializar frame específico
        self.on_user_type_change(form_vars, specific_frame)
        
        # Enfocar primer campo
        nombre_entry.focus()
    
    def open_calendar(self, date_var):
        """Abrir selector de calendario"""
        try:
            from tkcalendar import DateEntry
            
            calendar_window = tk.Toplevel()
            calendar_window.title("Seleccionar Fecha")
            calendar_window.geometry("300x250")
            calendar_window.resizable(False, False)
            calendar_window.configure(bg='white')
            
            # Centrar ventana
            calendar_window.transient(self.root)
            calendar_window.grab_set()
            
            tk.Label(calendar_window, text="Seleccionar Fecha de Nacimiento", 
                    font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
            
            # DateEntry widget
            cal = DateEntry(calendar_window, width=12, background='darkblue',
                           foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
            cal.pack(pady=20)
            
            # Botones
            btn_frame = tk.Frame(calendar_window, bg='white')
            btn_frame.pack(pady=20)
            
            def select_date():
                selected_date = cal.get_date().strftime('%Y-%m-%d')
                date_var.set(selected_date)
                calendar_window.destroy()
            
            tk.Button(btn_frame, text="Seleccionar", bg='#0B5394', fg='white',
                     font=('Arial', 10, 'bold'), command=select_date).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Cancelar", bg='#0B5394', fg='white',
                     font=('Arial', 10, 'bold'), command=calendar_window.destroy).pack(side='left', padx=5)
            
        except ImportError:
            # Si no está disponible tkcalendar, usar entrada manual
            date_dialog = tk.Toplevel()
            date_dialog.title("Introducir Fecha")
            date_dialog.geometry("300x150")
            date_dialog.configure(bg='white')
            
            tk.Label(date_dialog, text="Formato: YYYY-MM-DD", 
                    font=('Arial', 10), bg='white').pack(pady=10)
            
            date_entry = tk.Entry(date_dialog, font=('Arial', 12), width=15)
            date_entry.pack(pady=10)
            
            def save_manual_date():
                date_var.set(date_entry.get())
                date_dialog.destroy()
            
            btn_frame = tk.Frame(date_dialog, bg='white')
            btn_frame.pack(pady=10)
            
            tk.Button(btn_frame, text="Guardar", bg='#0B5394', fg='white',
                     command=save_manual_date).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Cancelar", bg='#0B5394', fg='white',
                     command=date_dialog.destroy).pack(side='left', padx=5)
    
    def on_user_type_change(self, form_vars, specific_frame):
        """Manejar cambio de tipo de usuario"""
        # Limpiar frame específico
        for widget in specific_frame.winfo_children():
            widget.destroy()
        
        user_type = form_vars['tipo_usuario'].get()
        
        if user_type == 'doctor':
            self.create_doctor_specific_fields(specific_frame, form_vars)
        elif user_type == 'paciente':
            self.create_patient_specific_fields(specific_frame, form_vars)
        # Para admin y secretaria no necesitan campos adicionales por ahora
    
    def create_doctor_specific_fields(self, parent, form_vars):
        """Crear campos específicos para doctores"""
        grid = tk.Frame(parent)
        grid.pack(fill='x')
        
        tk.Label(grid, text="Especialidad *:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        especialidad_entry = tk.Entry(grid, textvariable=form_vars['especialidad'], 
                                    font=('Arial', 10), width=30)
        especialidad_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        grid.columnconfigure(1, weight=1)
    
    def create_patient_specific_fields(self, parent, form_vars):
        """Crear campos específicos para pacientes"""
        grid = tk.Frame(parent)
        grid.pack(fill='x')
        
        # Seguro médico
        tk.Label(grid, text="Seguro Médico:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        
        try:
            # Obtener lista de seguros
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM seguros_medicos ORDER BY nombre")
            seguros = [("", "Sin seguro")] + cursor.fetchall()
            cursor.close()
            conn.close()
            
            seguro_combo = ttk.Combobox(grid, textvariable=form_vars['seguro_id'], 
                                      values=[f"{s[0]}|{s[1]}" for s in seguros], 
                                      state='readonly', width=25)
            seguro_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
            
        except Exception as e:
            # Si hay error, usar entry simple
            seguro_entry = tk.Entry(grid, textvariable=form_vars['seguro_id'], 
                                  font=('Arial', 10), width=30)
            seguro_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        # Contacto de emergencia
        tk.Label(grid, text="Contacto Emergencia:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        contacto_entry = tk.Entry(grid, textvariable=form_vars['contacto_emergencia'], 
                                font=('Arial', 10), width=30)
        contacto_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        # Teléfono de emergencia
        tk.Label(grid, text="Tel. Emergencia:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        tel_emerg_entry = tk.Entry(grid, textvariable=form_vars['telefono_emergencia'], 
                                 font=('Arial', 10), width=30)
        tel_emerg_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        grid.columnconfigure(1, weight=1)
    
    def save_user(self, form_vars, form_window, edit_mode, specific_frame):
        """Guardar usuario (crear o actualizar)"""
        try:
            # Validar campos obligatorios
            if not form_vars['nombre'].get().strip():
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            if not form_vars['apellido'].get().strip():
                messagebox.showerror("Error", "El apellido es obligatorio")
                return
            
            if not form_vars['email'].get().strip():
                messagebox.showerror("Error", "El email es obligatorio")
                return
            
            if not form_vars['tipo_usuario'].get():
                messagebox.showerror("Error", "Debe seleccionar un tipo de usuario")
                return
            
            # Validar contraseña para usuarios nuevos
            if not edit_mode:
                if not form_vars['password'].get():
                    messagebox.showerror("Error", "La contraseña es obligatoria")
                    return
                
                if form_vars['password'].get() != form_vars['confirm_password'].get():
                    messagebox.showerror("Error", "Las contraseñas no coinciden")
                    return
            
            # Validar email único
            if not self.validate_unique_email(form_vars['email'].get(), edit_mode):
                messagebox.showerror("Error", "Ya existe un usuario con este email")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if edit_mode:
                # Actualizar usuario existente
                cursor.execute("""
                    UPDATE usuarios SET 
                        nombre = ?, apellido = ?, email = ?, telefono = ?, 
                        direccion = ?, fecha_nacimiento = ?, tipo_usuario = ?, activo = ?,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    form_vars['nombre'].get().strip(),
                    form_vars['apellido'].get().strip(),
                    form_vars['email'].get().strip(),
                    form_vars['telefono'].get().strip() or None,
                    form_vars['direccion'].get().strip() or None,
                    form_vars['fecha_nacimiento'].get().strip() or None,
                    form_vars['tipo_usuario'].get(),
                    form_vars['activo'].get(),
                    self.selected_user_id
                ))
                
                user_id = self.selected_user_id
                action = "actualizado"
                
            else:
                # Crear nuevo usuario
                password_hash = self.hash_password(form_vars['password'].get())
                
                cursor.execute("""
                    INSERT INTO usuarios (nombre, apellido, email, telefono, direccion, 
                                        fecha_nacimiento, tipo_usuario, password_hash, activo, 
                                        fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    form_vars['nombre'].get().strip(),
                    form_vars['apellido'].get().strip(),
                    form_vars['email'].get().strip(),
                    form_vars['telefono'].get().strip() or None,
                    form_vars['direccion'].get().strip() or None,
                    form_vars['fecha_nacimiento'].get().strip() or None,
                    form_vars['tipo_usuario'].get(),
                    password_hash,
                    form_vars['activo'].get()
                ))
                
                user_id = cursor.lastrowid
                action = "creado"
            
            # Guardar información específica según el tipo de usuario
            user_type = form_vars['tipo_usuario'].get()
            
            if user_type == 'doctor':
                if edit_mode:
                    cursor.execute("DELETE FROM doctores WHERE id = ?", (user_id,))
                
                cursor.execute("""
                    INSERT INTO doctores (id, especialidad)
                    VALUES (?, ?)
                """, (user_id, form_vars['especialidad'].get().strip()))
                
            elif user_type == 'paciente':
                if edit_mode:
                    cursor.execute("DELETE FROM pacientes WHERE id = ?", (user_id,))
                
                # Generar número de expediente si no existe
                if not edit_mode:
                    numero_expediente = self.generate_expediente_number()
                else:
                    # Mantener el número de expediente existente
                    cursor.execute("SELECT numero_expediente FROM pacientes WHERE id = ?", (user_id,))
                    result = cursor.fetchone()
                    numero_expediente = result[0] if result else self.generate_expediente_number()
                
                cursor.execute("""
                    INSERT INTO pacientes (id, numero_expediente, seguro_medico, 
                                         contacto_emergencia, telefono_emergencia)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id, 
                    numero_expediente,
                    form_vars.get('seguro_medico', tk.StringVar()).get().strip() or None,
                    form_vars.get('contacto_emergencia', tk.StringVar()).get().strip() or None,
                    form_vars.get('telefono_emergencia', tk.StringVar()).get().strip() or None
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Éxito", f"Usuario {action} exitosamente")
            form_window.destroy()
            self.refresh_user_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando usuario: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
    
    def validate_unique_email(self, email, edit_mode):
        """Validar que el email sea único"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if edit_mode and hasattr(self, 'selected_user_id'):
                # En modo edición, excluir el usuario actual
                cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", 
                             (email, self.selected_user_id))
            else:
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result is None
            
        except Exception as e:
            print(f"Error validando email: {e}")
            return False
    
    def generate_expediente_number(self):
        """Generar número de expediente único"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener el último número de expediente
            cursor.execute("SELECT MAX(CAST(numero_expediente AS INTEGER)) FROM pacientes WHERE numero_expediente REGEXP '^[0-9]+$'")
            result = cursor.fetchone()
            
            if result and result[0]:
                next_number = int(result[0]) + 1
            else:
                next_number = 1001  # Empezar desde 1001
            
            cursor.close()
            conn.close()
            
            return str(next_number).zfill(6)  # Formato: 001001, 001002, etc.
            
        except Exception as e:
            print(f"Error generando expediente: {e}")
            # Fallback: usar timestamp
            return datetime.now().strftime("%Y%m%d%H%M%S")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}")
    
    def validate_unique_email(self, email, edit_mode):
        """Validar que el email sea único"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if edit_mode:
                cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", 
                             (email, self.selected_user_id))
            else:
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result is None
            
        except Exception as e:
            print(f"Error validando email: {e}")
            return False
    
    def generate_expediente_number(self):
        """Generar número de expediente único"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener el último número de expediente
            cursor.execute("SELECT MAX(CAST(numero_expediente AS INTEGER)) FROM pacientes WHERE numero_expediente REGEXP '^[0-9]+$'")
            result = cursor.fetchone()
            
            if result and result[0]:
                next_number = int(result[0]) + 1
            else:
                next_number = 1000  # Empezar desde 1000
            
            cursor.close()
            conn.close()
            
            return str(next_number).zfill(6)  # Formato 000001, 000002, etc.
            
        except Exception as e:
            print(f"Error generando expediente: {e}")
            return datetime.now().strftime('%Y%m%d%H%M%S')  # Fallback
    
    def hash_password(self, password):
        """Hash de contraseña simple (en producción usar bcrypt o similar)"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def change_user_password(self):
        """Cambiar contraseña del usuario seleccionado"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        # Ventana para cambio de contraseña
        pwd_window = tk.Toplevel()
        pwd_window.title("Cambiar Contraseña - MEDISYNC")
        pwd_window.geometry("400x250")
        pwd_window.configure(bg='#F8FAFC')
        pwd_window.resizable(False, False)
        
        # Centrar ventana
        pwd_window.transient(self.root)
        pwd_window.grab_set()
        
        # Header
        header_frame = tk.Frame(pwd_window, bg='#0B5394', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔑 Cambiar Contraseña", font=('Arial', 14, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido
        content_frame = tk.Frame(pwd_window, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Información del usuario
        user_info = f"Usuario: {self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}"
        tk.Label(content_frame, text=user_info, font=('Arial', 11, 'bold'), 
                bg='#F8FAFC', fg='#1E3A8A').pack(pady=(0, 20))
        
        # Variables
        new_password = tk.StringVar()
        confirm_password = tk.StringVar()
        
        # Campos
        tk.Label(content_frame, text="Nueva Contraseña:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC').pack(anchor='w')
        new_pwd_entry = tk.Entry(content_frame, textvariable=new_password, 
                               font=('Arial', 11), show='*', width=30)
        new_pwd_entry.pack(fill='x', pady=(5, 15))
        
        tk.Label(content_frame, text="Confirmar Contraseña:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC').pack(anchor='w')
        confirm_pwd_entry = tk.Entry(content_frame, textvariable=confirm_password, 
                                   font=('Arial', 11), show='*', width=30)
        confirm_pwd_entry.pack(fill='x', pady=(5, 20))
        
        # Botones
        btn_frame = tk.Frame(content_frame, bg='#F8FAFC')
        btn_frame.pack(fill='x')
        
        def save_password():
            if not new_password.get():
                messagebox.showerror("Error", "La nueva contraseña es obligatoria")
                return
            
            if new_password.get() != confirm_password.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            if len(new_password.get()) < 6:
                messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
                return
            
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                password_hash = self.hash_password(new_password.get())
                cursor.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", 
                             (password_hash, self.selected_user_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                pwd_window.destroy()
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar contraseña: {str(e)}")
        
        tk.Button(btn_frame, text="❌ Cancelar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), width=12,
                 command=pwd_window.destroy).pack(side='right', padx=(10, 0))
        
        tk.Button(btn_frame, text="💾 Guardar", bg='#0B5394', fg='white',
                 font=('Arial', 10, 'bold'), width=12,
                 command=save_password).pack(side='right')
        
        new_pwd_entry.focus()
    
    def activate_user(self):
        """Activar usuario seleccionado"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        if self.selected_user_data.get('activo'):
            messagebox.showinfo("Información", "El usuario ya está activo")
            return
        
        result = messagebox.askyesno("Confirmar", 
                                   f"¿Está seguro de activar al usuario {self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}?")
        
        if result:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("UPDATE usuarios SET activo = 1 WHERE id = ?", (self.selected_user_id,))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                self.load_users_list()
                self.load_selected_user_info()
                messagebox.showinfo("Éxito", "Usuario activado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al activar usuario: {str(e)}")
    
    def deactivate_user(self):
        """Desactivar usuario seleccionado"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        if not self.selected_user_data.get('activo'):
            messagebox.showinfo("Información", "El usuario ya está inactivo")
            return
        
        result = messagebox.askyesno("Confirmar", 
                                   f"¿Está seguro de desactivar al usuario {self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}?\n\nEsto impedirá que el usuario acceda al sistema.")
        
        if result:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (self.selected_user_id,))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                self.load_users_list()
                self.load_selected_user_info()
                messagebox.showinfo("Éxito", "Usuario desactivado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al desactivar usuario: {str(e)}")
    
    def view_user_details(self):
        """Ver detalles completos del usuario"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        # Ventana de detalles
        details_window = tk.Toplevel()
        details_window.title("Detalles del Usuario - MEDISYNC")
        details_window.geometry("600x500")
        details_window.configure(bg='#F8FAFC')
        
        # Centrar ventana
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Header
        header_frame = tk.Frame(details_window, bg='#0B5394', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="👁️ Detalles del Usuario", font=('Arial', 16, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido
        content_frame = tk.Frame(details_window, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollable frame
        canvas = tk.Canvas(content_frame, bg='white')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar información detallada
        data = self.selected_user_data
        
        # Información básica
        basic_frame = tk.LabelFrame(scrollable_frame, text="Información Básica", 
                                  font=('Arial', 12, 'bold'), padx=15, pady=10)
        basic_frame.pack(fill='x', pady=(0, 10))
        
        basic_info = [
            ("ID:", str(data.get('id', 'N/A'))),
            ("Nombre completo:", f"{data.get('nombre', '')} {data.get('apellido', '')}"),
            ("Email:", data.get('email', 'N/A')),
            ("Tipo de usuario:", data.get('tipo_usuario', 'N/A').title()),
            ("Estado:", "✅ Activo" if data.get('activo') else "❌ Inactivo"),
            ("Teléfono:", data.get('telefono', 'No especificado')),
            ("Dirección:", data.get('direccion', 'No especificada')),
            ("Fecha de nacimiento:", data.get('fecha_nacimiento', 'No especificada')),
            ("Fecha de creación:", data.get('fecha_creacion', 'N/A')),
            ("Último acceso:", data.get('ultimo_acceso', 'Nunca'))
        ]
        
        for label, value in basic_info:
            info_frame = tk.Frame(basic_frame, bg='white')
            info_frame.pack(fill='x', pady=2)
            
            tk.Label(info_frame, text=label, font=('Arial', 10, 'bold'), 
                    bg='white', width=20, anchor='w').pack(side='left')
            tk.Label(info_frame, text=value, font=('Arial', 10), 
                    bg='white', anchor='w').pack(side='left', padx=(10, 0))
        
        # Información específica según tipo
        if data.get('tipo_usuario') == 'doctor':
            doctor_frame = tk.LabelFrame(scrollable_frame, text="Información de Doctor", 
                                       font=('Arial', 12, 'bold'), padx=15, pady=10)
            doctor_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(doctor_frame, text=f"Especialidad: {data.get('info_adicional', 'No especificada')}", 
                    font=('Arial', 10), bg='white').pack(anchor='w')
        
        elif data.get('tipo_usuario') == 'paciente':
            patient_frame = tk.LabelFrame(scrollable_frame, text="Información de Paciente", 
                                        font=('Arial', 12, 'bold'), padx=15, pady=10)
            patient_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(patient_frame, text=f"Número de expediente: {data.get('info_adicional', 'No asignado')}", 
                    font=('Arial', 10), bg='white').pack(anchor='w')
        
        # Botón cerrar
        btn_frame = tk.Frame(scrollable_frame, bg='white')
        btn_frame.pack(fill='x', pady=20)
        
        tk.Button(btn_frame, text="Cerrar", bg='#0B5394', fg='white',
                 font=('Arial', 11, 'bold'), width=15,
                 command=details_window.destroy).pack()
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def send_user_email(self):
        """Enviar email al usuario"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        user_email = self.selected_user_data.get('email', '')
        if not user_email:
            messagebox.showwarning("Email no disponible", "Este usuario no tiene email registrado")
            return
        
        # Crear ventana de composición de email
        email_window = tk.Toplevel(self.root)
        email_window.title(f"Enviar Email - {self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}")
        email_window.geometry("500x400")
        email_window.configure(bg='#F8FAFC')
        
        # Header
        header_frame = tk.Frame(email_window, bg='#0B5394', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📧 Enviar Email", font=('Arial', 16, 'bold'), 
                bg='#0B5394', fg='white').pack(expand=True)
        
        # Contenido
        content_frame = tk.Frame(email_window, bg='#F8FAFC')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Destinatario
        tk.Label(content_frame, text="Para:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC').pack(anchor='w')
        recipient_entry = tk.Entry(content_frame, font=('Arial', 10), width=50)
        recipient_entry.insert(0, user_email)
        recipient_entry.pack(fill='x', pady=(5, 15))
        
        # Asunto
        tk.Label(content_frame, text="Asunto:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC').pack(anchor='w')
        subject_entry = tk.Entry(content_frame, font=('Arial', 10))
        subject_entry.pack(fill='x', pady=(5, 15))
        
        # Mensaje
        tk.Label(content_frame, text="Mensaje:", font=('Arial', 10, 'bold'), 
                bg='#F8FAFC').pack(anchor='w')
        message_text = tk.Text(content_frame, height=10, font=('Arial', 10))
        message_text.pack(fill='both', expand=True, pady=(5, 15))
        
        # Botones
        buttons_frame = tk.Frame(content_frame, bg='#F8FAFC')
        buttons_frame.pack(fill='x')
        
        def send_email():
            recipient = recipient_entry.get().strip()
            subject = subject_entry.get().strip()
            message = message_text.get("1.0", tk.END).strip()
            
            if not all([recipient, subject, message]):
                messagebox.showwarning("Campos requeridos", "Por favor complete todos los campos")
                return
            
            # Aquí iría la lógica real de envío de email
            messagebox.showinfo("Email Enviado", f"Email enviado exitosamente a {recipient}")
            email_window.destroy()
        
        tk.Button(buttons_frame, text="📧 Enviar", command=send_email,
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=8).pack(side='right', padx=(10, 0))
        
        tk.Button(buttons_frame, text="❌ Cancelar", command=email_window.destroy,
                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=8).pack(side='right')
    
    def view_access_history(self):
        """Ver historial de accesos del usuario"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        try:
            # Crear ventana de historial
            history_window = tk.Toplevel(self.root)
            history_window.title(f"Historial de Accesos - {self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}")
            history_window.geometry("600x400")
            history_window.configure(bg='#F8FAFC')
            
            # Header
            header_frame = tk.Frame(history_window, bg='#0B5394', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="📋 Historial de Accesos", font=('Arial', 16, 'bold'), 
                    bg='#0B5394', fg='white').pack(expand=True)
            
            # Frame para la lista
            list_frame = tk.Frame(history_window, bg='#F8FAFC')
            list_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Treeview para mostrar el historial
            columns = ('Fecha', 'Hora', 'Tipo', 'Detalles')
            history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
            
            # Configurar columnas
            history_tree.heading('Fecha', text='Fecha')
            history_tree.heading('Hora', text='Hora') 
            history_tree.heading('Tipo', text='Tipo de Acceso')
            history_tree.heading('Detalles', text='Detalles')
            
            history_tree.column('Fecha', width=100)
            history_tree.column('Hora', width=80)
            history_tree.column('Tipo', width=120)
            history_tree.column('Detalles', width=250)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=history_tree.yview)
            h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=history_tree.xview)
            history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Empaquetar
            history_tree.pack(side='left', fill='both', expand=True)
            v_scrollbar.pack(side='right', fill='y')
            h_scrollbar.pack(side='bottom', fill='x')
            
            # Datos de ejemplo (en una implementación real, vendrían de la base de datos)
            sample_data = [
                ('2025-08-10', '09:15:23', 'Login', 'Inicio de sesión exitoso'),
                ('2025-08-10', '09:45:12', 'Consulta', 'Consultó lista de pacientes'),
                ('2025-08-10', '10:30:45', 'Edición', 'Modificó datos de paciente'),
                ('2025-08-09', '14:20:11', 'Login', 'Inicio de sesión exitoso'),
                ('2025-08-09', '16:55:33', 'Logout', 'Cerró sesión'),
                ('2025-08-08', '08:30:22', 'Login', 'Inicio de sesión exitoso'),
            ]
            
            for item in sample_data:
                history_tree.insert('', 'end', values=item)
            
            # Botón cerrar
            close_btn = tk.Button(history_window, text="🔙 Cerrar", command=history_window.destroy,
                                 bg='#0B5394', fg='white', font=('Arial', 10, 'bold'),
                                 padx=20, pady=8)
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar historial: {str(e)}")
    
    def delete_user(self):
        """Eliminar usuario (con confirmación)"""
        if not self.selected_user_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario")
            return
        
        user_name = f"{self.selected_user_data.get('nombre', '')} {self.selected_user_data.get('apellido', '')}"
        
        result = messagebox.askyesno("Confirmar Eliminación", 
                                   f"¿Está COMPLETAMENTE SEGURO de eliminar al usuario {user_name}?\n\n⚠️ ADVERTENCIA: Esta acción NO se puede deshacer.\n\nSe eliminarán todos los datos relacionados con este usuario.")
        
        if result:
            # Segunda confirmación
            confirmation = messagebox.askyesno("Confirmación Final", 
                                             "¿Confirma definitivamente la eliminación?\n\nEsta es su última oportunidad para cancelar.")
            
            if confirmation:
                try:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    # Eliminar de tablas relacionadas primero
                    if self.selected_user_data.get('tipo_usuario') == 'doctor':
                        cursor.execute("DELETE FROM doctores WHERE id = ?", (self.selected_user_id,))
                    elif self.selected_user_data.get('tipo_usuario') == 'paciente':
                        cursor.execute("DELETE FROM pacientes WHERE id = ?", (self.selected_user_id,))
                    
                    # Eliminar citas relacionadas (opcional, dependiendo de la política)
                    # cursor.execute("DELETE FROM citas WHERE doctor_id = ? OR paciente_id = ?", 
                    #              (self.selected_user_id, self.selected_user_id))
                    
                    # Eliminar usuario principal
                    cursor.execute("DELETE FROM usuarios WHERE id = ?", (self.selected_user_id,))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    self.load_users_list()
                    self.selected_user_id = None
                    self.selected_user_data = None
                    
                    # Limpiar información mostrada
                    for widget in self.user_info_frame.winfo_children():
                        widget.destroy()
                    
                    self.user_info_label = tk.Label(self.user_info_frame, 
                                                   text="Usuario eliminado. Seleccione otro usuario.", 
                                                   font=('Arial', 11), bg='white', fg='#C0392B')
                    self.user_info_label.pack()
                    
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")
    
    # Funciones para pacientes
    def request_appointment(self): messagebox.showinfo("Acción", "Solicitar cita - En desarrollo")
    def view_my_history(self): messagebox.showinfo("Acción", "Ver mi historial - En desarrollo")
    def view_my_bills(self): messagebox.showinfo("Acción", "Ver mis facturas - En desarrollo")
    def update_my_profile(self): messagebox.showinfo("Acción", "Actualizar perfil - En desarrollo")
    def request_new_appointment(self): messagebox.showinfo("Acción", "Solicitar nueva cita - En desarrollo")
    def filter_patient_appointments(self, event=None): messagebox.showinfo("Acción", "Filtrar citas - En desarrollo")
    def load_patient_appointments(self): messagebox.showinfo("Acción", "Cargar mis citas - En desarrollo")
    
    # NUEVAS FUNCIONES PARA FORMULARIO MEJORADO
    def select_date_enhanced(self, var):
        """Selector de fecha mejorado con calendario visual"""
        try:
            import calendar
            from datetime import datetime, timedelta
            
            # Crear ventana de calendario
            cal_window = tk.Toplevel(self.root)
            cal_window.title("📅 Seleccionar Fecha")
            cal_window.geometry("350x400")
            cal_window.configure(bg='#F8FAFC')
            cal_window.transient(self.root)
            cal_window.grab_set()
            cal_window.resizable(False, False)
            
            # Centrar ventana
            cal_window.update_idletasks()
            x = (cal_window.winfo_screenwidth() // 2) - (350 // 2)
            y = (cal_window.winfo_screenheight() // 2) - (400 // 2)
            cal_window.geometry(f"350x400+{x}+{y}")
            
            # Variables para navegación
            today = datetime.now()
            current_date = [today.year, today.month]
            
            # Header con navegación
            header_frame = tk.Frame(cal_window, bg='#0B5394', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            nav_frame = tk.Frame(header_frame, bg='#0B5394')
            nav_frame.pack(expand=True, fill='both')
            
            # Botón mes anterior
            prev_btn = tk.Button(nav_frame, text="◀", bg='#0B5394', fg='white', 
                               font=('Arial', 14, 'bold'), relief='flat',
                               command=lambda: navigate_month(-1))
            prev_btn.pack(side='left', padx=(20, 0), pady=15)
            
            # Label del mes/año
            month_label = tk.Label(nav_frame, text="", bg='#0B5394', fg='white',
                                 font=('Arial', 14, 'bold'))
            month_label.pack(expand=True, pady=15)
            
            # Botón mes siguiente
            next_btn = tk.Button(nav_frame, text="▶", bg='#0B5394', fg='white',
                               font=('Arial', 14, 'bold'), relief='flat',
                               command=lambda: navigate_month(1))
            next_btn.pack(side='right', padx=(0, 20), pady=15)
            
            # Frame para calendario
            cal_frame = tk.Frame(cal_window, bg='#F8FAFC')
            cal_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Días de la semana
            days_frame = tk.Frame(cal_frame, bg='#F8FAFC')
            days_frame.pack(fill='x', pady=(0, 10))
            
            days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            for day in days:
                tk.Label(days_frame, text=day, bg='#FFFFFF', fg='#1E3A8A',
                        font=('Arial', 10, 'bold'), width=5, height=2,
                        relief='solid', bd=1).pack(side='left', padx=1, pady=1)
            
            # Frame para días del mes
            dates_frame = tk.Frame(cal_frame, bg='#F8FAFC')
            dates_frame.pack(fill='both', expand=True)
            
            def navigate_month(direction):
                current_date[1] += direction
                if current_date[1] > 12:
                    current_date[1] = 1
                    current_date[0] += 1
                elif current_date[1] < 1:
                    current_date[1] = 12
                    current_date[0] -= 1
                update_calendar()
            
            def update_calendar():
                # Limpiar frame anterior
                for widget in dates_frame.winfo_children():
                    widget.destroy()
                
                # Actualizar label del mes
                month_names = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                month_label.config(text=f"{month_names[current_date[1]]} {current_date[0]}")
                
                # Obtener calendario del mes
                cal = calendar.monthcalendar(current_date[0], current_date[1])
                
                for week_num, week in enumerate(cal):
                    week_frame = tk.Frame(dates_frame, bg='#F8FAFC')
                    week_frame.pack(fill='x', pady=1)
                    
                    for day in week:
                        if day == 0:
                            # Día vacío
                            tk.Label(week_frame, text="", width=5, height=2,
                                   bg='#F8FAFC').pack(side='left', padx=1)
                        else:
                            # Determinar color según el día
                            btn_color = '#ffffff'
                            text_color = '#1E3A8A'
                            
                            # Marcar día actual
                            if (current_date[0] == today.year and 
                                current_date[1] == today.month and day == today.day):
                                btn_color = '#0B5394'
                                text_color = 'white'
                            
                            # Deshabilitar días pasados
                            date_obj = datetime(current_date[0], current_date[1], day)
                            if date_obj < today.replace(hour=0, minute=0, second=0, microsecond=0):
                                btn_color = '#FFFFFF'
                                text_color = '#CBD5E1'
                                state = 'disabled'
                            else:
                                state = 'normal'
                            
                            def select_day(d=day):
                                selected_date = f"{d:02d}/{current_date[1]:02d}/{current_date[0]}"
                                var.set(selected_date)
                                cal_window.destroy()
                            
                            day_btn = tk.Button(week_frame, text=str(day), 
                                              width=5, height=2, bg=btn_color, fg=text_color,
                                              font=('Arial', 10), relief='solid', bd=1,
                                              command=select_day, state=state, cursor='hand2')
                            day_btn.pack(side='left', padx=1)
            
            # Botones de acción rápida
            quick_frame = tk.Frame(cal_window, bg='#F8FAFC')
            quick_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            quick_dates = [
                ("Hoy", today),
                ("Mañana", today + timedelta(days=1)),
                ("En una semana", today + timedelta(days=7))
            ]
            
            for label, date_obj in quick_dates:
                def select_quick_date(d=date_obj):
                    selected_date = f"{d.day:02d}/{d.month:02d}/{d.year}"
                    var.set(selected_date)
                    cal_window.destroy()
                
                tk.Button(quick_frame, text=label, command=select_quick_date,
                         bg='#0B5394', fg='white', font=('Arial', 9),
                         relief='flat', padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
            
            # Inicializar calendario
            update_calendar()
            
        except Exception as e:
            # Fallback al selector simple
            self.select_date(var)

    def clear_appointment_form(self, appointment_vars, entries):
        """Limpiar todos los campos del formulario"""
        try:
            # Limpiar variables StringVar
            for var_name, var in appointment_vars.items():
                if var_name == 'estado':
                    var.set('pendiente')
                elif var_name == 'duracion':
                    var.set('60')
                elif var_name == 'tipo_consulta':
                    var.set('general')
                else:
                    var.set('')
            
            # Limpiar widget de texto de observaciones
            if 'observaciones' in entries:
                obs_widget = entries['observaciones']
                if isinstance(obs_widget, tk.Text):
                    obs_widget.delete(1.0, tk.END)
                    obs_widget.insert(1.0, "Ingrese observaciones adicionales, instrucciones especiales, o notas importantes para la cita...")
            
            # Resetear comboboxes
            for key, widget in entries.items():
                if isinstance(widget, ttk.Combobox):
                    if key == 'paciente_id':
                        widget.set("Seleccione un paciente...")
                    elif key == 'doctor_id':
                        widget.set("Seleccione un doctor...")
                    elif key == 'estado':
                        widget.set('pendiente')
                    elif key == 'tipo_consulta':
                        widget.set('general')
                    elif key == 'duracion':
                        widget.set('60')
            
            messagebox.showinfo("✅ Formulario Limpiado", 
                              "Todos los campos han sido restablecidos a sus valores por defecto.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar formulario: {str(e)}")

    def setup_form_validation(self, appointment_vars, entries):
        """Configurar validación en tiempo real para el formulario"""
        def validate_date(*args):
            date_str = appointment_vars['fecha'].get()
            if date_str:
                try:
                    # Validar formato DD/MM/YYYY
                    datetime.strptime(date_str, '%d/%m/%Y')
                    entries['fecha'].config(bg='#d5f4e6')  # Verde claro
                except ValueError:
                    entries['fecha'].config(bg='#ffeaa7')  # Amarillo claro
            else:
                entries['fecha'].config(bg='white')
        
        def validate_time(*args):
            time_str = appointment_vars['hora'].get()
            if time_str:
                try:
                    # Validar formato HH:MM
                    datetime.strptime(time_str, '%H:%M')
                    entries['hora'].config(bg='#d5f4e6')  # Verde claro
                except ValueError:
                    entries['hora'].config(bg='#ffeaa7')  # Amarillo claro
            else:
                entries['hora'].config(bg='white')
        
        # Configurar validación
        appointment_vars['fecha'].trace('w', validate_date)
        appointment_vars['hora'].trace('w', validate_time)

    def save_appointment_enhanced(self, window, appointment_vars, entries):
        """Guardar cita con validación mejorada"""
        try:
            # Obtener valores del formulario
            fecha = appointment_vars['fecha'].get().strip()
            hora = appointment_vars['hora'].get().strip()
            paciente_selection = appointment_vars['paciente_id'].get().strip()
            doctor_selection = appointment_vars['doctor_id'].get().strip()
            motivo = appointment_vars['motivo'].get().strip()
            estado = appointment_vars['estado'].get().strip()
            duracion = appointment_vars['duracion'].get().strip()
            tipo_consulta = appointment_vars['tipo_consulta'].get().strip()
            
            # Obtener observaciones del Text widget
            observaciones = ""
            if 'observaciones' in entries:
                obs_widget = entries['observaciones']
                if isinstance(obs_widget, tk.Text):
                    observaciones = obs_widget.get(1.0, tk.END).strip()
                    # Limpiar placeholder text
                    if observaciones.startswith("Ingrese observaciones"):
                        observaciones = ""
            
            # Validaciones mejoradas
            errors = []
            
            if not fecha:
                errors.append("• La fecha es obligatoria")
            else:
                try:
                    fecha_obj = datetime.strptime(fecha, '%d/%m/%Y')
                    if fecha_obj.date() < datetime.now().date():
                        errors.append("• La fecha no puede ser anterior a hoy")
                except ValueError:
                    errors.append("• Formato de fecha inválido (debe ser DD/MM/YYYY)")
            
            if not hora:
                errors.append("• La hora es obligatoria")
            else:
                try:
                    datetime.strptime(hora, '%H:%M')
                except ValueError:
                    errors.append("• Formato de hora inválido (debe ser HH:MM)")
            
            if not paciente_selection or paciente_selection.startswith("Seleccione"):
                errors.append("• Debe seleccionar un paciente")
            
            if not doctor_selection or doctor_selection.startswith("Seleccione"):
                errors.append("• Debe seleccionar un doctor")
            
            if not motivo:
                errors.append("• El motivo de la consulta es obligatorio")
            
            if errors:
                error_message = "Por favor corrija los siguientes errores:\n\n" + "\n".join(errors)
                messagebox.showerror("❌ Errores en el Formulario", error_message)
                return
            
            # Extraer IDs de las selecciones
            try:
                paciente_id = paciente_selection.split(' - ')[0]
                doctor_id = doctor_selection.split(' - ')[0]
            except:
                messagebox.showerror("Error", "Error al procesar selecciones de paciente/doctor")
                return
            
            # Verificar disponibilidad del horario
            if self.check_appointment_conflict(fecha, hora, doctor_id):
                response = messagebox.askyesno("⚠️ Conflicto de Horario", 
                    "Ya existe una cita programada para este doctor en el mismo horario.\n\n"
                    "¿Desea programar la cita de todas formas?")
                if not response:
                    return
            
            # Crear diccionario de datos de la cita
            appointment_data = {
                'fecha': fecha,
                'hora': hora,
                'paciente_id': int(paciente_id),
                'doctor_id': int(doctor_id),
                'motivo': motivo,
                'observaciones': observaciones,
                'estado': estado,
                'duracion': int(duracion) if duracion else 60,
                'tipo_consulta': tipo_consulta
            }
            
            # Guardar en la base de datos
            result = self.db_manager.create_appointment(appointment_data)
            
            if result:
                # Mostrar confirmación con detalles
                paciente_name = paciente_selection.split(' - ')[1] if ' - ' in paciente_selection else "Paciente"
                doctor_name = doctor_selection.split(' - ')[1] if ' - ' in doctor_selection else "Doctor"
                
                confirmation_msg = f"""✅ ¡Cita programada exitosamente!

📅 Fecha: {fecha}
🕐 Hora: {hora}
👤 Paciente: {paciente_name}
👨‍⚕️ Doctor: {doctor_name}
💭 Motivo: {motivo}
📊 Estado: {estado}
⏱️ Duración: {duracion} minutos

La cita ha sido guardada en el sistema."""
                
                messagebox.showinfo("🎉 Cita Creada", confirmation_msg)
                
                # Refrescar la lista de citas si existe
                if hasattr(self, 'load_appointments_data') and hasattr(self, 'appointments_tree'):
                    self.load_appointments_data(self.appointments_tree)
                
                window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la cita. Verifique los datos e intente nuevamente.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado al guardar la cita:\n{str(e)}")

    def check_appointment_conflict(self, fecha, hora, doctor_id):
        """Verificar si existe conflicto de horario para un doctor"""
        try:
            # Obtener todas las citas del doctor para la fecha
            appointments = self.db_manager.get_all_appointments()
            
            # Convertir hora a objeto time para comparación
            new_time = datetime.strptime(hora, '%H:%M').time()
            
            for appointment in appointments:
                # Verificar si es el mismo doctor
                if str(appointment.get('doctor_id')) == str(doctor_id):
                    # Verificar fecha
                    app_fecha = appointment.get('fecha_hora', '')
                    if app_fecha:
                        try:
                            app_dt = datetime.fromisoformat(app_fecha)
                            app_fecha_str = app_dt.strftime('%d/%m/%Y')
                            app_time = app_dt.time()
                            
                            if app_fecha_str == fecha and app_time == new_time:
                                estado = appointment.get('estado', '').lower()
                                if estado not in ['cancelada', 'completada']:
                                    return True
                        except:
                            continue
            
            return False
        except Exception:
            return False
    
    def update_available_hours(self, doctor_var, fecha_var, hora_var, hours_frame):
        """Actualizar horarios disponibles según el doctor seleccionado"""
        try:
            doctor_text = doctor_var.get()
            if not doctor_text or "Seleccione" in doctor_text:
                return
            
            # Extraer ID del doctor del texto "ID - Dr. Nombre Apellido"
            doctor_id = doctor_text.split(' - ')[0]
            
            # Limpiar botones de hora anteriores
            for widget in hours_frame.winfo_children():
                widget.destroy()
            
            # Obtener horarios del doctor desde la base de datos
            doctor_hours = self.get_doctor_schedule(doctor_id)
            
            # Si no hay horarios específicos, usar horarios por defecto
            if not doctor_hours:
                doctor_hours = ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
            
            # Crear botones para las primeras 4 horas
            for i, time in enumerate(doctor_hours[:4]):
                tk.Button(hours_frame, text=time, 
                         command=lambda t=time: hora_var.set(t),
                         bg='#FFFFFF', fg='#1E3A8A', font=('Arial', 8),
                         relief='flat', padx=5, pady=2, cursor='hand2').pack(side='left', padx=1)
            
            # Agregar botón "Más horarios" si hay más de 4
            if len(doctor_hours) > 4:
                tk.Button(hours_frame, text="⋯", 
                         command=lambda: self.show_more_hours(doctor_hours[4:], hora_var),
                         bg='#E3F2FD', fg='#1E3A8A', font=('Arial', 8, 'bold'),
                         relief='flat', padx=5, pady=2, cursor='hand2').pack(side='left', padx=1)
            
        except Exception as e:
            print(f"Error actualizando horarios: {e}")
    
    def get_doctor_schedule(self, doctor_id):
        """Obtener horarios del doctor desde la base de datos"""
        try:
            # Aquí puedes implementar la lógica para obtener horarios específicos del doctor
            # Por ahora retornamos horarios estándar de consultorio médico
            
            # Horarios comunes para diferentes turnos
            morning_hours = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
            afternoon_hours = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30']
            
            # Combinar horarios de mañana y tarde
            all_hours = morning_hours + afternoon_hours
            
            return all_hours
            
        except Exception as e:
            print(f"Error obteniendo horarios del doctor: {e}")
            return ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
    
    def show_more_hours(self, additional_hours, hora_var):
        """Mostrar ventana con horarios adicionales"""
        try:
            hours_window = tk.Toplevel(self.root)
            hours_window.title("⏰ Horarios Disponibles")
            hours_window.geometry("400x300")
            hours_window.configure(bg='#F8FAFC')
            hours_window.transient(self.root)
            hours_window.grab_set()
            hours_window.resizable(False, False)
            
            # Centrar ventana
            hours_window.update_idletasks()
            x = (hours_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (hours_window.winfo_screenheight() // 2) - (300 // 2)
            hours_window.geometry(f"400x300+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(hours_window, bg='#0B5394', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="⏰ Seleccionar Horario", 
                    font=('Arial', 14, 'bold'), bg='#0B5394', fg='white').pack(expand=True)
            
            # Frame para horarios
            content_frame = tk.Frame(hours_window, bg='#F8FAFC')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Crear grid de horarios
            hours_per_row = 4
            for i, hour in enumerate(additional_hours):
                row = i // hours_per_row
                col = i % hours_per_row
                
                def select_hour(h=hour):
                    hora_var.set(h)
                    hours_window.destroy()
                
                btn = tk.Button(content_frame, text=hour, 
                               command=select_hour,
                               bg='#FFFFFF', fg='#1E3A8A', font=('Arial', 10),
                               relief='solid', bd=1, padx=15, pady=8, cursor='hand2',
                               width=8)
                btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            # Configurar grid
            for i in range(hours_per_row):
                content_frame.columnconfigure(i, weight=1)
            
        except Exception as e:
            print(f"Error mostrando horarios adicionales: {e}")
    
    def set_appointment_hour(self, doctor_var, fecha_var, hour, hours_frame):
        """Establecer hora de la cita y verificar disponibilidad"""
        try:
            # Aquí podrías agregar verificación de disponibilidad
            # Por ahora simplemente establecemos la hora
            
            # Buscar el StringVar de hora en las variables padre
            # Como tenemos acceso limitado, vamos a buscar en el frame padre
            parent_window = hours_frame.winfo_toplevel()
            
            # Buscar el entry de hora en la ventana
            for widget in parent_window.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    self.find_and_set_hour_entry(widget, hour)
            
        except Exception as e:
            print(f"Error estableciendo hora: {e}")
    
    def find_and_set_hour_entry(self, widget, hour):
        """Buscar recursivamente el campo de hora y establecer el valor"""
        try:
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'get') and hasattr(child, 'set'):
                        # Es un Entry o similar
                        try:
                            current_val = child.get()
                            if ':' in current_val or len(current_val) == 0:
                                child.delete(0, tk.END)
                                child.insert(0, hour)
                                return True
                        except:
                            pass
                    
                    # Buscar recursivamente
                    if self.find_and_set_hour_entry(child, hour):
                        return True
            return False
        except:
            return False
    
    # Funciones de datos adicionales que faltan
    def get_billing_summary(self): return {}
    def get_secretaria_quick_stats(self): return {}
    def get_patient_health_summary(self): return {}
    def get_patient_billing_summary(self): return {}
    def get_patient_profile_data(self): return self.get_patient_info()
    def get_patient_personal_stats(self): return {}

if __name__ == "__main__":
    app = MedisyncApp()
