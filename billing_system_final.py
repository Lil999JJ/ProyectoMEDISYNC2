#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEDISYNC - SISTEMA DE FACTURACIÓN DEFINITIVO CON PDFs Y PAGOS
============================================================

Integración completa de todas las fases desarrolladas:
• Fase 1-5: Sistema completo de facturación
• Generación automática de PDFs
• Sistema de pagos con cambio/faltante
• Interfaz ultra moderna y amigable

Autor: MEDISYNC Team
Versión: DEFINITIVA 2.0
Fecha: 25 de Julio 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import json
import subprocess
import sys

# Instalar dependencias automáticamente
def install_dependencies():
    """Instalar dependencias necesarias para PDFs"""
    try:
        import reportlab
        import qrcode
        from PIL import Image
        print("✅ Dependencias para PDF disponibles")
        return True
    except ImportError:
        print("📦 Instalando dependencias para PDFs...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "qrcode[pil]", "pillow"])
            print("✅ Dependencias instaladas exitosamente")
            return True
        except:
            print("⚠️ No se pudieron instalar dependencias - PDFs no disponibles")
            return False

# Verificar e instalar dependencias
PDF_AVAILABLE = install_dependencies()

if PDF_AVAILABLE:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    import qrcode
    from PIL import Image

class PDFGenerator:
    """Generador de PDFs para facturas médicas"""
    
    def __init__(self):
        self.pdf_directory = "facturas_pdf"
        self.ensure_pdf_directory()
        
    def ensure_pdf_directory(self):
        """Crear directorio de PDFs si no existe"""
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)
    
    def generate_invoice_pdf(self, invoice_data, clinic_config, output_path):
        """Generar PDF de factura médica"""
        if not PDF_AVAILABLE:
            print("⚠️ PDFs no disponibles - dependencias faltantes")
            return False
        
        try:
            # Crear documento PDF
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_LEFT
            )
            
            # Header de la clínica
            story.append(Paragraph("🏥 " + clinic_config.get('nombre', 'MEDISYNC CLINIC'), title_style))
            story.append(Paragraph(f"📍 {clinic_config.get('direccion', 'Dirección no disponible')}", header_style))
            story.append(Paragraph(f"📞 {clinic_config.get('telefono', 'Teléfono no disponible')}", header_style))
            story.append(Paragraph(f"✉️ {clinic_config.get('email', 'Email no disponible')}", header_style))
            story.append(Spacer(1, 20))
            
            # Título de factura
            story.append(Paragraph(f"FACTURA MÉDICA", title_style))
            story.append(Paragraph(f"No. {invoice_data.get('numero_factura', 'N/A')}", header_style))
            story.append(Spacer(1, 20))
            
            # Información del paciente y doctor
            info_data = [
                ['👤 PACIENTE:', invoice_data.get('paciente_nombre', 'N/A')],
                ['👨‍⚕️ DOCTOR:', invoice_data.get('doctor_nombre', 'N/A')],
                ['📅 FECHA:', invoice_data.get('fecha_creacion', datetime.now().strftime('%d/%m/%Y'))],
                ['🛡️ SEGURO:', invoice_data.get('seguro_aplicado', 'Sin seguro')],
                ['💭 CONCEPTO:', invoice_data.get('concepto', 'Consulta médica')]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 30))
            
            # Servicios (si están disponibles)
            if 'servicios' in invoice_data and invoice_data['servicios']:
                story.append(Paragraph("SERVICIOS PRESTADOS", styles['Heading2']))
                
                servicios_data = [['Servicio', 'Cantidad', 'Precio Unitario', 'Total']]
                for servicio in invoice_data['servicios']:
                    servicios_data.append([
                        servicio.get('nombre', 'Servicio'),
                        str(servicio.get('cantidad', 1)),
                        f"₡{servicio.get('precio', 0):,.2f}",
                        f"₡{servicio.get('precio', 0) * servicio.get('cantidad', 1):,.2f}"
                    ])
                
                servicios_table = Table(servicios_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
                servicios_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(servicios_table)
                story.append(Spacer(1, 20))
            
            # Totales
            totales_data = []
            
            if invoice_data.get('monto_original'):
                totales_data.append(['Subtotal:', f"₡{float(invoice_data.get('monto_original', 0)):,.2f}"])
            
            if invoice_data.get('monto_descuento', 0) > 0:
                totales_data.append(['Descuento:', f"-₡{float(invoice_data.get('monto_descuento', 0)):,.2f}"])
            
            totales_data.append(['TOTAL A PAGAR:', f"₡{float(invoice_data.get('monto', 0)):,.2f}"])
            
            # Información de pago si existe
            if invoice_data.get('monto_pagado'):
                totales_data.append(['Monto Recibido:', f"₡{float(invoice_data.get('monto_pagado', 0)):,.2f}"])
                
                cambio = float(invoice_data.get('monto_pagado', 0)) - float(invoice_data.get('monto', 0))
                if cambio > 0:
                    totales_data.append(['Cambio:', f"₡{cambio:,.2f}"])
                elif cambio < 0:
                    totales_data.append(['Faltante:', f"₡{abs(cambio):,.2f}"])
            
            totales_table = Table(totales_data, colWidths=[4*inch, 2*inch])
            totales_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkgreen),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ]))
            
            story.append(totales_table)
            story.append(Spacer(1, 30))
            
            # Pie de página
            story.append(Paragraph("Gracias por confiar en nuestros servicios médicos", styles['Normal']))
            story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            
            # Generar código QR si está disponible
            try:
                qr_text = f"Factura: {invoice_data.get('numero_factura', 'N/A')} - Total: ₡{float(invoice_data.get('monto', 0)):,.2f}"
                qr = qrcode.QRCode(version=1, box_size=3, border=2)
                qr.add_data(qr_text)
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_path = "temp_qr.png"
                qr_img.save(qr_path)
                
                story.append(Spacer(1, 20))
                story.append(RLImage(qr_path, width=1.5*inch, height=1.5*inch))
                
                # Limpiar archivo temporal
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                    
            except Exception as e:
                print(f"⚠️ No se pudo generar código QR: {e}")
            
            # Construir PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            return False


