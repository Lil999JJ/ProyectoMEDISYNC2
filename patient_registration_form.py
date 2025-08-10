"""
Formulario de Registro de Pacientes para MEDISYNC
Interfaz completa y amigable para registro de nuevos pacientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import hashlib
import re
from PIL import Image, ImageTk
import os

def create_patient_registration_form(parent, db_manager):
    """Crear formulario de registro de pacientes con diseño moderno y amigable"""
    
    # Crear ventana de registro
    register_window = tk.Toplevel(parent)
    register_window.title("🩺 MEDISYNC - Registro de Nuevo Paciente")
    register_window.geometry("900x800")
    register_window.resizable(False, False)
    register_window.grab_set()
    register_window.configure(bg='#f8f9fa')
    
    # Centrar ventana
    register_window.transient(parent)
    register_window.update_idletasks()
    x = (register_window.winfo_screenwidth() // 2) - (900 // 2)
    y = (register_window.winfo_screenheight() // 2) - (800 // 2)
    register_window.geometry(f"900x800+{x}+{y}")
    
    # ==================== HEADER MODERNO ====================
    header_frame = tk.Frame(register_window, bg='#2c3e50', height=80)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    
    header_content = tk.Frame(header_frame, bg='#2c3e50')
    header_content.pack(expand=True, fill='both', padx=30, pady=15)
    
    # Icono y título
    tk.Label(header_content, text="🩺", font=('Arial', 28), bg='#2c3e50', fg='white').pack(side='left')
    
    title_frame = tk.Frame(header_content, bg='#2c3e50')
    title_frame.pack(side='left', fill='both', expand=True, padx=(15, 0))
    
    tk.Label(title_frame, text="REGISTRO DE NUEVO PACIENTE", 
             font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white').pack(anchor='w')
    tk.Label(title_frame, text="Complete todos los campos para crear su cuenta", 
             font=('Arial', 11), bg='#2c3e50', fg='#bdc3c7').pack(anchor='w')
    
    # ==================== CONTENIDO PRINCIPAL CON SCROLL ====================
    main_container = tk.Frame(register_window, bg='#f8f9fa')
    main_container.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Canvas y scrollbar para hacer scroll
    canvas = tk.Canvas(main_container, bg='#f8f9fa', highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Layout del canvas y scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Variables del formulario
    fields = {}
    
    # ==================== SECCIÓN 1: INFORMACIÓN PERSONAL ====================
    personal_section = create_section(scrollable_frame, "👤 Información Personal", "#3498db")
    
    # Fila 1: Nombre y Apellido
    row1 = tk.Frame(personal_section, bg='white')
    row1.pack(fill='x', pady=5)
    
    # Nombre
    name_frame = tk.Frame(row1, bg='white')
    name_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    tk.Label(name_frame, text="Nombre *", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['nombre'] = tk.Entry(name_frame, font=('Arial', 11), relief='solid', bd=1, 
                               bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['nombre'].pack(fill='x', ipady=8)
    
    # Apellido
    lastname_frame = tk.Frame(row1, bg='white')
    lastname_frame.pack(side='left', fill='x', expand=True)
    
    tk.Label(lastname_frame, text="Apellido *", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['apellido'] = tk.Entry(lastname_frame, font=('Arial', 11), relief='solid', bd=1,
                                 bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['apellido'].pack(fill='x', ipady=8)
    
    # Fila 2: Email
    email_frame = tk.Frame(personal_section, bg='white')
    email_frame.pack(fill='x', pady=5)
    
    tk.Label(email_frame, text="Correo Electrónico *", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['email'] = tk.Entry(email_frame, font=('Arial', 11), relief='solid', bd=1,
                              bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['email'].pack(fill='x', ipady=8)
    
    # Validación de email en tiempo real
    email_status = tk.Label(email_frame, text="", font=('Arial', 9), bg='white')
    email_status.pack(anchor='w')
    
    def validate_email(*args):
        email = fields['email'].get()
        if email and '@' in email and '.' in email.split('@')[-1]:
            email_status.config(text="✅ Email válido", fg='#27ae60')
        elif email:
            email_status.config(text="❌ Formato de email inválido", fg='#e74c3c')
        else:
            email_status.config(text="")
    
    fields['email'].bind('<KeyRelease>', validate_email)
    
    # Fila 3: Teléfono y Fecha de Nacimiento
    row3 = tk.Frame(personal_section, bg='white')
    row3.pack(fill='x', pady=5)
    
    # Teléfono
    phone_frame = tk.Frame(row3, bg='white')
    phone_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    tk.Label(phone_frame, text="Teléfono *", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['telefono'] = tk.Entry(phone_frame, font=('Arial', 11), relief='solid', bd=1,
                                 bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['telefono'].pack(fill='x', ipady=8)
    
    # Validación de teléfono
    phone_status = tk.Label(phone_frame, text="Ej: 809-555-1234", font=('Arial', 8), bg='white', fg='#7f8c8d')
    phone_status.pack(anchor='w')
    
    # Fecha de nacimiento
    birth_frame = tk.Frame(row3, bg='white')
    birth_frame.pack(side='left', fill='x', expand=True)
    
    tk.Label(birth_frame, text="Fecha de Nacimiento", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    
    # Frame para los selectores de fecha
    date_selectors = tk.Frame(birth_frame, bg='white')
    date_selectors.pack(fill='x')
    
    # Día
    tk.Label(date_selectors, text="Día:", font=('Arial', 9), bg='white').grid(row=0, column=0, sticky='w')
    fields['dia'] = ttk.Combobox(date_selectors, width=5, state="readonly", values=[str(i) for i in range(1, 32)])
    fields['dia'].grid(row=0, column=1, padx=(5, 10))
    
    # Mes
    tk.Label(date_selectors, text="Mes:", font=('Arial', 9), bg='white').grid(row=0, column=2, sticky='w')
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fields['mes'] = ttk.Combobox(date_selectors, width=10, state="readonly", values=meses)
    fields['mes'].grid(row=0, column=3, padx=(5, 10))
    
    # Año
    tk.Label(date_selectors, text="Año:", font=('Arial', 9), bg='white').grid(row=0, column=4, sticky='w')
    current_year = datetime.now().year
    years = [str(year) for year in range(current_year - 100, current_year + 1)][::-1]
    fields['año'] = ttk.Combobox(date_selectors, width=8, state="readonly", values=years)
    fields['año'].grid(row=0, column=5, padx=(5, 0))
    
    # Dirección
    address_frame = tk.Frame(personal_section, bg='white')
    address_frame.pack(fill='x', pady=5)
    
    tk.Label(address_frame, text="Dirección", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['direccion'] = tk.Text(address_frame, font=('Arial', 10), height=3, relief='solid', bd=1,
                                 bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['direccion'].pack(fill='x', pady=5)
    
    # Contraseña
    password_frame = tk.Frame(personal_section, bg='white')
    password_frame.pack(fill='x', pady=5)
    
    tk.Label(password_frame, text="Contraseña *", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    
    # Frame para contraseña y mostrar/ocultar
    pwd_container = tk.Frame(password_frame, bg='white')
    pwd_container.pack(fill='x')
    
    fields['password'] = tk.Entry(pwd_container, font=('Arial', 11), show='*', relief='solid', bd=1,
                                 bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['password'].pack(side='left', fill='x', expand=True, ipady=8)
    
    # Botón mostrar/ocultar contraseña
    show_password_var = tk.BooleanVar()
    def toggle_password():
        if show_password_var.get():
            fields['password'].config(show='')
            show_pwd_btn.config(text='🙈')
        else:
            fields['password'].config(show='*')
            show_pwd_btn.config(text='👁️')
    
    show_pwd_btn = tk.Button(pwd_container, text='👁️', command=toggle_password, 
                            bg='#ecf0f1', relief='flat', width=3)
    show_pwd_btn.pack(side='right', padx=(5, 0))
    
    # Medidor de fortaleza de contraseña
    pwd_strength = tk.Label(password_frame, text="", font=('Arial', 9), bg='white')
    pwd_strength.pack(anchor='w')
    
    def check_password_strength(*args):
        password = fields['password'].get()
        if len(password) < 4:
            pwd_strength.config(text="❌ Mínimo 4 caracteres", fg='#e74c3c')
        elif len(password) < 6:
            pwd_strength.config(text="🔶 Contraseña débil", fg='#f39c12')
        elif len(password) < 8:
            pwd_strength.config(text="🔸 Contraseña moderada", fg='#f1c40f')
        else:
            pwd_strength.config(text="✅ Contraseña fuerte", fg='#27ae60')
    
    fields['password'].bind('<KeyRelease>', check_password_strength)
    
    # ==================== SECCIÓN 2: INFORMACIÓN MÉDICA ====================
    medical_section = create_section(scrollable_frame, "🏥 Información Médica", "#e74c3c")
    
    # Fila 1: Tipo de sangre y Género
    med_row1 = tk.Frame(medical_section, bg='white')
    med_row1.pack(fill='x', pady=5)
    
    # Tipo de sangre
    blood_frame = tk.Frame(med_row1, bg='white')
    blood_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    tk.Label(blood_frame, text="Tipo de Sangre", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['tipo_sangre'] = ttk.Combobox(blood_frame, font=('Arial', 11), state="readonly",
                                        values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Desconocido'])
    fields['tipo_sangre'].pack(fill='x', ipady=5)
    fields['tipo_sangre'].set('Desconocido')
    
    # Género
    gender_frame = tk.Frame(med_row1, bg='white')
    gender_frame.pack(side='left', fill='x', expand=True)
    
    tk.Label(gender_frame, text="Género", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['genero'] = ttk.Combobox(gender_frame, font=('Arial', 11), state="readonly",
                                   values=['Masculino', 'Femenino', 'Otro', 'Prefiero no decir'])
    fields['genero'].pack(fill='x', ipady=5)
    
    # Alergias
    allergies_frame = tk.Frame(medical_section, bg='white')
    allergies_frame.pack(fill='x', pady=5)
    
    tk.Label(allergies_frame, text="Alergias Conocidas", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    tk.Label(allergies_frame, text="Especifique cualquier alergia a medicamentos, alimentos u otras sustancias", 
             font=('Arial', 8), bg='white', fg='#7f8c8d').pack(anchor='w')
    fields['alergias'] = tk.Text(allergies_frame, font=('Arial', 10), height=3, relief='solid', bd=1,
                                bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['alergias'].pack(fill='x', pady=5)
    fields['alergias'].insert('1.0', "Ninguna conocida")
    
    # Seguro médico
    insurance_frame = tk.Frame(medical_section, bg='white')
    insurance_frame.pack(fill='x', pady=5)
    
    tk.Label(insurance_frame, text="Seguro Médico", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    
    # Obtener seguros disponibles
    try:
        seguros = db_manager.get_medical_insurances()
        seguro_names = [seguro['nombre'] for seguro in seguros]
    except:
        seguro_names = ['Sin Seguro', 'ARS Senasa', 'ARS Humano', 'ARS Universal', 'ARS MetaData', 'Seguro Privado']
    
    fields['seguro_medico'] = ttk.Combobox(insurance_frame, font=('Arial', 11), state="readonly", values=seguro_names)
    fields['seguro_medico'].pack(fill='x', ipady=5)
    fields['seguro_medico'].set('Sin Seguro')
    
    # ==================== SECCIÓN 3: CONTACTO DE EMERGENCIA ====================
    emergency_section = create_section(scrollable_frame, "🚨 Contacto de Emergencia", "#f39c12")
    
    # Fila 1: Nombre y Relación
    emerg_row1 = tk.Frame(emergency_section, bg='white')
    emerg_row1.pack(fill='x', pady=5)
    
    # Nombre del contacto
    emerg_name_frame = tk.Frame(emerg_row1, bg='white')
    emerg_name_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    tk.Label(emerg_name_frame, text="Nombre del Contacto", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['contacto_emergencia'] = tk.Entry(emerg_name_frame, font=('Arial', 11), relief='solid', bd=1,
                                           bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['contacto_emergencia'].pack(fill='x', ipady=8)
    
    # Relación
    relation_frame = tk.Frame(emerg_row1, bg='white')
    relation_frame.pack(side='left', fill='x', expand=True)
    
    tk.Label(relation_frame, text="Relación", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['relacion_contacto'] = ttk.Combobox(relation_frame, font=('Arial', 11), state="readonly",
                                              values=['Padre/Madre', 'Esposo/Esposa', 'Hermano/Hermana', 
                                                     'Hijo/Hija', 'Amigo/Amiga', 'Otro'])
    fields['relacion_contacto'].pack(fill='x', ipady=5)
    
    # Teléfono de emergencia
    emerg_phone_frame = tk.Frame(emergency_section, bg='white')
    emerg_phone_frame.pack(fill='x', pady=5)
    
    tk.Label(emerg_phone_frame, text="Teléfono de Emergencia", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
    fields['telefono_emergencia'] = tk.Entry(emerg_phone_frame, font=('Arial', 11), relief='solid', bd=1,
                                           bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50')
    fields['telefono_emergencia'].pack(fill='x', ipady=8)
    
    # ==================== TÉRMINOS Y CONDICIONES ====================
    terms_section = create_section(scrollable_frame, "📋 Términos y Condiciones", "#9b59b6")
    
    terms_text = tk.Text(terms_section, height=6, font=('Arial', 9), bg='#f8f9fa', 
                        fg='#2c3e50', relief='solid', bd=1, wrap='word')
    terms_text.pack(fill='x', pady=5)
    
    terms_content = """Al registrarse en MEDISYNC, usted acepta:

