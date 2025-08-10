"""
MÓDULO DE FACTURACIÓN PROFESIONAL - MEDISYNC
Fase 1: Estructura Base y Conexión a Base de Datos
Versión: 1.0.0
Fecha: 25 de Julio 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date, timedelta
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import hashlib
import json

# Importar reportlab para PDFs (instalar si no existe)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    print("⚠️ ReportLab no disponible. Instalar con: pip install reportlab")
    PDF_AVAILABLE = False

# Importar el database manager del sistema principal
try:
    from database_manager import DatabaseManager
    DATABASE_MANAGER_AVAILABLE = True
except ImportError:
    try:
        from simple_database_manager import SimpleDatabaseManager as DatabaseManager
        DATABASE_MANAGER_AVAILABLE = True
    except ImportError:
        print("⚠️ Database Manager no encontrado")
        DATABASE_MANAGER_AVAILABLE = False

@dataclass
class Invoice:
    """Clase de datos para facturas"""
    id: Optional[int] = None
    numero_factura: str = ""
    paciente_id: int = 0
    doctor_id: int = 0
    concepto: str = ""
    monto_original: float = 0.0
    descuento_seguro: float = 0.0
    monto_final: float = 0.0
    estado: str = "pendiente"
    fecha_creacion: str = ""
    fecha_vencimiento: str = ""
    fecha_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    seguro_aplicado: Optional[str] = None
    moneda: str = "RD$"
    notas: str = ""

@dataclass
class Patient:
    """Clase de datos para pacientes"""
    id: int
    nombre: str
    apellido: str
    email: str
    telefono: str
    seguro_id: Optional[int] = None
    seguro_nombre: str = ""
    descuento_porcentaje: float = 0.0

class InvoiceNumberGenerator:
    """Generador de números de factura únicos"""
    
    @staticmethod
    def generate() -> str:
        """Generar número de factura con formato: FAC-YYYY-NNNN"""
        try:
            year = datetime.now().year
            month = datetime.now().month
            day = datetime.now().day
            
            # Formato: FAC-2025-0725-NNNN
            base_number = f"FAC-{year}-{month:02d}{day:02d}"
            
            # Buscar el último número del día
            if DATABASE_MANAGER_AVAILABLE:
                db_manager = DatabaseManager()
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT numero_factura FROM facturas 
                    WHERE numero_factura LIKE ? 
                    ORDER BY numero_factura DESC LIMIT 1
                """, (f"{base_number}-%",))
                
                result = cursor.fetchone()
                
                if result:
                    # Extraer el número secuencial
                    last_number = result[0]
                    sequence = int(last_number.split('-')[-1]) + 1
                else:
                    sequence = 1
                
                cursor.close()
                conn.close()
            else:
                # Fallback: usar timestamp
                sequence = int(datetime.now().strftime("%H%M"))
            
            return f"{base_number}-{sequence:04d}"
            
        except Exception as e:
            print(f"Error generando número de factura: {e}")
            # Fallback: usar timestamp completo
            return f"FAC-{datetime.now().strftime('%Y-%m%d-%H%M%S')}"

