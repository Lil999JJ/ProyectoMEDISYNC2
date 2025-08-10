import sqlite3
from datetime import datetime

def setup_missing_tables():
    """Configurar tablas faltantes para el sistema"""
    try:
        conn = sqlite3.connect('database/medisync.db')
        cursor = conn.cursor()
        
        # Verificar y crear tabla doctores si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctores (
                id INTEGER PRIMARY KEY,
                especialidad VARCHAR(100),
                FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        # Verificar y crear tabla pacientes si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY,
                numero_expediente VARCHAR(20) UNIQUE,
                seguro_medico VARCHAR(100),
                contacto_emergencia VARCHAR(100),
                telefono_emergencia VARCHAR(20),
                FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        # Verificar y crear tabla seguros si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seguros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                activo BOOLEAN DEFAULT 1
            )
        """)
        
        # Insertar algunos seguros médicos por defecto
        cursor.execute("SELECT COUNT(*) FROM seguros")
        if cursor.fetchone()[0] == 0:
            seguros_default = [
                ("Seguro Nacional", "Seguro público de salud"),
                ("ARS Universal", "Administradora de Riesgos de Salud Universal"),
                ("ARS Humano", "Administradora de Riesgos de Salud Humano"),
                ("ARS Primera", "Administradora de Riesgos de Salud Primera"),
                ("Seguro Privado", "Seguro médico privado"),
                ("Sin Seguro", "Paciente sin cobertura médica")
            ]
            
            cursor.executemany("""
                INSERT INTO seguros (nombre, descripcion)
                VALUES (?, ?)
            """, seguros_default)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Todas las tablas están configuradas correctamente")
        
    except Exception as e:
        print(f"❌ Error configurando tablas: {e}")

if __name__ == "__main__":
    setup_missing_tables()