• Proporcionar información veraz y actualizada
• Mantener la confidencialidad de su contraseña
• Permitir el uso de sus datos médicos para el tratamiento
• Cumplir con las políticas de la clínica
• Autorizar el procesamiento de sus datos personales conforme a la ley

Sus datos están protegidos y serán utilizados únicamente para fines médicos."""
    
    terms_text.insert('1.0', terms_content)
    terms_text.config(state='disabled')
    
    # Checkbox de aceptación
    accept_frame = tk.Frame(terms_section, bg='white')
    accept_frame.pack(fill='x', pady=10)
    
    fields['acepta_terminos'] = tk.BooleanVar()
    tk.Checkbutton(accept_frame, text="Acepto los términos y condiciones", 
                   variable=fields['acepta_terminos'], font=('Arial', 10, 'bold'),
                   bg='white', fg='#2c3e50').pack(anchor='w')
    
    # ==================== BOTONES FINALES ====================
    buttons_section = tk.Frame(scrollable_frame, bg='#f8f9fa', pady=20)
    buttons_section.pack(fill='x')
    
    buttons_frame = tk.Frame(buttons_section, bg='#f8f9fa')
    buttons_frame.pack()
    
    # Funciones de botones
    def cancel_registration():
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea cancelar el registro?"):
            register_window.destroy()
    
    def validate_and_register():
        """Validar y registrar paciente con validaciones avanzadas"""
        try:
            # Validar términos
            if not fields['acepta_terminos'].get():
                messagebox.showerror("Error", "Debe aceptar los términos y condiciones para continuar")
                return
            
            # Validar campos requeridos
            required_fields = {
                'nombre': 'Nombre',
                'apellido': 'Apellido', 
                'email': 'Correo electrónico',
                'telefono': 'Teléfono',
                'password': 'Contraseña'
            }
            
            for field, label in required_fields.items():
                value = fields[field].get().strip()
                if not value:
                    messagebox.showerror("Error", f"El campo '{label}' es obligatorio")
                    fields[field].focus()
                    return
            
            # Validar contraseña
            password = fields['password'].get().strip()
            if len(password) < 4:
                messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
                fields['password'].focus()
                return
            
            # Validar formato de email
            email = fields['email'].get().strip()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showerror("Error", "El formato del email no es válido")
                fields['email'].focus()
                return
            
            # Validar fecha de nacimiento
            fecha_nacimiento = ""
            if fields['dia'].get() and fields['mes'].get() and fields['año'].get():
                try:
                    mes_num = meses.index(fields['mes'].get()) + 1
                    fecha_nacimiento = f"{fields['año'].get()}-{mes_num:02d}-{fields['dia'].get().zfill(2)}"
                    # Validar que la fecha sea válida
                    datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                except (ValueError, IndexError):
                    messagebox.showerror("Error", "La fecha de nacimiento no es válida")
                    return
            
            # Preparar datos del usuario
            user_data = {
                'nombre': fields['nombre'].get().strip(),
                'apellido': fields['apellido'].get().strip(),
                'email': email.lower(),
                'telefono': fields['telefono'].get().strip(),
                'direccion': fields['direccion'].get('1.0', tk.END).strip(),
                'fecha_nacimiento': fecha_nacimiento,
                'tipo_usuario': 'paciente',
                'password': password,
                'activo': True
            }
            
            # Preparar datos del paciente
            patient_data = {
                'tipo_sangre': fields['tipo_sangre'].get(),
                'genero': fields['genero'].get(),
                'alergias': fields['alergias'].get('1.0', tk.END).strip(),
                'contacto_emergencia': fields['contacto_emergencia'].get().strip(),
                'relacion_contacto': fields['relacion_contacto'].get(),
                'telefono_emergencia': fields['telefono_emergencia'].get().strip(),
                'seguro_medico': fields['seguro_medico'].get()
            }
            
            # Mostrar confirmación
            confirm_message = f"""¿Confirma el registro con los siguientes datos?

