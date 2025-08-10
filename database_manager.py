"""
Database Manager para MEDISYNC
Gestor completo de base de datos con todas las funcionalidades
"""
import sqlite3
import hashlib
import os
import threading
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json

@dataclass
class User:
    id: int
    nombre: str
    apellido: str
    email: str
    telefono: str
    tipo_usuario: str
    activo: bool = True
    especialidad: str = None
    cedula_profesional: str = None
    numero_expediente: str = None
    tipo_sangre: str = None

@dataclass
class Cita:
    id: int
    paciente_id: int
    doctor_id: int
    fecha_hora: datetime
    motivo: str
    estado: str
    notas: str = ""
    duracion_minutos: int = 30

@dataclass
class HistorialMedico:
    id: int
    paciente_id: int
    doctor_id: int
    fecha_consulta: date
    diagnostico: str
    tratamiento: str = ""
    medicamentos: str = ""
    observaciones: str = ""
    estado: str = "activo"

@dataclass
class Factura:
    id: int
    paciente_id: int
    numero_factura: str
    concepto: str
    monto: float
    estado: str
    fecha_creacion: date
    fecha_vencimiento: date
    fecha_pago: datetime = None
    metodo_pago: str = None

class DatabaseManager:
    """Gestor completo de base de datos para MEDISYNC"""
    
    def __init__(self, db_path='database/medisync.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.ensure_database_exists()
        self.create_tables()
        self.create_default_users()
    
    def ensure_database_exists(self):
        """Asegurar que la base de datos y el directorio existan"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Obtener conexión a la base de datos con row_factory"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_simple_connection(self):
        """Obtener conexión simple sin row_factory"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def create_tables(self):
        """Crear todas las tablas necesarias"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Tabla usuarios
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    telefono TEXT,
                    direccion TEXT,
                    fecha_nacimiento DATE,
                    tipo_usuario TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Tabla pacientes
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY,
                    numero_expediente TEXT UNIQUE,
                    tipo_sangre TEXT,
                    alergias TEXT,
                    contacto_emergencia TEXT,
                    telefono_emergencia TEXT,
                    seguro_medico TEXT,
                    seguro_medico_id INTEGER DEFAULT 4,
                    tiene_seguro BOOLEAN DEFAULT 0,
                    FOREIGN KEY (id) REFERENCES usuarios(id)
                )
                ''')
                
                # Tabla doctores
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctores (
                    id INTEGER PRIMARY KEY,
                    especialidad TEXT,
                    cedula_profesional TEXT UNIQUE,
                    acepta_seguros BOOLEAN DEFAULT 1,
                    tarifa_consulta DECIMAL(10,2) DEFAULT 500.00,
                    horario_inicio TIME DEFAULT '08:00',
                    horario_fin TIME DEFAULT '17:00',
                    FOREIGN KEY (id) REFERENCES usuarios(id)
                )
                ''')
                
                # Tabla citas (estructura existente)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS citas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    fecha_hora TIMESTAMP,
                    motivo TEXT,
                    estado VARCHAR(20) DEFAULT 'programada',
                    notas TEXT,
                    duracion_minutos INTEGER DEFAULT 30,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tarifa_consulta REAL,
                    seguro_aplicable BOOLEAN DEFAULT 0,
                    FOREIGN KEY (paciente_id) REFERENCES usuarios(id),
                    FOREIGN KEY (doctor_id) REFERENCES usuarios(id)
                )
                ''')
                
                # Tabla historiales médicos
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS historiales_medicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    fecha_consulta DATE NOT NULL,
                    diagnostico TEXT NOT NULL,
                    tratamiento TEXT,
                    medicamentos TEXT,
                    observaciones TEXT,
                    estado TEXT DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paciente_id) REFERENCES usuarios(id),
                    FOREIGN KEY (doctor_id) REFERENCES usuarios(id)
                )
                ''')
                
                # Tabla facturas
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE NOT NULL,
                    paciente_id INTEGER NOT NULL,
                    doctor_id INTEGER,
                    concepto TEXT NOT NULL,
                    monto DECIMAL(10,2) NOT NULL,
                    estado TEXT DEFAULT 'pendiente',
                    fecha_creacion DATE NOT NULL,
                    fecha_vencimiento DATE NOT NULL,
                    fecha_pago DATETIME,
                    metodo_pago TEXT,
                    FOREIGN KEY (paciente_id) REFERENCES usuarios(id),
                    FOREIGN KEY (doctor_id) REFERENCES usuarios(id)
                )
                ''')
                
                # Tabla seguros médicos
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS seguros_medicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descuento_porcentaje DECIMAL(5,2) DEFAULT 0,
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT 1
                )
                ''')
                
                # Tabla historial_medico (nueva estructura mejorada)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_medico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    fecha_consulta DATE NOT NULL,
                    tipo_consulta TEXT DEFAULT 'Consulta General',
                    motivo_consulta TEXT,
                    sintomas TEXT,
                    diagnostico TEXT,
                    tratamiento TEXT,
                    medicamentos TEXT,
                    observaciones TEXT,
                    proxima_cita DATE,
                    estado TEXT DEFAULT 'Completada',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paciente_id) REFERENCES usuarios(id),
                    FOREIGN KEY (doctor_id) REFERENCES usuarios(id)
                )
                ''')
                
                # Insertar seguros por defecto
                cursor.execute('''
                INSERT OR IGNORE INTO seguros_medicos (id, nombre, descuento_porcentaje, descripcion, activo)
                VALUES 
                    (1, 'ARS Senasa', 15.0, 'Seguro Nacional de Salud', 1),
                    (2, 'ARS Humano', 20.0, 'Seguro Privado ARS Humano', 1),
                    (3, 'Universal', 10.0, 'Seguro Universal', 1),
                    (4, 'Sin Seguro', 0.0, 'Sin cobertura de seguro médico', 1)
                ''')
                
                conn.commit()
                
            except Exception as e:
                print(f"Error creando tablas: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    def hash_password(self, password):
        """Hash de contraseña usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_default_users(self):
        """Crear usuarios por defecto del sistema"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                default_users = [
                    {
                        'nombre': 'Admin',
                        'apellido': 'Sistema',
                        'email': 'admin@medisync.com',
                        'telefono': '8095551234',
                        'tipo_usuario': 'admin',
                        'password': 'admin123'
                    },
                    {
                        'nombre': 'Dr. Carlos',
                        'apellido': 'Rodríguez',
                        'email': 'carlos@medisync.com',
                        'telefono': '8095555678',
                        'tipo_usuario': 'doctor',
                        'password': 'doctor123'
                    },
                    {
                        'nombre': 'María',
                        'apellido': 'López',
                        'email': 'maria@medisync.com',
                        'telefono': '8095559999',
                        'tipo_usuario': 'secretaria',
                        'password': 'secretaria123'
                    },
                    {
                        'nombre': 'Pedro',
                        'apellido': 'Ramírez',
                        'email': 'pedro@medisync.com',
                        'telefono': '8095557777',
                        'tipo_usuario': 'paciente',
                        'password': 'paciente123'
                    }
                ]
                
                for user_data in default_users:
                    # Verificar si el usuario ya existe
                    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (user_data['email'],))
                    if cursor.fetchone()[0] == 0:
                        password_hash = self.hash_password(user_data['password'])
                        cursor.execute('''
                        INSERT INTO usuarios (nombre, apellido, email, telefono, tipo_usuario, password_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            user_data['nombre'], user_data['apellido'], user_data['email'],
                            user_data['telefono'], user_data['tipo_usuario'], password_hash
                        ))
                        
                        user_id = cursor.lastrowid
                        
                        # Crear registro específico según tipo
                        if user_data['tipo_usuario'] == 'doctor':
                            cursor.execute('''
                            INSERT INTO doctores (id, especialidad, cedula_profesional)
                            VALUES (?, ?, ?)
                            ''', (user_id, 'Medicina General', f'DOC-{user_id:04d}'))
                        elif user_data['tipo_usuario'] == 'paciente':
                            cursor.execute('''
                            INSERT INTO pacientes (id, numero_expediente, seguro_medico_id, tiene_seguro)
                            VALUES (?, ?, ?, ?)
                            ''', (user_id, f'EXP-{user_id:03d}', 4, 0))
                
                conn.commit()
                
            except Exception as e:
                print(f"Error creando usuarios por defecto: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    def authenticate_user(self, email, password):
        """Autenticar usuario"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                password_hash = self.hash_password(password)
                cursor.execute('''
                SELECT id, nombre, apellido, email, telefono, tipo_usuario, activo
                FROM usuarios 
                WHERE email = ? AND password_hash = ? AND activo = 1
                ''', (email, password_hash))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        nombre=row['nombre'],
                        apellido=row['apellido'],
                        email=row['email'],
                        telefono=row['telefono'],
                        tipo_usuario=row['tipo_usuario'],
                        activo=row['activo']
                    )
                return None
                
            except Exception as e:
                print(f"Error en autenticación: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
    
    def get_all_users(self, tipo_usuario=None):
        """Obtener todos los usuarios"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                if tipo_usuario:
                    cursor.execute('''
                    SELECT id, nombre, apellido, email, telefono, tipo_usuario, activo
                    FROM usuarios
                    WHERE tipo_usuario = ? AND activo = 1
                    ORDER BY nombre, apellido
                    ''', (tipo_usuario,))
                else:
                    cursor.execute('''
                    SELECT id, nombre, apellido, email, telefono, tipo_usuario, activo
                    FROM usuarios
                    WHERE activo = 1
                    ORDER BY nombre, apellido
                    ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append(User(
                        id=row['id'],
                        nombre=row['nombre'],
                        apellido=row['apellido'],
                        email=row['email'],
                        telefono=row['telefono'],
                        tipo_usuario=row['tipo_usuario'],
                        activo=row['activo']
                    ))
                return users
                
            except Exception as e:
                print(f"Error obteniendo usuarios: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_all_patients(self):
        """Obtener todos los pacientes"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT u.id, u.nombre, u.apellido, u.email, u.telefono, u.tipo_usuario, u.activo,
                       p.numero_expediente, p.tipo_sangre, p.alergias, p.contacto_emergencia,
                       p.telefono_emergencia, p.seguro_medico, p.tiene_seguro,
                       s.nombre as seguro_nombre
                FROM usuarios u
                JOIN pacientes p ON u.id = p.id
                LEFT JOIN seguros_medicos s ON p.seguro_medico_id = s.id
                WHERE u.tipo_usuario = 'paciente' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo pacientes: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_all_doctors(self):
        """Obtener todos los doctores"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT u.id, u.nombre, u.apellido, u.email, u.telefono, u.tipo_usuario, u.activo,
                       d.especialidad, d.cedula_profesional, d.acepta_seguros, 
                       COALESCE(d.tarifa_consulta, 500.00) as tarifa_consulta,
                       d.horario_inicio, d.horario_fin
                FROM usuarios u
                JOIN doctores d ON u.id = d.id
                WHERE u.tipo_usuario = 'doctor' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo doctores: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_all_appointments(self):
        """Obtener todas las citas"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT c.*, 
                       up.nombre || ' ' || up.apellido as paciente_nombre,
                       ud.nombre || ' ' || ud.apellido as doctor_nombre,
                       COALESCE(doc.especialidad, 'N/A') as especialidad
                FROM citas c
                JOIN usuarios up ON c.paciente_id = up.id
                JOIN usuarios ud ON c.doctor_id = ud.id
                LEFT JOIN doctores doc ON ud.id = doc.id
                ORDER BY c.fecha_hora DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo citas: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_all_invoices(self):
        """Obtener todas las facturas"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT f.*, 
                       p.nombre || ' ' || p.apellido as paciente_nombre,
                       COALESCE(d.nombre || ' ' || d.apellido, 'N/A') as doctor_nombre
                FROM facturas f
                JOIN usuarios p ON f.paciente_id = p.id
                LEFT JOIN usuarios d ON f.doctor_id = d.id
                ORDER BY f.fecha_creacion DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo facturas: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_pending_invoices(self):
        """Obtener facturas pendientes"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT f.*, 
                       p.nombre || ' ' || p.apellido as paciente_nombre,
                       COALESCE(d.nombre || ' ' || d.apellido, 'N/A') as doctor_nombre
                FROM facturas f
                JOIN usuarios p ON f.paciente_id = p.id
                LEFT JOIN usuarios d ON f.doctor_id = d.id
                WHERE f.estado = 'pendiente'
                ORDER BY f.fecha_vencimiento ASC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo facturas pendientes: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def create_appointment(self, appointment_data):
        """Crear nueva cita"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Crear fecha_hora si viene por separado
                if 'fecha_cita' in appointment_data and 'hora_cita' in appointment_data:
                    fecha_hora = f"{appointment_data['fecha_cita']} {appointment_data['hora_cita']}"
                else:
                    fecha_hora = appointment_data.get('fecha_hora', '')
                
                cursor.execute('''
                INSERT INTO citas (paciente_id, doctor_id, fecha_hora, motivo, estado, notas)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    appointment_data['paciente_id'], appointment_data['doctor_id'],
                    fecha_hora, appointment_data.get('motivo', ''),
                    appointment_data.get('estado', 'pendiente'),
                    appointment_data.get('observaciones', '')
                ))
                
                conn.commit()
                return cursor.lastrowid
                
            except Exception as e:
                print(f"Error creando cita: {e}")
                conn.rollback()
                return None
            finally:
                cursor.close()
                conn.close()
    
    def get_appointment_by_id(self, appointment_id):
        """Obtener cita por ID"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT c.id, c.fecha_hora, c.motivo, c.estado, c.notas as observaciones,
                       up.nombre || ' ' || up.apellido as paciente_nombre,
                       ud.nombre || ' ' || ud.apellido as doctor_nombre,
                       c.paciente_id, c.doctor_id
                FROM citas c
                LEFT JOIN usuarios up ON c.paciente_id = up.id
                LEFT JOIN usuarios ud ON c.doctor_id = ud.id
                WHERE c.id = ?
                ''', (appointment_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'fecha_hora': row[1],
                        'motivo': row[2],
                        'estado': row[3],
                        'observaciones': row[4],
                        'paciente_nombre': row[5],
                        'doctor_nombre': row[6],
                        'paciente_id': row[7],
                        'doctor_id': row[8]
                    }
                return None
                
            except Exception as e:
                print(f"Error obteniendo cita: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
    
    def update_appointment(self, appointment_id, appointment_data):
        """Actualizar cita existente"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                UPDATE citas 
                SET paciente_id = ?, doctor_id = ?, fecha_hora = ?, 
                    motivo = ?, estado = ?, notas = ?
                WHERE id = ?
                ''', (
                    appointment_data['paciente_id'],
                    appointment_data['doctor_id'],
                    appointment_data.get('fecha_hora', ''),
                    appointment_data.get('motivo', ''),
                    appointment_data.get('estado', 'pendiente'),
                    appointment_data.get('observaciones', ''),
                    appointment_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                print(f"Error actualizando cita: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
    
    def update_appointment_status(self, appointment_id, new_status):
        """Actualizar solo el estado de la cita"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                UPDATE citas SET estado = ? WHERE id = ?
                ''', (new_status, appointment_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                print(f"Error actualizando estado de cita: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()

    def cancel_appointment_with_reason(self, appointment_id, reason):
        """Cancelar cita con motivo específico"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Actualizar estado y agregar motivo a observaciones
                cursor.execute('''
                UPDATE citas 
                SET estado = 'cancelada',
                    observaciones = CASE 
                        WHEN observaciones IS NULL OR observaciones = '' 
                        THEN 'CANCELADA: ' || ?
                        ELSE observaciones || '\n\nCANCELADA: ' || ?
                    END
                WHERE id = ?
                ''', (reason, reason, appointment_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                print(f"Error cancelando cita con motivo: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
    
    def delete_appointment(self, appointment_id):
        """Eliminar cita"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM citas WHERE id = ?', (appointment_id,))
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                print(f"Error eliminando cita: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
    
    def get_all_patients(self):
        """Obtener todos los pacientes para combobox"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT u.id, u.nombre, u.apellido 
                FROM usuarios u 
                WHERE u.tipo_usuario = 'paciente' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
                ''')
                
                patients = []
                for row in cursor.fetchall():
                    patients.append({
                        'id': row[0],
                        'nombre': row[1],
                        'apellido': row[2]
                    })
                
                return patients
                
            except Exception as e:
                print(f"Error obteniendo pacientes: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_all_doctors(self):
        """Obtener todos los doctores para combobox"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT u.id, u.nombre, u.apellido 
                FROM usuarios u 
                WHERE u.tipo_usuario = 'doctor' AND u.activo = 1
                ORDER BY u.nombre, u.apellido
                ''')
                
                doctors = []
                for row in cursor.fetchall():
                    doctors.append({
                        'id': row[0],
                        'nombre': row[1],
                        'apellido': row[2]
                    })
                
                return doctors
                
            except Exception as e:
                print(f"Error obteniendo doctores: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def create_invoice(self, invoice_data):
        """Crear nueva factura"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                INSERT INTO facturas (numero_factura, paciente_id, doctor_id, concepto,
                                    monto, estado, fecha_creacion, fecha_vencimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice_data['numero_factura'], invoice_data['paciente_id'],
                    invoice_data.get('doctor_id'), invoice_data['concepto'],
                    invoice_data['monto'], invoice_data.get('estado', 'pendiente'),
                    invoice_data['fecha_creacion'], invoice_data['fecha_vencimiento']
                ))
                
                conn.commit()
                return cursor.lastrowid
                
            except Exception as e:
                print(f"Error creando factura: {e}")
                conn.rollback()
                return None
            finally:
                cursor.close()
                conn.close()
    
    def pay_invoice(self, invoice_id, payment_data):
        """Marcar factura como pagada"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                UPDATE facturas SET estado = 'pagada', fecha_pago = ?, metodo_pago = ?
                WHERE id = ?
                ''', (payment_data['fecha_pago'], payment_data['metodo_pago'], invoice_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Error pagando factura: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT id, nombre, apellido, email, telefono, tipo_usuario, activo
                FROM usuarios 
                WHERE id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        nombre=row['nombre'],
                        apellido=row['apellido'],
                        email=row['email'],
                        telefono=row['telefono'],
                        tipo_usuario=row['tipo_usuario'],
                        activo=row['activo']
                    )
                return None
                
            except Exception as e:
                print(f"Error obteniendo usuario: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
    
    def get_medical_insurances(self):
        """Obtener seguros médicos"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT * FROM seguros_medicos WHERE activo = 1
                ORDER BY nombre
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception as e:
                print(f"Error obteniendo seguros: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    
    def get_monthly_income(self, year, month):
        """Obtener ingresos mensuales"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT SUM(monto) as total_ingresos, COUNT(*) as total_facturas
                FROM facturas
                WHERE estado = 'pagada' 
                AND strftime('%Y', fecha_pago) = ? 
                AND strftime('%m', fecha_pago) = ?
                ''', (str(year), f"{month:02d}"))
                
                result = cursor.fetchone()
                return {
                    'total_ingresos': result['total_ingresos'] or 0,
                    'total_facturas': result['total_facturas'] or 0
                }
                
            except Exception as e:
                print(f"Error obteniendo ingresos: {e}")
                return {'total_ingresos': 0, 'total_facturas': 0}
            finally:
                cursor.close()
                conn.close()

# Función auxiliar para obtener doctores disponibles (compatible con versión anterior)
def get_available_doctors_global(db_manager):
    """Función para compatibilidad con código anterior"""
    try:
        doctors = db_manager.get_all_doctors()
        return [
            {
                'id': doc['id'],
                'nombre_completo': f"{doc['nombre']} {doc['apellido']}",
                'especialidad': doc.get('especialidad', 'N/A')
            }
            for doc in doctors
        ]
    except Exception as e:
        print(f"Error obteniendo doctores disponibles: {e}")
        return []