class DatabaseManager:
    """Gestor de base de datos integrado"""
    
    def __init__(self, db_path="database/medisync.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_completed_appointments(self, days_back=30):
        """Obtener citas completadas sin facturar"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_limit = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            query = '''
            SELECT 
                c.id as cita_id,
                c.fecha_hora,
                c.motivo,
                c.paciente_id,
                c.doctor_id,
                p.nombre || ' ' || p.apellido as paciente_nombre,
                d.nombre || ' ' || d.apellido as doctor_nombre,
                doc.especialidad,
                seg.nombre as seguro_nombre,
                seg.descuento_porcentaje as porcentaje_descuento
            FROM citas c
            LEFT JOIN usuarios p ON c.paciente_id = p.id
            LEFT JOIN usuarios d ON c.doctor_id = d.id
            LEFT JOIN pacientes pac ON p.id = pac.id
            LEFT JOIN doctores doc ON d.id = doc.id
            LEFT JOIN seguros_medicos seg ON pac.seguro_medico_id = seg.id
            LEFT JOIN facturas f ON c.id = f.cita_id
            WHERE c.estado = 'completada' 
                AND f.cita_id IS NULL
                AND DATE(c.fecha_hora) >= ?
            ORDER BY c.fecha_hora DESC
            '''
            
            cursor.execute(query, [date_limit])
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error obteniendo citas: {e}")
            return []
        finally:
            conn.close()
    
    def get_appointment_details(self, cita_id):
        """Obtener detalles de una cita"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT 
                c.*,
                p.nombre || ' ' || p.apellido as paciente_nombre,
                p.telefono as paciente_telefono,
                d.nombre || ' ' || d.apellido as doctor_nombre,
                doc.especialidad,
                seg.nombre as seguro_nombre,
                seg.descuento_porcentaje as porcentaje_descuento
            FROM citas c
            LEFT JOIN usuarios p ON c.paciente_id = p.id
            LEFT JOIN usuarios d ON c.doctor_id = d.id
            LEFT JOIN pacientes pac ON p.id = pac.id
            LEFT JOIN doctores doc ON d.id = doc.id
            LEFT JOIN seguros_medicos seg ON pac.seguro_medico_id = seg.id
            WHERE c.id = ?
            ''', (cita_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            print(f"Error obteniendo detalles de cita: {e}")
            return None
        finally:
            conn.close()
    
    def create_invoice_from_appointment(self, cita_id, servicios, observaciones="", monto_pagado=0, metodo_pago="efectivo"):
        """Crear factura desde cita con información de pago"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            appointment = self.get_appointment_details(cita_id)
            if not appointment:
                return False, "Cita no encontrada", None
            
            # Generar número de factura
            numero_factura = self.generate_invoice_number()
            
            # Calcular totales
            subtotal = sum(float(s.get('precio', 0)) * int(s.get('cantidad', 1)) for s in servicios)
            
            # Calcular descuento si hay seguro
            porcentaje_descuento = float(appointment.get('porcentaje_descuento', 0))
            descuento = subtotal * (porcentaje_descuento / 100) if porcentaje_descuento else 0
            total = subtotal - descuento
            
            # Crear concepto descriptivo
            servicios_nombres = [s.get('nombre', 'Servicio') for s in servicios]
            concepto = f"Consulta médica - {', '.join(servicios_nombres[:2])}"
            if len(servicios) > 2:
                concepto += f" y {len(servicios) - 2} servicios más"
            
            # Fechas
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            fecha_vencimiento = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Determinar estado según pago
            if monto_pagado >= total:
                estado = 'pagada'
                fecha_pago = fecha_actual
            elif monto_pagado > 0:
                estado = 'pago_parcial'
                fecha_pago = fecha_actual
            else:
                estado = 'pendiente'
                fecha_pago = None
            
            # Crear factura usando el esquema correcto
            cursor.execute('''
            INSERT INTO facturas (
                numero_factura, paciente_id, doctor_id, cita_id,
                concepto, monto_original, monto_descuento, monto,
                estado, fecha_creacion, fecha_vencimiento, fecha_pago,
                metodo_pago, notas, seguro_aplicado, descuento_seguro,
                tipo_consulta, moneda
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_factura,
                appointment['paciente_id'],
                appointment['doctor_id'],
                cita_id,
                concepto,
                subtotal,
                descuento,
                total,
                estado,
                fecha_actual,
                fecha_vencimiento,
                fecha_pago,
                metodo_pago if monto_pagado > 0 else None,
                f"Generada desde sistema integrado. Servicios: {len(servicios)}. Pagado: ₡{monto_pagado:,.2f}. {observaciones}",
                appointment.get('seguro_nombre', 'Sin seguro'),
                porcentaje_descuento,
                appointment.get('especialidad', 'Consulta General'),
                'CRC'
            ))
            
            # Obtener ID de la factura creada
            factura_id = cursor.lastrowid
            
            conn.commit()
            
            # Crear objeto con datos completos para PDF
            invoice_data = {
                'id': factura_id,
                'numero_factura': numero_factura,
                'paciente_nombre': appointment.get('paciente_nombre'),
                'doctor_nombre': appointment.get('doctor_nombre'),
                'fecha_creacion': fecha_actual,
                'concepto': concepto,
                'monto_original': subtotal,
                'monto_descuento': descuento,
                'monto': total,
                'monto_pagado': monto_pagado,
                'seguro_aplicado': appointment.get('seguro_nombre', 'Sin seguro'),
                'servicios': servicios,
                'estado': estado,
                'metodo_pago': metodo_pago
            }
            
            return True, f"Factura {numero_factura} creada exitosamente", invoice_data
            
        except Exception as e:
            conn.rollback()
            return False, f"Error creando factura: {str(e)}", None
        finally:
            conn.close()
    
    def generate_invoice_number(self):
        """Generar número de factura"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM facturas')
            count = cursor.fetchone()[0]
            year = datetime.now().strftime('%Y')
            return f"FAC-{year}-{count + 1:04d}"
        except:
            return f"FAC-{datetime.now().strftime('%Y')}-0001"
        finally:
            conn.close()
    
    def get_medical_services(self):
        """Obtener servicios médicos"""
        # Servicios básicos hardcodeados por simplicidad
        return [
            {'codigo': 'CONS001', 'nombre': 'Consulta General', 'categoria': 'Consulta', 'precio': 1500.00},
            {'codigo': 'CONS002', 'nombre': 'Consulta Especializada', 'categoria': 'Consulta', 'precio': 2500.00},
            {'codigo': 'LAB001', 'nombre': 'Análisis de Sangre', 'categoria': 'Laboratorio', 'precio': 800.00},
            {'codigo': 'RAD001', 'nombre': 'Radiografía', 'categoria': 'Imagen', 'precio': 1800.00},
            {'codigo': 'PROC001', 'nombre': 'Procedimiento Menor', 'categoria': 'Procedimiento', 'precio': 1000.00}
        ]


class BillingSystemComplete:
    """Sistema de facturación completo e integrado con PDFs y pagos"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.pdf_generator = PDFGenerator() if PDF_AVAILABLE else None
        self.current_appointment = None
        self.selected_services = []
        
        # Configuración de clínica
        self.clinic_config = {
            'nombre': 'MEDISYNC - Centro Médico',
            'direccion': 'Avenida Central, San José, Costa Rica',
            'telefono': '+506 2000-0000',
            'email': 'info@medisync.cr'
        }
        
        # Variables de interfaz
        self.root = None
        self.appointments_tree = None
        self.services_tree = None
        self.invoice_services_tree = None
        self.search_var = None
        self.total_var = None
        self.subtotal_var = None
        self.discount_var = None
        self.payment_var = None
        self.change_var = None
        
    def create_interface(self):
        """Crear interfaz principal mejorada"""
        self.root = tk.Tk()
        self.root.title("🏥 MEDISYNC - SISTEMA DE FACTURACIÓN AVANZADO")
        self.root.geometry("1800x1100")
        self.root.configure(bg='#f8f9fa')
        
        # Configurar estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.Treeview', 
                       background='white',
                       foreground='black',
                       rowheight=25,
                       fieldbackground='white')
        style.configure('Modern.Treeview.Heading',
                       background='#2c3e50',
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        # Header mejorado
        self.create_modern_header()
        
        # Contenido principal con pestañas
        self.create_tabbed_interface()
        
        # Status bar mejorado
        self.create_modern_status_bar()
        
        # Cargar datos
        self.load_initial_data()
        
        return self.root
    
    def create_modern_header(self):
        """Crear header moderno y atractivo"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Container para centrar contenido
        header_container = tk.Frame(header_frame, bg='#2c3e50')
        header_container.pack(expand=True, fill='both')
        
        # Título principal con gradiente visual
        title_frame = tk.Frame(header_container, bg='#2c3e50')
        title_frame.pack(expand=True, fill='both')
        
        title_label = tk.Label(
            title_frame,
            text="🏥 MEDISYNC",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='#3498db'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            title_frame,
            text="💰 Sistema de Facturación Avanzado | PDFs Automáticos | Control de Pagos",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Indicador de estado PDF
        pdf_status = "✅ PDFs Habilitados" if PDF_AVAILABLE else "⚠️ PDFs No Disponibles"
        status_label = tk.Label(
            title_frame,
            text=pdf_status,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#2ecc71' if PDF_AVAILABLE else '#e74c3c'
        )
        status_label.pack()
    
    def create_tabbed_interface(self):
        """Crear interfaz con pestañas modernas"""
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pestaña 1: Facturación Principal
        self.billing_tab = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.billing_tab, text="💰 Facturación")
        
        # Pestaña 2: Configuración
        self.config_tab = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.config_tab, text="⚙️ Configuración")
        
        # Crear contenido de pestañas
        self.create_billing_tab_content()
        self.create_config_tab_content()
    
    def create_billing_tab_content(self):
        """Contenido de la pestaña de facturación"""
        # Panel superior: Citas (más compacto)
        self.create_appointments_panel_modern(self.billing_tab)
        
        # Panel principal: Facturación
        self.create_billing_panel_modern(self.billing_tab)
    
    def create_config_tab_content(self):
        """Contenido de la pestaña de configuración"""
        config_frame = tk.LabelFrame(
            self.config_tab,
            text="🏥 CONFIGURACIÓN DE CLÍNICA",
            font=('Arial', 14, 'bold'),
            bg='#e3f2fd',
            fg='#1565c0',
            padx=20,
            pady=20
        )
        config_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Campos de configuración
        fields = [
            ("Nombre de la Clínica:", 'nombre'),
            ("Dirección:", 'direccion'),
            ("Teléfono:", 'telefono'),
            ("Email:", 'email')
        ]
        
        self.config_vars = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(config_frame, text=label, font=('Arial', 12, 'bold'),
                    bg='#e3f2fd').grid(row=i, column=0, sticky='w', pady=10, padx=(0, 10))
            
            var = tk.StringVar(value=self.clinic_config.get(key, ''))
            entry = tk.Entry(config_frame, textvariable=var, font=('Arial', 11), width=40)
            entry.grid(row=i, column=1, pady=10, padx=(0, 20))
            
            self.config_vars[key] = var
        
        # Botón guardar configuración
        save_btn = tk.Button(
            config_frame,
            text="💾 Guardar Configuración",
            command=self.save_clinic_config,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def create_appointments_panel_modern(self, parent):
        """Panel moderno de citas completadas"""
        appointments_frame = tk.LabelFrame(
            parent,
            text="📅 CITAS COMPLETADAS PENDIENTES DE FACTURACIÓN",
            font=('Arial', 12, 'bold'),
            bg='#e8f4f8',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        appointments_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Controles mejorados
        controls_frame = tk.Frame(appointments_frame, bg='#e8f4f8')
        controls_frame.pack(fill='x', pady=(0, 15))
        
        # Búsqueda
        search_frame = tk.Frame(controls_frame, bg='#e8f4f8')
        search_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(search_frame, text="🔍 Buscar Paciente:", 
                font=('Arial', 10, 'bold'), bg='#e8f4f8').pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 11), width=25)
        search_entry.pack(side='left', padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.search_appointments)
        
        # Botones de acción
        buttons_frame = tk.Frame(controls_frame, bg='#e8f4f8')
        buttons_frame.pack(side='right')
        
        refresh_btn = tk.Button(
            buttons_frame,
            text="🔄 Actualizar",
            command=self.load_appointments,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        )
        refresh_btn.pack(side='left', padx=5)
        
        load_btn = tk.Button(
            buttons_frame,
            text="📋 Cargar para Facturar",
            command=self.load_appointment_for_billing,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        )
        load_btn.pack(side='left', padx=5)
        
        # Tabla de citas moderna
        columns = ('ID', 'Fecha', 'Paciente', 'Doctor', 'Motivo', 'Seguro', 'Descuento')
        self.appointments_tree = ttk.Treeview(appointments_frame, columns=columns, 
                                            show='headings', height=5, style='Modern.Treeview')
        
        # Configurar columnas
        column_configs = {
            'ID': 60, 'Fecha': 100, 'Paciente': 150, 'Doctor': 150, 
            'Motivo': 200, 'Seguro': 120, 'Descuento': 80
        }
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=column_configs.get(col, 100), anchor='center')
        
        # Scrollbar para citas
        scrollbar_appointments = ttk.Scrollbar(appointments_frame, orient="vertical", 
                                             command=self.appointments_tree.yview)
        self.appointments_tree.configure(yscrollcommand=scrollbar_appointments.set)
        
        # Pack tabla
        appointments_table_frame = tk.Frame(appointments_frame, bg='#e8f4f8')
        appointments_table_frame.pack(fill='both', expand=True)
        
        self.appointments_tree.pack(side='left', fill='both', expand=True)
        scrollbar_appointments.pack(side='right', fill='y')
        
        # Eventos
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        self.appointments_tree.bind('<Double-1>', self.load_appointment_for_billing)
    
    def create_billing_panel_modern(self, parent):
        """Panel moderno de facturación con pagos"""
        billing_main_frame = tk.Frame(parent, bg='#f8f9fa')
        billing_main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel izquierdo: Servicios y Factura
        left_panel = tk.Frame(billing_main_frame, bg='#f8f9fa')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Panel derecho: Totales y Pagos
        right_panel = tk.Frame(billing_main_frame, bg='#f8f9fa')
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        
        # Crear secciones
        self.create_services_section(left_panel)
        self.create_invoice_construction_section(left_panel)
        self.create_payment_and_totals_section(right_panel)
    
    def create_services_section(self, parent):
        """Sección de servicios médicos"""
        services_frame = tk.LabelFrame(
            parent,
            text="🏥 SERVICIOS MÉDICOS DISPONIBLES",
            font=('Arial', 11, 'bold'),
            bg='#fff3cd',
            fg='#856404',
            padx=15,
            pady=15
        )
        services_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Instrucciones
        tk.Label(services_frame, 
                text="💡 Doble clic para agregar servicio a la factura",
                font=('Arial', 9, 'italic'),
                bg='#fff3cd',
                fg='#856404').pack(pady=(0, 10))
        
        # Tabla de servicios
        services_columns = ('Código', 'Servicio', 'Categoría', 'Precio')
        self.services_tree = ttk.Treeview(services_frame, columns=services_columns,
                                        show='headings', height=6, style='Modern.Treeview')
        
        # Configurar columnas
        services_widths = {'Código': 80, 'Servicio': 200, 'Categoría': 120, 'Precio': 100}
        
        for col in services_columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=services_widths.get(col, 100), anchor='center')
        
        # Scrollbar
        services_scroll = ttk.Scrollbar(services_frame, orient="vertical",
                                      command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=services_scroll.set)
        
        # Pack tabla
        services_table_frame = tk.Frame(services_frame, bg='#fff3cd')
        services_table_frame.pack(fill='both', expand=True)
        
        self.services_tree.pack(side='left', fill='both', expand=True)
        services_scroll.pack(side='right', fill='y')
        
        self.services_tree.bind('<Double-1>', self.add_service_to_invoice)
    
    def create_invoice_construction_section(self, parent):
        """Sección de construcción de factura"""
        invoice_frame = tk.LabelFrame(
            parent,
            text="� FACTURA EN CONSTRUCCIÓN",
            font=('Arial', 11, 'bold'),
            bg='#d4edda',
            fg='#155724',
            padx=15,
            pady=15
        )
        invoice_frame.pack(fill='both', expand=True)
        
        # Info de cita seleccionada
        self.appointment_info_label = tk.Label(
            invoice_frame,
            text="👆 Seleccione una cita completada para comenzar la facturación",
            font=('Arial', 10),
            bg='#d4edda',
            fg='#155724',
            justify='left',
            anchor='w'
        )
        self.appointment_info_label.pack(fill='x', pady=(0, 15))
        
        # Tabla de servicios en factura
        invoice_columns = ('Servicio', 'Cantidad', 'Precio Unit.', 'Subtotal')
        self.invoice_services_tree = ttk.Treeview(invoice_frame, columns=invoice_columns,
                                                show='headings', height=8, style='Modern.Treeview')
        
        # Configurar columnas
        invoice_widths = {'Servicio': 200, 'Cantidad': 80, 'Precio Unit.': 100, 'Subtotal': 100}
        
        for col in invoice_columns:
            self.invoice_services_tree.heading(col, text=col)
            self.invoice_services_tree.column(col, width=invoice_widths.get(col, 100), anchor='center')
        
        # Scrollbar
        invoice_scroll = ttk.Scrollbar(invoice_frame, orient="vertical",
                                     command=self.invoice_services_tree.yview)
        self.invoice_services_tree.configure(yscrollcommand=invoice_scroll.set)
        
        # Pack tabla
        invoice_table_frame = tk.Frame(invoice_frame, bg='#d4edda')
        invoice_table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.invoice_services_tree.pack(side='left', fill='both', expand=True)
        invoice_scroll.pack(side='right', fill='y')
        
        # Botones de gestión de servicios
        services_buttons_frame = tk.Frame(invoice_frame, bg='#d4edda')
        services_buttons_frame.pack(fill='x', pady=(0, 15))
        
        add_custom_btn = tk.Button(
            services_buttons_frame,
            text="➕ Agregar Personalizado",
            command=self.add_custom_service,
            bg='#17a2b8',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10
        )
        add_custom_btn.pack(side='left', padx=5)
        
        edit_quantity_btn = tk.Button(
            services_buttons_frame,
            text="✏️ Editar Cantidad",
            command=self.edit_service_quantity,
            bg='#ffc107',
            fg='black',
            font=('Arial', 9, 'bold'),
            padx=10
        )
        edit_quantity_btn.pack(side='left', padx=5)
        
        remove_service_btn = tk.Button(
            services_buttons_frame,
            text="🗑️ Quitar Servicio",
            command=self.remove_service_from_invoice,
            bg='#dc3545',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10
        )
        remove_service_btn.pack(side='left', padx=5)
        
        clear_all_btn = tk.Button(
            services_buttons_frame,
            text="🧹 Limpiar Todo",
            command=self.clear_invoice,
            bg='#6c757d',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10
        )
        clear_all_btn.pack(side='right', padx=5)
        
        # Eventos
        self.invoice_services_tree.bind('<Double-1>', self.edit_service_quantity)
        self.invoice_services_tree.bind('<Delete>', self.remove_service_from_invoice)
    
    def create_payment_and_totals_section(self, parent):
        """Sección moderna de totales y pagos"""
        # Panel principal de pagos
        payment_main_frame = tk.Frame(parent, bg='#f8f9fa', width=350)
        payment_main_frame.pack(fill='both', expand=True)
        payment_main_frame.pack_propagate(False)
        
        # Información de la cita
        cita_info_frame = tk.LabelFrame(
            payment_main_frame,
            text="🏥 INFORMACIÓN DE CITA",
            font=('Arial', 11, 'bold'),
            bg='#e3f2fd',
            fg='#1565c0',
            padx=15,
            pady=15
        )
        cita_info_frame.pack(fill='x', pady=(0, 15))
        
        self.detailed_appointment_info = tk.Label(
            cita_info_frame,
            text="Seleccione una cita para ver detalles",
            font=('Arial', 9),
            bg='#e3f2fd',
            fg='#1565c0',
            justify='left',
            anchor='w'
        )
        self.detailed_appointment_info.pack(fill='x')
        
        # Panel de totales
        totals_frame = tk.LabelFrame(
            payment_main_frame,
            text="💰 CÁLCULOS Y TOTALES",
            font=('Arial', 11, 'bold'),
            bg='#f1f8e9',
            fg='#2e7d32',
            padx=15,
            pady=15
        )
        totals_frame.pack(fill='x', pady=(0, 15))
        
        # Variables de totales
        self.subtotal_var = tk.StringVar(value="₡0.00")
        self.discount_var = tk.StringVar(value="₡0.00")
        self.total_var = tk.StringVar(value="₡0.00")
        
        # Crear filas de totales
        totals_data = [
            ("Subtotal:", self.subtotal_var, '#666666'),
            ("Descuento Seguro:", self.discount_var, '#e74c3c'),
            ("TOTAL A PAGAR:", self.total_var, '#27ae60')
        ]
        
        for i, (label, var, color) in enumerate(totals_data):
            row_frame = tk.Frame(totals_frame, bg='#f1f8e9')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=label, 
                    font=('Arial', 11, 'bold' if i == 2 else 'normal'),
                    bg='#f1f8e9', fg='#2e7d32').pack(side='left')
            
            tk.Label(row_frame, textvariable=var, 
                    font=('Arial', 12, 'bold' if i == 2 else 'normal'),
                    bg='#f1f8e9', fg=color).pack(side='right')
        
        # Panel de pago
        payment_frame = tk.LabelFrame(
            payment_main_frame,
            text="💳 INFORMACIÓN DE PAGO",
            font=('Arial', 11, 'bold'),
            bg='#fff3e0',
            fg='#e65100',
            padx=15,
            pady=15
        )
        payment_frame.pack(fill='x', pady=(0, 15))
        
        # Método de pago
        method_frame = tk.Frame(payment_frame, bg='#fff3e0')
        method_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(method_frame, text="Método de Pago:", 
                font=('Arial', 10, 'bold'), bg='#fff3e0').pack(side='left')
        
        self.payment_method_var = tk.StringVar(value="efectivo")
        payment_methods = [("💵 Efectivo", "efectivo"), ("💳 Tarjeta", "tarjeta"), ("🏧 Transferencia", "transferencia")]
        
        methods_frame = tk.Frame(method_frame, bg='#fff3e0')
        methods_frame.pack(side='right')
        
        for text, value in payment_methods:
            tk.Radiobutton(methods_frame, text=text, variable=self.payment_method_var,
                          value=value, bg='#fff3e0', font=('Arial', 9)).pack(side='left', padx=5)
        
        # Monto recibido
        payment_amount_frame = tk.Frame(payment_frame, bg='#fff3e0')
        payment_amount_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(payment_amount_frame, text="Monto Recibido:", 
                font=('Arial', 10, 'bold'), bg='#fff3e0').pack(side='left')
        
        self.payment_var = tk.StringVar(value="0")
        payment_entry = tk.Entry(payment_amount_frame, textvariable=self.payment_var,
                               font=('Arial', 11), width=15, justify='right')
        payment_entry.pack(side='right', padx=(10, 0))
        payment_entry.bind('<KeyRelease>', self.calculate_change)
        
        # Cambio/Faltante
        change_frame = tk.Frame(payment_frame, bg='#fff3e0')
        change_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(change_frame, text="Cambio/Faltante:", 
                font=('Arial', 10, 'bold'), bg='#fff3e0').pack(side='left')
        
        self.change_var = tk.StringVar(value="₡0.00")
        self.change_label = tk.Label(change_frame, textvariable=self.change_var,
                                   font=('Arial', 11, 'bold'), bg='#fff3e0', fg='#27ae60')
        self.change_label.pack(side='right')
        
        # Botón de pago rápido
        quick_payment_frame = tk.Frame(payment_frame, bg='#fff3e0')
        quick_payment_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(quick_payment_frame, text="Pago Exacto:", 
                font=('Arial', 9), bg='#fff3e0').pack(side='left')
        
        exact_payment_btn = tk.Button(
            quick_payment_frame,
            text="� Cantidad Exacta",
            command=self.set_exact_payment,
            bg='#4caf50',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10
        )
        exact_payment_btn.pack(side='right')
        
        # Panel de acciones finales
        actions_frame = tk.LabelFrame(
            payment_main_frame,
            text="🚀 GENERAR FACTURA",
            font=('Arial', 11, 'bold'),
            bg='#e8f5e8',
            fg='#2e7d32',
            padx=15,
            pady=15
        )
        actions_frame.pack(fill='x')
        
        # Botón principal de generar factura
        generate_btn = tk.Button(
            actions_frame,
            text="� GENERAR FACTURA Y PDF",
            command=self.generate_invoice_with_pdf,
            bg='#4caf50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=15
        )
        generate_btn.pack(fill='x', pady=(0, 10))
        
        # Botón de vista previa
        preview_btn = tk.Button(
            actions_frame,
            text="👁️ Vista Previa",
            command=self.preview_invoice,
            bg='#2196f3',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        )
        preview_btn.pack(fill='x')
    
    def save_clinic_config(self):
        """Guardar configuración de clínica"""
        for key, var in self.config_vars.items():
            self.clinic_config[key] = var.get()
        
        messagebox.showinfo("Configuración", "✅ Configuración de clínica guardada exitosamente")
        self.update_status("✅ Configuración actualizada")
    
    def create_modern_status_bar(self):
        """Crear barra de estado moderna"""
        self.status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)
        
        # Status principal
        self.status_label = tk.Label(
            self.status_frame,
            text="✅ Sistema iniciado - Listo para facturar",
            bg='#34495e',
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(side='left', padx=15, pady=5)
        
        # Contador de citas
        self.citas_count_label = tk.Label(
            self.status_frame,
            text="📋 Citas: 0",
            bg='#34495e',
            fg='#3498db',
            font=('Arial', 9)
        )
        self.citas_count_label.pack(side='right', padx=(0, 15), pady=5)
        
        # Indicador PDF
        pdf_text = "📄 PDFs: ✅" if PDF_AVAILABLE else "📄 PDFs: ❌"
        self.pdf_status_label = tk.Label(
            self.status_frame,
            text=pdf_text,
            bg='#34495e',
            fg='#2ecc71' if PDF_AVAILABLE else '#e74c3c',
            font=('Arial', 9)
        )
        self.pdf_status_label.pack(side='right', padx=(0, 15), pady=5)
    
    def search_appointments(self, event=None):
        """Buscar citas por texto"""
        search_text = self.search_var.get().lower()
        
        # Obtener todas las citas nuevamente si no hay filtro
        if not search_text:
            self.load_appointments()
            return
        
        # Filtrar elementos visibles
        for item in self.appointments_tree.get_children():
            values = self.appointments_tree.item(item)['values']
            # Buscar en paciente, doctor y motivo
            if any(search_text in str(val).lower() for val in values[2:5]):
                # Mostrar elemento
                pass
            else:
                # Ocultar elemento (detach)
                self.appointments_tree.detach(item)
    
    def calculate_change(self, event=None):
        """Calcular cambio o faltante en tiempo real"""
        try:
            payment_amount = float(self.payment_var.get().replace(',', ''))
            total_amount = float(self.total_var.get().replace('₡', '').replace(',', ''))
            
            change = payment_amount - total_amount
            
            if change > 0:
                self.change_var.set(f"₡{change:,.2f}")
                self.change_label.config(fg='#27ae60')  # Verde para cambio
            elif change < 0:
                self.change_var.set(f"-₡{abs(change):,.2f}")
                self.change_label.config(fg='#e74c3c')  # Rojo para faltante
            else:
                self.change_var.set("₡0.00")
                self.change_label.config(fg='#666666')  # Gris para exacto
                
        except ValueError:
            self.change_var.set("₡0.00")
            self.change_label.config(fg='#666666')
    
    def set_exact_payment(self):
        """Establecer pago exacto"""
        total_str = self.total_var.get().replace('₡', '').replace(',', '')
        try:
            total = float(total_str)
            self.payment_var.set(f"{total:.2f}")
            self.calculate_change()
        except ValueError:
            pass
    
    def add_custom_service(self):
        """Agregar servicio personalizado"""
        if not self.current_appointment:
            messagebox.showwarning("Advertencia", "Seleccione una cita primero")
            return
        
        # Ventana de servicio personalizado
        window = tk.Toplevel(self.root)
        window.title("Agregar Servicio Personalizado")
        window.geometry("450x350")
        window.configure(bg='#f8f9fa')
        window.transient(self.root)
        window.grab_set()
        
        # Header
        header_frame = tk.Frame(window, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="➕ Agregar Servicio Personalizado",
                font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(pady=15)
        
        # Formulario
        form_frame = tk.Frame(window, bg='#f8f9fa')
        form_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Campos
        fields = [
            ("Nombre del servicio:", "nombre"),
            ("Descripción:", "descripcion"),
            ("Precio (₡):", "precio"),
            ("Cantidad:", "cantidad")
        ]
        
        vars_dict = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11, 'bold'),
                    bg='#f8f9fa').grid(row=i, column=0, sticky='w', pady=10, padx=(0, 15))
            
            if key == "descripcion":
                var = tk.StringVar()
                widget = tk.Text(form_frame, height=3, width=25, font=('Arial', 10))
                widget.grid(row=i, column=1, pady=10, sticky='ew')
                vars_dict[key] = widget
            else:
                var = tk.StringVar()
                if key == "cantidad":
                    var.set("1")
                widget = tk.Entry(form_frame, textvariable=var, font=('Arial', 11), width=25)
                widget.grid(row=i, column=1, pady=10, sticky='ew')
                vars_dict[key] = var
        
        # Botones
        buttons_frame = tk.Frame(window, bg='#f8f9fa')
        buttons_frame.pack(pady=20)
        
        def save_custom_service():
            try:
                nombre = vars_dict["nombre"].get().strip()
                descripcion = vars_dict["descripcion"].get("1.0", tk.END).strip()
                precio = float(vars_dict["precio"].get().replace(',', ''))
                cantidad = int(vars_dict["cantidad"].get())
                
                if not nombre or precio < 0 or cantidad < 1:
                    messagebox.showerror("Error", "Complete todos los campos correctamente")
                    return
                
                service = {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'precio': precio,
                    'cantidad': cantidad,
                    'categoria': 'Personalizado'
                }
                
                self.selected_services.append(service)
                self.update_invoice_display()
                window.destroy()
                
                messagebox.showinfo("Éxito", f"✅ Servicio '{nombre}' agregado exitosamente")
                
            except ValueError:
                messagebox.showerror("Error", "Precio y cantidad deben ser números válidos")
        
        tk.Button(buttons_frame, text="💾 Agregar Servicio", command=save_custom_service,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='left', padx=10)
        tk.Button(buttons_frame, text="❌ Cancelar", command=window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='left', padx=10)
    
    def edit_service_quantity(self, event=None):
        """Editar cantidad de servicio"""
        selection = self.invoice_services_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Seleccione un servicio para editar")
            return
        
        item = self.invoice_services_tree.item(selection[0])
        service_name = item['values'][0]
        current_quantity = item['values'][1]
        
        # Buscar servicio
        service_index = None
        for i, service in enumerate(self.selected_services):
            if service['nombre'] == service_name:
                service_index = i
                break
        
        if service_index is None:
            return
        
        # Solicitar nueva cantidad
        new_quantity = simpledialog.askinteger(
            "Editar Cantidad",
            f"Nueva cantidad para '{service_name}':",
            initialvalue=current_quantity,
            minvalue=1,
            maxvalue=50
        )
        
        if new_quantity:
            self.selected_services[service_index]['cantidad'] = new_quantity
            self.update_invoice_display()
            self.update_status(f"✏️ Cantidad actualizada: {service_name}")
    
    def remove_service_from_invoice(self, event=None):
        """Quitar servicio de la factura"""
        selection = self.invoice_services_tree.selection()
        if not selection:
            if event:  # Viene del evento Delete
                messagebox.showinfo("Info", "Seleccione un servicio para quitar")
            return
        
        item = self.invoice_services_tree.item(selection[0])
        service_name = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{service_name}' de la factura?"):
            for i, service in enumerate(self.selected_services):
                if service['nombre'] == service_name:
                    del self.selected_services[i]
                    break
            
            self.update_invoice_display()
            self.update_status(f"🗑️ Servicio removido: {service_name}")
    
    def generate_invoice_with_pdf(self):
        """Generar factura con PDF automático"""
        if not self.current_appointment:
            messagebox.showwarning("Advertencia", "Seleccione una cita primero")
            return
        
        if not self.selected_services:
            messagebox.showwarning("Advertencia", "Agregue servicios a la factura")
            return
        
        # Obtener información de pago
        try:
            monto_pagado = float(self.payment_var.get().replace(',', ''))
        except ValueError:
            monto_pagado = 0
        
        metodo_pago = self.payment_method_var.get()
        
        # Confirmar generación
        total_amount = float(self.total_var.get().replace('₡', '').replace(',', ''))
        
        confirm_text = f"""¿Generar factura para {self.current_appointment.get('paciente_nombre')}?

💰 RESUMEN DE FACTURACIÓN:
• Total a pagar: {self.total_var.get()}
• Servicios: {len(self.selected_services)}
• Monto recibido: ₡{monto_pagado:,.2f}
• Método de pago: {metodo_pago.title()}
• Cambio/Faltante: {self.change_var.get()}

✅ Se generará automáticamente el PDF de la factura"""
        
        if not messagebox.askyesno("Confirmar Facturación", confirm_text):
            return
        
        try:
            self.update_status("💾 Generando factura y PDF...")
            
            # Crear factura en base de datos
            success, message, invoice_data = self.db_manager.create_invoice_from_appointment(
                self.current_appointment['id'],
                self.selected_services,
                f"Pago {metodo_pago}. Monto recibido: ₡{monto_pagado:,.2f}",
                monto_pagado,
                metodo_pago
            )
            
            if success:
                # Generar PDF si está disponible
                pdf_generated = False
                pdf_path = ""
                
                if self.pdf_generator and invoice_data:
                    try:
                        # Crear nombre de archivo
                        patient_name = self.current_appointment.get('paciente_nombre', 'Paciente')
                        safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"Factura_{invoice_data['numero_factura']}_{safe_name}_{timestamp}.pdf"
                        pdf_path = os.path.join(self.pdf_generator.pdf_directory, filename)
                        
                        # Generar PDF
                        pdf_generated = self.pdf_generator.generate_invoice_pdf(
                            invoice_data=invoice_data,
                            clinic_config=self.clinic_config,
                            output_path=pdf_path
                        )
                        
                    except Exception as e:
                        print(f"Error generando PDF: {e}")
                
                # Mostrar resultado
                result_text = f"✅ {message}"
                if pdf_generated:
                    result_text += f"\n📄 PDF generado: {os.path.basename(pdf_path)}"
                    
                    # Preguntar si abrir PDF
                    if messagebox.askyesno("PDF Generado", 
                                         f"{result_text}\n\n¿Desea abrir el PDF generado?"):
                        try:
                            os.startfile(pdf_path)  # Windows
                        except:
                            try:
                                subprocess.call(['open', pdf_path])  # macOS
                            except:
                                try:
                                    subprocess.call(['xdg-open', pdf_path])  # Linux
                                except:
                                    messagebox.showinfo("PDF", f"PDF guardado en: {pdf_path}")
                else:
                    if PDF_AVAILABLE:
                        result_text += "\n⚠️ No se pudo generar PDF"
                    else:
                        result_text += "\n⚠️ PDF no disponible (dependencias faltantes)"
                
                messagebox.showinfo("¡Facturación Exitosa!", result_text)
                
                # Limpiar y recargar
                self.clear_invoice()
                self.load_appointments()
                self.update_status("✅ Factura generada exitosamente")
                
            else:
                messagebox.showerror("Error", f"❌ {message}")
                self.update_status("❌ Error generando factura")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.update_status(f"❌ Error: {str(e)}")
    
    def preview_invoice(self):
        """Vista previa de la factura"""
        if not self.current_appointment or not self.selected_services:
            messagebox.showwarning("Advertencia", "Seleccione una cita y agregue servicios primero")
            return
        
        # Crear ventana de vista previa
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Vista Previa de Factura")
        preview_window.geometry("700x800")
        preview_window.configure(bg='white')
        preview_window.transient(self.root)
        
        # Frame scrollable
        canvas = tk.Canvas(preview_window, bg='white')
        scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido de la vista previa
        self.create_preview_content(scrollable_frame)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_preview_content(self, parent):
        """Crear contenido de vista previa"""
        # Header de clínica
        tk.Label(parent, text=f"🏥 {self.clinic_config['nombre']}", 
                font=('Arial', 18, 'bold'), bg='white', fg='#2c3e50').pack(pady=10)
        
        tk.Label(parent, text=f"📍 {self.clinic_config['direccion']}", 
                font=('Arial', 11), bg='white').pack()
        tk.Label(parent, text=f"📞 {self.clinic_config['telefono']} | ✉️ {self.clinic_config['email']}", 
                font=('Arial', 11), bg='white').pack(pady=(0, 20))
        
        # Título factura
        tk.Label(parent, text="FACTURA MÉDICA", 
                font=('Arial', 16, 'bold'), bg='white', fg='#e74c3c').pack(pady=10)
        
        # Información del paciente
        info_frame = tk.Frame(parent, bg='white', relief='ridge', bd=1)
        info_frame.pack(fill='x', padx=30, pady=20)
        
        info_data = [
            f"👤 Paciente: {self.current_appointment.get('paciente_nombre')}",
            f"👨‍⚕️ Doctor: {self.current_appointment.get('doctor_nombre')}",
            f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"🛡️ Seguro: {self.current_appointment.get('seguro_nombre', 'Sin seguro')}",
            f"💳 Método de Pago: {self.payment_method_var.get().title()}"
        ]
        
        for info in info_data:
            tk.Label(info_frame, text=info, font=('Arial', 11), 
                    bg='white', anchor='w').pack(anchor='w', padx=15, pady=3)
        
        # Servicios
        tk.Label(parent, text="SERVICIOS PRESTADOS", 
                font=('Arial', 14, 'bold'), bg='white', fg='#2c3e50').pack(pady=(30, 15))
        
        services_frame = tk.Frame(parent, bg='white')
        services_frame.pack(fill='x', padx=30)
        
        for service in self.selected_services:
            service_item = tk.Frame(services_frame, bg='#f8f9fa', relief='flat', bd=1)
            service_item.pack(fill='x', pady=3)
            
            total_service = service['precio'] * service['cantidad']
            
            tk.Label(service_item, 
                    text=f"• {service['nombre']} | Cantidad: {service['cantidad']} × ₡{service['precio']:,.2f} = ₡{total_service:,.2f}",
                    font=('Arial', 10), bg='#f8f9fa', anchor='w').pack(anchor='w', padx=15, pady=8)
        
        # Totales
        totals_frame = tk.Frame(parent, bg='white', relief='ridge', bd=2)
        totals_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(totals_frame, text="RESUMEN DE TOTALES", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(pady=10)
        
        totals_info = [
            f"Subtotal: {self.subtotal_var.get()}",
            f"Descuento: {self.discount_var.get()}",
            f"TOTAL A PAGAR: {self.total_var.get()}"
        ]
        
        # Información de pago
        try:
            monto_pagado = float(self.payment_var.get())
            if monto_pagado > 0:
                totals_info.append(f"Monto Recibido: ₡{monto_pagado:,.2f}")
                totals_info.append(f"Cambio/Faltante: {self.change_var.get()}")
        except:
            pass
        
        for total_info in totals_info:
            font_weight = 'bold' if 'TOTAL' in total_info else 'normal'
            color = '#27ae60' if 'TOTAL' in total_info else '#666666'
            
            tk.Label(totals_frame, text=total_info, 
                    font=('Arial', 11, font_weight), bg='white', fg=color).pack(anchor='e', padx=15, pady=2)
        
        # Footer
        tk.Label(parent, text="Gracias por confiar en nuestros servicios médicos", 
                font=('Arial', 10, 'italic'), bg='white', fg='#666666').pack(pady=30)
    
    def update_status(self, message):
        """Actualizar estado"""
        self.status_label.config(text=message)
    
    def load_initial_data(self):
        """Cargar datos iniciales"""
        self.load_appointments()
        self.load_services()
    
    def load_appointments(self):
        """Cargar citas completadas"""
        try:
            # Limpiar tabla
            for item in self.appointments_tree.get_children():
                self.appointments_tree.delete(item)
            
            appointments = self.db_manager.get_completed_appointments()
            
            for apt in appointments:
                # Formatear fecha
                try:
                    dt = datetime.fromisoformat(apt['fecha_hora'])
                    fecha = dt.strftime('%d/%m/%Y')
                except:
                    fecha = apt['fecha_hora'][:10] if apt['fecha_hora'] else 'N/A'
                
                # Formatear descuento
                descuento = f"{apt.get('porcentaje_descuento', 0):.0f}%" if apt.get('porcentaje_descuento') else '0%'
                
                self.appointments_tree.insert('', 'end', values=(
                    apt['cita_id'],
                    fecha,
                    apt.get('paciente_nombre', 'N/A'),
                    apt.get('doctor_nombre', 'N/A'),
                    apt.get('motivo', 'Sin motivo')[:25] + '...' if len(apt.get('motivo', '')) > 25 else apt.get('motivo', 'Sin motivo'),
                    apt.get('seguro_nombre', 'Sin seguro')[:15],
                    descuento
                ))
            
            self.update_status(f"✅ {len(appointments)} citas cargadas")
            self.citas_count_label.config(text=f"📋 Citas: {len(appointments)}")
            
        except Exception as e:
            self.update_status(f"❌ Error cargando citas: {str(e)}")
    
    def load_services(self):
        """Cargar servicios médicos"""
        try:
            # Limpiar tabla
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)
            
            services = self.db_manager.get_medical_services()
            
            for service in services:
                self.services_tree.insert('', 'end', values=(
                    service['codigo'],
                    service['nombre'],
                    service['categoria'],
                    f"₡{service['precio']:,.2f}"
                ))
            
            print(f"✅ {len(services)} servicios cargados")
            
        except Exception as e:
            print(f"❌ Error cargando servicios: {e}")
    
    def on_appointment_select(self, event=None):
        """Manejar selección de cita"""
        selection = self.appointments_tree.selection()
        if not selection:
            return
        
        item = self.appointments_tree.item(selection[0])
        cita_id = item['values'][0]
        
        appointment = self.db_manager.get_appointment_details(cita_id)
        if appointment:
            self.current_appointment = appointment
            self.update_appointment_info()
            self.update_detailed_appointment_info()
    
    def update_appointment_info(self):
        """Actualizar info básica de cita"""
        if not self.current_appointment:
            return
        
        info_text = f"""🏥 CITA SELECCIONADA:
👤 Paciente: {self.current_appointment.get('paciente_nombre')}
👨‍⚕️ Doctor: {self.current_appointment.get('doctor_nombre')}
📅 Fecha: {self.current_appointment.get('fecha_hora', '')[:16]}
💭 Motivo: {self.current_appointment.get('motivo', 'Sin motivo')}
🛡️ Seguro: {self.current_appointment.get('seguro_nombre', 'Sin seguro')}"""
        
        self.appointment_info_label.config(text=info_text)
    
    def update_detailed_appointment_info(self):
        """Actualizar info detallada en panel de pagos"""
        if not self.current_appointment:
            return
        
        # Formatear fecha
        try:
            dt = datetime.fromisoformat(self.current_appointment.get('fecha_hora', ''))
            fecha_formateada = dt.strftime('%d/%m/%Y %H:%M')
        except:
            fecha_formateada = self.current_appointment.get('fecha_hora', 'N/A')[:16]
        
        detailed_text = f"""ID: {self.current_appointment.get('id')}
Paciente: {self.current_appointment.get('paciente_nombre')}
Teléfono: {self.current_appointment.get('paciente_telefono', 'N/A')}
Doctor: {self.current_appointment.get('doctor_nombre')}
Especialidad: {self.current_appointment.get('especialidad', 'General')}
Fecha/Hora: {fecha_formateada}
Seguro: {self.current_appointment.get('seguro_nombre', 'Sin seguro')}
Descuento: {self.current_appointment.get('porcentaje_descuento', 0):.0f}%"""
        
        self.detailed_appointment_info.config(text=detailed_text)
    
    def load_appointment_for_billing(self, event=None):
        """Cargar cita para facturación"""
        if not self.current_appointment:
            messagebox.showwarning("Advertencia", "Seleccione una cita primero")
            return
        
        response = messagebox.askyesno(
            "Cargar Cita para Facturación",
            f"¿Cargar la cita de {self.current_appointment.get('paciente_nombre')} para facturación?\n\n"
            f"👨‍⚕️ Doctor: {self.current_appointment.get('doctor_nombre')}\n"
            f"📅 Fecha: {self.current_appointment.get('fecha_hora', '')[:16]}\n"
            f"💭 Motivo: {self.current_appointment.get('motivo', 'Sin motivo')}\n\n"
            f"Esto limpiará la factura actual si existe."
        )
        
        if response:
            self.clear_invoice()
            self.add_consultation_service()
            self.update_status(f"✅ Cita cargada: {self.current_appointment.get('paciente_nombre')}")
    
    def add_consultation_service(self):
        """Agregar servicio de consulta automáticamente"""
        if not self.current_appointment:
            return
        
        especialidad = self.current_appointment.get('especialidad', '').lower()
        
        if 'general' in especialidad or not especialidad:
            service = {
                'nombre': 'Consulta General',
                'precio': 1500.00,
                'cantidad': 1,
                'categoria': 'Consulta'
            }
        else:
            service = {
                'nombre': 'Consulta Especializada',
                'precio': 2500.00,
                'cantidad': 1,
                'categoria': 'Consulta'
            }
        
        self.selected_services.append(service)
        self.update_invoice_display()
        self.update_status(f"✅ Servicio de consulta agregado automáticamente")
    
    def add_service_to_invoice(self, event=None):
        """Agregar servicio a factura"""
        if not self.current_appointment:
            messagebox.showwarning("Advertencia", "Seleccione una cita primero")
            return
        
        selection = self.services_tree.selection()
        if not selection:
            return
        
        item = self.services_tree.item(selection[0])
        values = item['values']
        
        service = {
            'nombre': values[1],
            'categoria': values[2],
            'precio': float(values[3].replace('₡', '').replace(',', '')),
            'cantidad': 1
        }
        
        # Verificar si ya existe
        for existing in self.selected_services:
            if existing['nombre'] == service['nombre']:
                existing['cantidad'] += 1
                self.update_invoice_display()
                self.update_status(f"✅ Cantidad incrementada: {service['nombre']}")
                return
        
        self.selected_services.append(service)
        self.update_invoice_display()
        self.update_status(f"✅ Servicio agregado: {service['nombre']}")
    
    def update_invoice_display(self):
        """Actualizar visualización de factura"""
        # Limpiar tabla
        for item in self.invoice_services_tree.get_children():
            self.invoice_services_tree.delete(item)
        
        # Agregar servicios
        subtotal = 0
        for service in self.selected_services:
            service_total = service['precio'] * service['cantidad']
            subtotal += service_total
            
            self.invoice_services_tree.insert('', 'end', values=(
                service['nombre'],
                service['cantidad'],
                f"₡{service['precio']:,.2f}",
                f"₡{service_total:,.2f}"
            ))
        
        # Calcular descuento si hay seguro
        discount_percent = 0
        discount_amount = 0
        if self.current_appointment:
            discount_percent = float(self.current_appointment.get('porcentaje_descuento', 0))
            discount_amount = subtotal * (discount_percent / 100)
        
        # Total final
        total = subtotal - discount_amount
        
        # Actualizar variables
        self.subtotal_var.set(f"₡{subtotal:,.2f}")
        self.discount_var.set(f"₡{discount_amount:,.2f} ({discount_percent:.0f}%)")
        self.total_var.set(f"₡{total:,.2f}")
        
        # Recalcular cambio
        self.calculate_change()
    
    def clear_invoice(self):
        """Limpiar factura"""
        self.selected_services.clear()
        
        for item in self.invoice_services_tree.get_children():
            self.invoice_services_tree.delete(item)
        
        self.subtotal_var.set("₡0.00")
        self.discount_var.set("₡0.00")
        self.total_var.set("₡0.00")
        self.payment_var.set("0")
        self.change_var.set("₡0.00")
        
        self.update_status("🧹 Factura limpiada")
    
    def run(self):
        """Ejecutar sistema"""
        root = self.create_interface()
        root.mainloop()


def main():
    """Función principal"""
    print("🚀 INICIANDO SISTEMA DE FACTURACIÓN DEFINITIVO...")
    print("="*50)
    print("🎯 Integración completa de Fases 1-5")
    print("📋 Funcionalidades:")
    print("   • Facturación desde citas")
    print("   • Gestión de servicios")
    print("   • Base de datos integrada")
    print("   • Interfaz moderna")
    print("="*50)
    
    try:
        system = BillingSystemComplete()
        system.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Presione Enter...")


if __name__ == "__main__":
    main()