👤 Paciente: {user_data['nombre']} {user_data['apellido']}
📧 Email: {user_data['email']}
📞 Teléfono: {user_data['telefono']}
🩸 Tipo de sangre: {patient_data['tipo_sangre']}
🏥 Seguro: {patient_data['seguro_medico']}"""
            
            if not messagebox.askyesno("Confirmar Registro", confirm_message):
                return
            
            # Crear el usuario paciente
            success, message = create_patient_user(db_manager, user_data, patient_data)
            
            if success:
                messagebox.showinfo("¡Registro Exitoso! 🎉", 
                    f"Bienvenido/a {user_data['nombre']} {user_data['apellido']}\n\n"
                    f"Su cuenta ha sido creada exitosamente.\n"
                    f"📧 Email: {user_data['email']}\n"
                    f"🔑 Contraseña: {user_data['password']}\n\n"
                    f"Ya puede iniciar sesión en MEDISYNC")
                register_window.destroy()
            else:
                messagebox.showerror("Error en el Registro", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado durante el registro:\n{str(e)}")
    
    # Botón Cancelar
    cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar", command=cancel_registration,
                          bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                          width=15, height=2, relief='raised', bd=3)
    cancel_btn.pack(side='left', padx=(0, 20))
    
    # Botón Registrar
    register_btn = tk.Button(buttons_frame, text="✅ Registrar Paciente", command=validate_and_register,
                            bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                            width=20, height=2, relief='raised', bd=3)
    register_btn.pack(side='left')
    
    # Focus inicial y configuración de scroll con mouse
    fields['nombre'].focus()
    
    # Habilitar scroll con rueda del mouse
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Bind Enter para navegar entre campos
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    for field in ['nombre', 'apellido', 'email', 'telefono', 'password']:
        fields[field].bind('<Return>', focus_next_widget)

def create_section(parent, title, color):
    """Crear una sección con diseño moderno"""
    section_frame = tk.Frame(parent, bg='#f8f9fa')
    section_frame.pack(fill='x', pady=(0, 20))
    
    # Header de sección
    header = tk.Frame(section_frame, bg=color, height=40)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    tk.Label(header, text=title, font=('Arial', 12, 'bold'), 
             bg=color, fg='white').pack(side='left', padx=15, pady=10)
    
    # Contenido de sección
    content = tk.Frame(section_frame, bg='white', relief='solid', bd=1)
    content.pack(fill='x', padx=2)
    
    content_inner = tk.Frame(content, bg='white')
    content_inner.pack(fill='x', padx=20, pady=15)
    
    return content_inner

def create_patient_user(db_manager, user_data, patient_data):
    """Crear nuevo usuario paciente en la base de datos con manejo de errores mejorado"""
    try:
        conn = db_manager.get_simple_connection()
        cursor = conn.cursor()
        
        # Verificar si el email ya existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (user_data['email'],))
        if cursor.fetchone()[0] > 0:
            return False, "El email ya está registrado en el sistema"
        
        # Hash de la contraseña
        password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO usuarios 
            (nombre, apellido, email, telefono, direccion, fecha_nacimiento, 
             tipo_usuario, password_hash, activo, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['nombre'], user_data['apellido'], user_data['email'],
            user_data['telefono'], user_data['direccion'], user_data['fecha_nacimiento'],
            user_data['tipo_usuario'], password_hash, user_data['activo'],
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        
        # Generar número de expediente automático
        expediente = f"EXP-{user_id:04d}"
        
        # Obtener ID del seguro médico
        seguro_id = get_seguro_id_by_name(db_manager, patient_data.get('seguro_medico', 'Sin Seguro'))
        
        # Insertar datos del paciente
        cursor.execute("""
            INSERT INTO pacientes 
            (id, numero_expediente, tipo_sangre, genero, alergias, contacto_emergencia, 
             relacion_contacto, telefono_emergencia, seguro_medico, seguro_medico_id, tiene_seguro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, expediente, patient_data['tipo_sangre'], patient_data.get('genero', ''),
            patient_data['alergias'], patient_data['contacto_emergencia'],
            patient_data.get('relacion_contacto', ''), patient_data['telefono_emergencia'],
            patient_data.get('seguro_medico', ''), seguro_id,
            1 if patient_data.get('seguro_medico') and patient_data.get('seguro_medico') != 'Sin Seguro' else 0
        ))
        
        conn.commit()
        return True, "Paciente registrado exitosamente"
        
    except Exception as e:
        print(f"Error creando paciente: {e}")
        if conn:
            conn.rollback()
        return False, f"Error en la base de datos: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_seguro_id_by_name(db_manager, seguro_name):
    """Obtener ID del seguro médico por nombre"""
    if not seguro_name or seguro_name == 'Sin Seguro':
        seguro_name = 'Sin Seguro'
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM seguros_medicos WHERE nombre = ?", (seguro_name,))
        result = cursor.fetchone()
        return result[0] if result else 4  # 4 es 'Sin Seguro' por defecto
    except Exception as e:
        print(f"Error obteniendo seguro: {e}")
        return 4  # Sin Seguro por defecto
    finally:
        cursor.close()
        conn.close()
