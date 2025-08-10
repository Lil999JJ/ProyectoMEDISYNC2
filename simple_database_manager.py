"""
Simple Database Manager para MEDISYNC
Versión simplificada sin bloqueos
"""
import sqlite3
import hashlib
import os
from dataclasses import dataclass
from typing import Optional, List

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

class SimpleDatabaseManager:
    """Gestor de base de datos simplificado para MEDISYNC"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Asegurar que la base de datos existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_simple_connection(self):
        """Obtener conexión simple"""
        return self.get_connection()
    
    def create_tables(self):
        """Crear tablas necesarias"""
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
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Tabla citas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                fecha_cita DATE NOT NULL,
                hora_cita TIME NOT NULL,
                fecha_hora DATETIME,
                motivo TEXT,
                estado TEXT DEFAULT 'programada',
                notas TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            
            # Insertar seguros por defecto
            cursor.execute('''
            INSERT OR IGNORE INTO seguros_medicos (id, nombre, descuento_porcentaje, descripcion, activo)
            VALUES 
                (1, 'ARS Senasa', 15.0, 'Seguro Nacional de Salud', 1),
                (2, 'ARS Humano', 20.0, 'Seguro Privado ARS Humano', 1),
                (3, 'Universal', 10.0, 'Seguro Universal', 1),
                (4, 'Sin Seguro', 0.0, 'Sin cobertura de seguro médico', 1)
            ''')
            
            # Crear usuarios por defecto si no existen
            self.create_default_users(cursor)
            
            conn.commit()
            
        except Exception as e:
            print(f"Error creando tablas: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def create_default_users(self, cursor):
        """Crear usuarios por defecto"""
        default_users = [
            {
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'email': 'admin@medisync.com',
                'telefono': '8095551234',
                'tipo_usuario': 'admin',
                'password': 'admin123'
            },
            {
                'nombre': 'Dr. Carlos',
                'apellido': 'Médico',
                'email': 'carlos@medisync.com',
                'telefono': '8095555678',
                'tipo_usuario': 'doctor',
                'password': 'doctor123'
            },
            {
                'nombre': 'María',
                'apellido': 'Secretaria',
                'email': 'maria@medisync.com',
                'telefono': '8095559999',
                'tipo_usuario': 'secretaria',
                'password': 'secretaria123'
            },
            {
                'nombre': 'Pedro',
                'apellido': 'Sánchez',
                'email': 'pedro@medisync.com',
                'telefono': '8095557777',
                'tipo_usuario': 'paciente',
                'password': 'paciente123'
            }
        ]
        
        for user_data in default_users:
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
    
    def hash_password(self, password):
        """Hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, email, password):
        """Autenticar usuario"""
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
    
    def get_patient_medical_history(self, patient_id):
        """Obtener historial médico del paciente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT h.*, 
                   d.nombre || ' ' || d.apellido as doctor_nombre,
                   doc.especialidad
            FROM historiales_medicos h
            JOIN usuarios d ON h.doctor_id = d.id
            JOIN doctores doc ON d.id = doc.id
            WHERE h.paciente_id = ?
            ORDER BY h.fecha_consulta DESC
            ''', (patient_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_all_users(self):
        """Obtener todos los usuarios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, tipo_usuario, activo
            FROM usuarios
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
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT u.id, u.nombre, u.apellido, u.email, u.telefono, u.tipo_usuario, u.activo,
                   d.especialidad, d.cedula_profesional, d.acepta_seguros, d.tarifa_consulta,
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
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT c.*, 
                   p.nombre || ' ' || p.apellido as paciente_nombre,
                   d.nombre || ' ' || d.apellido as doctor_nombre,
                   COALESCE(doc.especialidad, 'N/A') as especialidad
            FROM citas c
            JOIN usuarios p ON c.paciente_id = p.id
            JOIN usuarios d ON c.doctor_id = d.id
            LEFT JOIN doctores doc ON d.id = doc.id
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
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
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
    
    def create_user(self, user_data):
        """Crear nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(user_data['password'])
            cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, telefono, direccion, 
                                fecha_nacimiento, tipo_usuario, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['nombre'], user_data['apellido'], user_data['email'],
                user_data['telefono'], user_data.get('direccion', ''),
                user_data.get('fecha_nacimiento', ''), user_data['tipo_usuario'],
                password_hash
            ))
            
            user_id = cursor.lastrowid
            
            # Crear registro específico según tipo
            if user_data['tipo_usuario'] == 'doctor':
                cursor.execute('''
                INSERT INTO doctores (id, especialidad, cedula_profesional, acepta_seguros, tarifa_consulta)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id, 
                    user_data.get('especialidad', 'Medicina General'),
                    user_data.get('cedula_profesional', f'DOC-{user_id:04d}'),
                    user_data.get('acepta_seguros', 1),
                    user_data.get('tarifa_consulta', 500.00)
                ))
            elif user_data['tipo_usuario'] == 'paciente':
                cursor.execute('''
                INSERT INTO pacientes (id, numero_expediente, tipo_sangre, alergias,
                                     contacto_emergencia, telefono_emergencia, 
                                     seguro_medico_id, tiene_seguro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    user_data.get('numero_expediente', f'EXP-{user_id:03d}'),
                    user_data.get('tipo_sangre', ''),
                    user_data.get('alergias', ''),
                    user_data.get('contacto_emergencia', ''),
                    user_data.get('telefono_emergencia', ''),
                    user_data.get('seguro_medico_id', 4),
                    user_data.get('tiene_seguro', 0)
                ))
            
            conn.commit()
            return user_id
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_user(self, user_id, user_data):
        """Actualizar usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE usuarios SET nombre = ?, apellido = ?, email = ?, telefono = ?,
                              direccion = ?, fecha_nacimiento = ?
            WHERE id = ?
            ''', (
                user_data['nombre'], user_data['apellido'], user_data['email'],
                user_data['telefono'], user_data.get('direccion', ''),
                user_data.get('fecha_nacimiento', ''), user_id
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def delete_user(self, user_id):
        """Eliminar usuario (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE usuarios SET activo = 0 WHERE id = ?', (user_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def create_appointment(self, appointment_data):
        """Crear nueva cita"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Crear fecha_hora combinando fecha y hora si vienen por separado
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
                appointment_data.get('estado', 'programada'),
                appointment_data.get('notas', '')
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
    
    def create_invoice(self, invoice_data):
        """Crear nueva factura"""
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
    
    def get_medical_insurances(self):
        """Obtener seguros médicos"""
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
