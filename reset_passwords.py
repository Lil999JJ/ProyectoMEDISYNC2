#!/usr/bin/env python3
"""
Script para verificar y resetear contraseñas de usuarios por defecto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_database_manager import SimpleDatabaseManager

def reset_default_passwords():
    """Resetear contraseñas de usuarios por defecto"""
    
    print("🔒 RESETEANDO CONTRASEÑAS DE USUARIOS POR DEFECTO")
    print("=" * 60)
    
    # Inicializar database manager
    db_manager = SimpleDatabaseManager('database/medisync.db')
    
    # Usuarios por defecto con nuevas contraseñas
    default_passwords = {
        "admin@medisync.com": "admin123",
        "carlos@medisync.com": "doctor123", 
        "maria@medisync.com": "secretaria123",
        "pedro@medisync.com": "paciente123"
    }
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Actualizando contraseñas:")
        
        for email, password in default_passwords.items():
            # Verificar si el usuario existe
            cursor.execute("SELECT id, nombre, apellido FROM usuarios WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user:
                # Actualizar contraseña
                password_hash = db_manager.hash_password(password)
                cursor.execute(
                    "UPDATE usuarios SET password_hash = ? WHERE email = ?", 
                    (password_hash, email)
                )
                print(f"   ✅ {user['nombre']} {user['apellido']} ({email}) -> {password}")
            else:
                print(f"   ❌ Usuario no encontrado: {email}")
        
        conn.commit()
        print("\n✅ Contraseñas actualizadas correctamente!")
        
        # Probar las credenciales actualizadas
        print("\n" + "=" * 60)
        print("🧪 PROBANDO CREDENCIALES ACTUALIZADAS:")
        
        for email, password in default_passwords.items():
            user = db_manager.authenticate_user(email, password)
            if user:
                print(f"   ✅ {email} / {password} -> {user.nombre} {user.apellido}")
            else:
                print(f"   ❌ {email} / {password} -> FALLO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 60)
    print("🚀 Ahora puede usar estas credenciales en MEDISYNC:")
    print("   🛡️  Admin: admin@medisync.com / admin123")
    print("   👨‍⚕️  Doctor: carlos@medisync.com / doctor123") 
    print("   👩‍💼  Secretaria: maria@medisync.com / secretaria123")
    print("   🤒  Paciente: pedro@medisync.com / paciente123")

if __name__ == "__main__":
    reset_default_passwords()