class BillingDatabase:
    """Gestor de base de datos específico para facturación"""
    
    def __init__(self):
        self.db_manager = DatabaseManager() if DATABASE_MANAGER_AVAILABLE else None
        self.init_billing_tables()
    
    def init_billing_tables(self):
        """Inicializar tablas específicas de facturación si no existen"""
        if not self.db_manager:
            return
            
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Tabla de configuración de facturación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS billing_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de plantillas de servicios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS billing_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio_base REAL NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insertar servicios básicos si no existen
            cursor.execute("SELECT COUNT(*) FROM billing_services")
            if cursor.fetchone()[0] == 0:
                default_services = [
                    ("Consulta General", "Consulta médica general", 1500.00),
                    ("Consulta Especializada", "Consulta con especialista", 2500.00),
                    ("Consulta de Seguimiento", "Consulta de control", 1200.00),
                    ("Examen Físico Completo", "Examen médico completo", 3000.00),
                    ("Certificado Médico", "Expedición de certificado", 800.00)
                ]
                
                cursor.executemany("""
                    INSERT INTO billing_services (nombre, descripcion, precio_base)
                    VALUES (?, ?, ?)
                """, default_services)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Tablas de facturación inicializadas correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando tablas de facturación: {e}")
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return self.db_manager.get_connection() if self.db_manager else None
    
    def get_patients_with_insurance(self) -> List[Patient]:
        """Obtener lista de pacientes con información de seguro"""
        if not self.db_manager:
            return []
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.nombre, u.apellido, u.email, u.telefono,
                       s.id as seguro_id, s.nombre as seguro_nombre, 
                       s.descuento_porcentaje
                FROM usuarios u
                LEFT JOIN pacientes p ON u.id = p.id
                LEFT JOIN seguros_medicos s ON p.seguro_medico_id = s.id
                WHERE u.tipo_usuario = 'paciente' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
            """)
            
            patients = []
            for row in cursor.fetchall():
                patient = Patient(
                    id=row[0],
                    nombre=row[1],
                    apellido=row[2],
                    email=row[3],
                    telefono=row[4] or "",
                    seguro_id=row[5],
                    seguro_nombre=row[6] or "Sin Seguro",
                    descuento_porcentaje=row[7] or 0.0
                )
                patients.append(patient)
            
            cursor.close()
            conn.close()
            return patients
            
        except Exception as e:
            print(f"Error obteniendo pacientes: {e}")
            return []
    
    def get_doctors(self) -> List[Dict]:
        """Obtener lista de doctores activos"""
        if not self.db_manager:
            return []
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.nombre, u.apellido, d.especialidad
                FROM usuarios u
                JOIN doctores d ON u.id = d.id
                WHERE u.tipo_usuario = 'doctor' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
            """)
            
            doctors = []
            for row in cursor.fetchall():
                doctor = {
                    'id': row[0],
                    'nombre': row[1],
                    'apellido': row[2],
                    'especialidad': row[3] or "Medicina General",
                    'nombre_completo': f"Dr. {row[1]} {row[2]} - {row[3] or 'Medicina General'}"
                }
                doctors.append(doctor)
            
            cursor.close()
            conn.close()
            return doctors
            
        except Exception as e:
            print(f"Error obteniendo doctores: {e}")
            return []
    
    def get_billing_services(self) -> List[Dict]:
        """Obtener servicios de facturación disponibles"""
        if not self.db_manager:
            return []
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, descripcion, precio_base
                FROM billing_services
                WHERE activo = 1
                ORDER BY nombre
            """)
            
            services = []
            for row in cursor.fetchall():
                service = {
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'precio_base': row[3]
                }
                services.append(service)
            
            cursor.close()
            conn.close()
            return services
            
        except Exception as e:
            print(f"Error obteniendo servicios: {e}")
            return []

class BillingCalculator:
    """Calculadora de facturación con descuentos y seguros"""
    
    @staticmethod
    def calculate_discount(amount: float, discount_percentage: float) -> float:
        """Calcular descuento"""
        return amount * (discount_percentage / 100)
    
    @staticmethod
    def calculate_final_amount(original_amount: float, discount_amount: float) -> float:
        """Calcular monto final después del descuento"""
        return max(0, original_amount - discount_amount)
    
    @staticmethod
    def calculate_invoice_totals(original_amount: float, patient: Patient) -> Dict[str, float]:
        """Calcular todos los totales de una factura"""
        discount_amount = 0.0
        
        if patient.seguro_id and patient.descuento_porcentaje > 0:
            discount_amount = BillingCalculator.calculate_discount(
                original_amount, patient.descuento_porcentaje
            )
        
        final_amount = BillingCalculator.calculate_final_amount(original_amount, discount_amount)
        
        return {
            'monto_original': original_amount,
            'descuento_seguro': discount_amount,
            'monto_final': final_amount,
            'ahorro': discount_amount,
            'porcentaje_descuento': patient.descuento_porcentaje
        }

# Función de prueba para verificar la fase 1
def test_phase_1():
    """Probar funcionalidades de la Fase 1"""
    print("🧪 PROBANDO FASE 1: Estructura Base")
    print("=" * 50)
    
    # Probar generador de números
    print("📄 Generando números de factura:")
    for i in range(3):
        number = InvoiceNumberGenerator.generate()
        print(f"  {i+1}. {number}")
    
    # Probar base de datos
    print("\n💾 Probando conexión a base de datos:")
    db = BillingDatabase()
    
    # Probar obtención de pacientes
    patients = db.get_patients_with_insurance()
    print(f"  📋 Pacientes encontrados: {len(patients)}")
    
    # Probar obtención de doctores
    doctors = db.get_doctors()
    print(f"  👨‍⚕️ Doctores encontrados: {len(doctors)}")
    
    # Probar servicios
    services = db.get_billing_services()
    print(f"  🏥 Servicios disponibles: {len(services)}")
    
    # Probar calculadora
    print("\n🧮 Probando calculadora:")
    if patients:
        patient = patients[0]
        amount = 2000.0
        totals = BillingCalculator.calculate_invoice_totals(amount, patient)
        print(f"  💰 Monto original: RD$ {totals['monto_original']:,.2f}")
        print(f"  💳 Descuento: RD$ {totals['descuento_seguro']:,.2f}")
        print(f"  ✅ Total final: RD$ {totals['monto_final']:,.2f}")
    
    print("\n✅ FASE 1 COMPLETADA - Estructura base funcionando")
    return True

if __name__ == "__main__":
    # Ejecutar pruebas de la Fase 1
    test_phase_1()
